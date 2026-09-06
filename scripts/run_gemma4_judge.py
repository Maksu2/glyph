#!/usr/bin/env python3
"""Ask Gemma 4 to judge Glyph-27M samples and write JSONL + summary reports."""
import argparse
import json
import math
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SCORE_KEYS = ("continuation_fit", "polish", "coherence", "repetition", "safety", "overall")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def atomic_write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(path)


def read_json(path: Path) -> dict:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def completion(base_url: str, prompt: str, timeout: int, n_predict: int) -> str:
    url = base_url.rstrip("/") + "/completion"
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": 0.1,
        "top_k": 20,
        "top_p": 0.9,
        "stream": False,
        "cache_prompt": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemma request failed: {exc}") from exc
    return data.get("content", "")


def extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            parsed, _ = decoder.raw_decode(text[match.start():])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("No JSON object found in judge output")
    return json.loads(match.group(0))


def clamp_score(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return max(1.0, min(5.0, number))


def compact_training_stats(stats: dict) -> str:
    if not stats:
        return "brak metryk treningu"

    last_eval = stats.get("last_eval") or {}
    parts = [
        f"step={stats.get('step', 'brak')}/{stats.get('total_steps', 'brak')}",
        f"progress={stats.get('progress_pct', 'brak')}%",
        f"train_loss={stats.get('loss', 'brak')}",
        f"val_loss={last_eval.get('val_loss', 'brak')}",
        f"learning_rate={stats.get('lr', 'brak')}",
        f"tok_s={stats.get('toks_per_sec', 'brak')}",
        f"tokens_m={stats.get('tokens_m', 'brak')}",
    ]
    return ", ".join(parts)


def judge_prompt(sample: dict, training_stats: dict) -> str:
    response = sample.get("response", "")
    if len(response) > 3500:
        response = response[:3500] + "\n[ucięto długą odpowiedź]"
    mode = sample.get("mode", "base")
    expected = sample.get("expected_behavior") or "naturalna kontynuacja tekstu"
    return f"""Jesteś surowym, ale sprawiedliwym ewaluatorem Glyph-27M, małego polskiego modelu językowego.
Oceniasz model po pretrainingu językowym, przed instruction tuningiem/SFT.
To znaczy: model NIE musi jeszcze zachowywać się jak asystent, wykonywać poleceń, formatować checklist ani odpowiadać użytkownikowi w trybie chatbota.
Najważniejsze jest, czy potrafi naturalnie kontynuować polski tekst, utrzymać lokalny kontekst, pisać poprawną polszczyzną i unikać powtarzalnego bełkotu.

Tryb promptu: {mode}
Oczekiwane zachowanie dla tego promptu: {expected}

Metryki treningu są kontekstem, nie bezpośrednią podstawą oceny pojedynczej próbki.
Uwzględnij je tylko przy interpretacji dojrzałości modelu:
{compact_training_stats(training_stats)}

Skala 1-5:
1 = bardzo słabo, 2 = słabo, 3 = częściowo akceptowalnie, 4 = dobrze, 5 = bardzo dobrze.

Kryteria:
- continuation_fit: czy tekst pasuje jako dalszy ciąg promptu; przy modelu bazowym nie karz za brak odpowiedzi instrukcyjnej, jeśli prompt jest fragmentem tekstu.
- polish: gramatyka, fleksja, interpunkcja, naturalność polszczyzny.
- coherence: spójność sensu w obrębie kilku zdań, brak nagłych zmian tematu, brak sprzeczności.
- repetition: 5 oznacza mało powtórzeń i brak pętli; 1 oznacza silne zapętlenie, spam lub powtarzanie fraz.
- safety: 5 oznacza brak niebezpiecznych treści; obniż tylko przy realnym problemie bezpieczeństwa.
- overall: całościowa ocena tej próbki jako kontynuacji tekstu przez mały model bazowy.

Nie oczekuj faktograficznej doskonałości. Jeśli tekst jest ogólnie płynny, ale płytki, zwykle jest to 3-4.
Jeśli tekst jest gramatyczny, lecz nie pasuje do promptu, obniż continuation_fit i overall.
Jeśli tekst zaczyna powtarzać te same konstrukcje lub traci sens, obniż repetition, coherence i overall.

Zwróć wyłącznie jeden obiekt JSON, bez Markdown i bez dodatkowego komentarza.

Wymagany format:
{{"continuation_fit": 1-5, "polish": 1-5, "coherence": 1-5, "repetition": 1-5, "safety": 1-5, "overall": 1-5, "notes": "2-4 zdania po polsku: co działa, co nie działa, jak interpretować wynik przy obecnym etapie treningu"}}

PROMPT:
{sample.get("prompt", "")}

ODPOWIEDŹ MODELU:
{response}
"""


def judge_retry_prompt(sample: dict, training_stats: dict, previous_output: str, error: str) -> str:
    response = sample.get("response", "")
    if len(response) > 2500:
        response = response[:2500] + "\n[ucięto długą odpowiedź]"
    previous_output = previous_output[-1800:] if previous_output else "brak poprzedniej odpowiedzi"
    return f"""Poprzednia odpowiedź sędziego nie była poprawnym JSON-em.
Błąd parsera: {error}

Oceń tę samą próbkę ponownie. Zwróć WYŁĄCZNIE jeden minifikowany obiekt JSON.
Nie używaj Markdown. Nie używaj komentarza poza JSON. W polu notes nie używaj cudzysłowów wewnątrz tekstu.

Wymagany format:
{{"continuation_fit":3,"polish":3,"coherence":3,"repetition":3,"safety":5,"overall":3,"notes":"krótka notatka po polsku bez cudzysłowów"}}

Kontekst treningu:
{compact_training_stats(training_stats)}

Tryb promptu: {sample.get("mode", "base")}
Oczekiwane zachowanie: {sample.get("expected_behavior") or "naturalna kontynuacja tekstu"}

PROMPT:
{sample.get("prompt", "")}

ODPOWIEDŹ MODELU:
{response}

POPRZEDNIA NIEPOPRAWNA ODPOWIEDŹ SĘDZIEGO:
{previous_output}
"""


def parse_judgement(raw: str) -> tuple[dict, bool, str, str | None]:
    parsed = extract_json(raw)
    scores = {key: clamp_score(parsed.get(key)) for key in SCORE_KEYS}
    valid = all(scores[key] is not None for key in SCORE_KEYS)
    notes = str(parsed.get("notes", "")).strip()
    error = None if valid else "missing-or-invalid-score"
    return scores, valid, notes, error


def descriptive_summary_prompt(summary: dict, rows: list[dict], training_stats: dict) -> str:
    examples = []
    for row in rows[:8]:
        examples.append({
            "prompt_id": row.get("prompt_id"),
            "scores": row.get("scores"),
            "notes": row.get("notes"),
        })
    return f"""Jesteś ewaluatorem postępów małego polskiego modelu językowego.
Napisz krótką, techniczną diagnozę całego runu benchmarkowego.
Zero motywacyjnego tonu, zero ogólników typu "warto obserwować dalej", zero prognoz bez danych.

Kontekst:
- model jest po pretrainingu, przed SFT/instruction tuningiem;
- benchmark domyślnie sprawdza kontynuację polskiego tekstu, nie jakość asystenta;
- metryki treningu są pomocnicze.

Metryki treningu:
{compact_training_stats(training_stats)}

Średnie oceny:
{json.dumps(summary.get("averages", {}), ensure_ascii=False)}

Przykładowe komentarze z ocen:
{json.dumps(examples, ensure_ascii=False)}

Zwróć wyłącznie JSON:
{{"description": "3-4 krótkie zdania po polsku. Podaj wynik overall, najsłabsze metryki, relację do train_loss/val_loss/lr oraz jeden konkretny typ błędu widoczny w próbkach."}}
"""


def summarize(rows: list[dict], model_label: str, samples_path: Path, report_path: Path, training_stats: dict) -> dict:
    valid = [r for r in rows if r.get("valid")]
    averages = {}
    for key in SCORE_KEYS:
        values = [r.get("scores", {}).get(key) for r in valid]
        values = [v for v in values if isinstance(v, (int, float))]
        averages[key] = round(sum(values) / len(values), 3) if values else None
    return {
        "status": "ok" if valid else "no-valid-judgements",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model_label,
        "samples": str(samples_path),
        "report": str(report_path),
        "count": len(rows),
        "valid_count": len(valid),
        "overall_avg": averages.get("overall"),
        "averages": averages,
        "description": "",
        "training_stats": {
            "step": training_stats.get("step"),
            "total_steps": training_stats.get("total_steps"),
            "progress_pct": training_stats.get("progress_pct"),
            "loss": training_stats.get("loss"),
            "lr": training_stats.get("lr"),
            "last_eval": training_stats.get("last_eval"),
            "tokens_m": training_stats.get("tokens_m"),
        },
    }


def fallback_description(summary: dict, rows: list[dict]) -> str:
    valid = [r for r in rows if r.get("valid")]
    averages = summary.get("averages", {})
    overall = summary.get("overall_avg")
    stats = summary.get("training_stats", {})
    last_eval = stats.get("last_eval") or {}
    metric_order = ("continuation_fit", "polish", "coherence", "repetition")
    scored = [
        (key, averages.get(key))
        for key in metric_order
        if isinstance(averages.get(key), (int, float))
    ]
    weakest = sorted(scored, key=lambda item: item[1])[:2]
    strongest = sorted(scored, key=lambda item: item[1], reverse=True)[:1]
    weakest_text = ", ".join(f"{key}={value:.2f}" for key, value in weakest) or "brak danych"
    strongest_text = ", ".join(f"{key}={value:.2f}" for key, value in strongest) or "brak danych"

    loop_hits = []
    for row in valid:
        response = (row.get("mini_response") or "").lower()
        if any(phrase in response for phrase in ("nie jest żadne", "nie ma w tym", "no ale")):
            loop_hits.append(row.get("prompt_id") or "?")
    loop_text = ""
    if loop_hits:
        loop_text = f" Podejrzane powtórzenia widać m.in. w próbkach: {', '.join(loop_hits[:4])}."
    return (
        "Benchmark kontynuacji tekstu bazowego modelu, nie chatu po SFT. "
        f"Wynik: overall={overall}/5 na {summary.get('valid_count')}/{summary.get('count')} próbkach. "
        f"Trening: step={stats.get('step')}, train_loss={stats.get('loss')}, "
        f"val_loss={last_eval.get('val_loss')}, lr={stats.get('lr')}. "
        f"Najsłabsze średnie: {weakest_text}; najmocniejsza metryka: {strongest_text}."
        f"{loop_text}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge Glyph-27M samples with Gemma 4 via llama.cpp")
    parser.add_argument("--samples", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary-out", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8182")
    parser.add_argument("--model-label", default="Gemma 4 E4B")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--n-predict", type=int, default=220)
    parser.add_argument("--training-stats", default=None)
    parser.add_argument("--summary-predict", type=int, default=420)
    parser.add_argument("--retries", type=int, default=1)
    args = parser.parse_args()

    samples_path = Path(args.samples)
    report_path = Path(args.out)
    training_stats = read_json(Path(args.training_stats)) if args.training_stats else {}
    rows = read_jsonl(samples_path)
    if args.limit > 0:
        rows = rows[: args.limit]

    judged = []
    for sample in rows:
        raw = ""
        attempts = 0
        try:
            attempts = 1
            raw = completion(args.base_url, judge_prompt(sample, training_stats), args.timeout, args.n_predict)
            scores, valid, notes, error = parse_judgement(raw)
            if not valid:
                raise ValueError(error or "invalid judgement")
        except Exception as exc:
            last_error = str(exc)
            for _ in range(max(0, args.retries)):
                try:
                    attempts += 1
                    raw = completion(
                        args.base_url,
                        judge_retry_prompt(sample, training_stats, raw, last_error),
                        args.timeout,
                        args.n_predict,
                    )
                    scores, valid, notes, error = parse_judgement(raw)
                    if valid:
                        break
                    last_error = error or "invalid judgement"
                except Exception as retry_exc:
                    last_error = str(retry_exc)
            else:
                scores = {key: None for key in SCORE_KEYS}
                valid = False
                notes = ""
                error = last_error

        judged.append({
            "judged_at": datetime.now(timezone.utc).isoformat(),
            "model": args.model_label,
            "prompt_id": sample.get("prompt_id"),
            "mode": sample.get("mode"),
            "category": sample.get("category"),
            "expected_behavior": sample.get("expected_behavior"),
            "checkpoint": sample.get("checkpoint"),
            "checkpoint_step": sample.get("checkpoint_step"),
            "prompt": sample.get("prompt"),
            "mini_response": sample.get("response"),
            "scores": scores,
            "notes": notes,
            "valid": valid,
            "error": error,
            "attempts": attempts,
            "raw_judge_output": raw,
        })

    atomic_write_jsonl(report_path, judged)
    summary = summarize(judged, args.model_label, samples_path, report_path, training_stats)
    if summary["valid_count"]:
        raw_summary = ""
        try:
            raw_summary = completion(
                args.base_url,
                descriptive_summary_prompt(summary, judged, training_stats),
                args.timeout,
                args.summary_predict,
            )
            parsed_summary = extract_json(raw_summary)
            summary["gemma_description"] = str(parsed_summary.get("description", "")).strip()
            summary["raw_description_output"] = raw_summary
        except Exception as exc:
            fallback = raw_summary.strip()
            if fallback:
                summary["gemma_description"] = fallback
                summary["raw_description_output"] = raw_summary
                summary["description_parse_warning"] = str(exc)
            else:
                summary["description_parse_warning"] = str(exc)
        summary["description"] = fallback_description(summary, judged)
    atomic_write_json(Path(args.summary_out), summary)
    print(f"Wrote {len(judged)} Gemma judgements to {report_path}")
    print(f"overall_avg={summary.get('overall_avg')}")
    return 0 if summary["valid_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
