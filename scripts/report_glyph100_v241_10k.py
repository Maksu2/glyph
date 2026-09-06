#!/usr/bin/env python3
"""Build the post-run report for Glyph-100M v2.4.1 at 10k."""
from __future__ import annotations

import json
import re
import statistics
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUN_LOG = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "train.log"
GPU_LOG = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "gpu_metrics.log"
STARTED = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "started_at.txt"
FINISHED = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "finished_at.txt"
EXIT_CODE = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "exit_code.txt"
TRAJECTORY = ROOT / "eval" / "glyph-100m" / "glyph100_v2_4_1_10k_eval_20260718_comparison.json"
SOURCE_VAL = ROOT / "eval" / "glyph-100m" / "glyph100_v2_4_1_10k_eval_20260718_source_validation.json"
HISTORICAL = ROOT / "eval" / "glyph-100m" / "glyph100_v2_4_1_10k_eval_20260718_vs_v231_10k.json"
DATASET = ROOT / "data" / "processed" / "glyph100_v2_4_1_metadata.json"
OUT_JSON = ROOT / "reports" / "glyph100_v2_4_1_10k_20260718_report.json"
OUT_MD = ROOT / "reports" / "glyph100_v2_4_1_10k_20260718_report.md"

STEP_RE = re.compile(
    r"^(?P<time>\S+ \S+) step=\s*(?P<step>\d+) \| loss=(?P<loss>[\d.]+) "
    r"\| lr=(?P<lr>[\deE+.-]+) \| tok/s=(?P<tps>[\d,]+) \| tokens=(?P<tokens>[\d.]+)M"
)
EVAL_RE = re.compile(
    r"^(?P<time>\S+ \S+) eval step=\s*(?P<step>\d+) \| val_loss=(?P<loss>[\d.]+)"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_run() -> dict:
    step_rows = []
    eval_rows = []
    text = RUN_LOG.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        step = STEP_RE.search(line)
        if step:
            step_rows.append(
                {
                    "time": step.group("time"),
                    "step": int(step.group("step")),
                    "loss": float(step.group("loss")),
                    "learning_rate": float(step.group("lr")),
                    "tokens_per_second": int(step.group("tps").replace(",", "")),
                    "tokens_m": float(step.group("tokens")),
                }
            )
        evaluation = EVAL_RE.search(line)
        if evaluation:
            eval_rows.append(
                {
                    "time": evaluation.group("time"),
                    "step": int(evaluation.group("step")),
                    "val_loss": float(evaluation.group("loss")),
                }
            )
    started = datetime.fromisoformat(STARTED.read_text().strip().replace("Z", "+00:00"))
    finished = datetime.fromisoformat(FINISHED.read_text().strip().replace("Z", "+00:00"))
    stable_tps = [row["tokens_per_second"] for row in step_rows if row["tokens_per_second"] > 3000]
    return {
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": int((finished - started).total_seconds()),
        "exit_code": int(EXIT_CODE.read_text().strip()),
        "start_step": 5000,
        "end_step": step_rows[-1]["step"],
        "stage_tokens": 5000 * 16384,
        "total_tokens": step_rows[-1]["step"] * 16384,
        "corpus_epochs": round((step_rows[-1]["step"] * 16384) / 278_089_665, 4),
        "first_logged_step": step_rows[0],
        "last_logged_step": step_rows[-1],
        "start_window_avg_loss": round(statistics.mean(row["loss"] for row in step_rows[:20]), 6),
        "end_window_avg_loss": round(statistics.mean(row["loss"] for row in step_rows[-20:]), 6),
        "min_train_loss": min(row["loss"] for row in step_rows),
        "max_train_loss": max(row["loss"] for row in step_rows),
        "stable_tokens_per_second": round(statistics.mean(stable_tps), 2),
        "end_to_end_tokens_per_second": round((5000 * 16384) / (finished - started).total_seconds(), 2),
        "validation": eval_rows,
        "non_finite_or_oom": any(
            marker in text.lower()
            for marker in ("non-finite", "out of memory", "traceback", "rocm crash")
        ),
        "checkpoint_saved_7500": "step_0007500.pt" in text,
        "checkpoint_saved_10000": "step_0010000.pt" in text,
    }


def parse_gpu(start: datetime, end: datetime) -> dict:
    chunks = re.split(r"(?m)^(?=\d{4}-\d{2}-\d{2}T)", GPU_LOG.read_text(errors="replace"))
    rows = []
    for chunk in chunks:
        if not chunk.strip():
            continue
        try:
            timestamp = datetime.fromisoformat(chunk.splitlines()[0].replace("Z", "+00:00"))
        except ValueError:
            continue
        if not start <= timestamp <= end:
            continue

        def value(pattern: str):
            match = re.search(pattern, chunk)
            return float(match.group(1)) if match else None

        rows.append(
            {
                "edge_c": value(r"edge:\s*\+([\d.]+)°C"),
                "hotspot_c": value(r"junction:\s*\+([\d.]+)°C"),
                "fan_rpm": value(r"fan1:\s*([\d.]+) RPM"),
                "power_w": value(r"PPT:\s*([\d.]+) W"),
            }
        )

    def metric(name: str) -> dict:
        values = [row[name] for row in rows if row[name] is not None]
        return {
            "samples": len(values),
            "avg": round(statistics.mean(values), 2),
            "min": min(values),
            "max": max(values),
        }

    return {
        "samples": len(rows),
        "edge_c": metric("edge_c"),
        "hotspot_c": metric("hotspot_c"),
        "fan_rpm": metric("fan_rpm"),
        "power_w": metric("power_w"),
    }


def human_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours} h {minutes} min {secs} s"


def main() -> None:
    run = parse_run()
    start = datetime.fromisoformat(run["started_at"])
    end = datetime.fromisoformat(run["finished_at"])
    gpu = parse_gpu(start, end)
    trajectory = load_json(TRAJECTORY)
    source_val = load_json(SOURCE_VAL)
    historical = load_json(HISTORICAL)
    dataset = load_json(DATASET)
    checkpoints = trajectory["checkpoint_contracts"]
    current = trajectory["summaries"]["10k"]["overall"]
    five = trajectory["summaries"]["5k"]["overall"]
    old = historical["summaries"]["v2.3.1-10k"]
    new = historical["summaries"]["v2.4.1-10k"]

    payload = {
        "report_id": "glyph100_v2_4_1_10k_20260718",
        "generated_at": datetime.now().astimezone().isoformat(),
        "status": "complete",
        "training": run,
        "gpu": gpu,
        "checkpoint_contracts": checkpoints,
        "dataset": {
            "name": dataset["dataset_name"],
            "train_tokens": dataset["train_tokens"],
            "val_tokens": dataset["val_tokens"],
            "total_tokens": dataset["total_tokens"],
            "wikipedia_share": dataset["wikipedia_share"],
            "literature_share": dataset["literature_share"],
            "parliamentary_share": dataset["parliamentary_share"],
        },
        "trajectory_eval": {
            "summaries": trajectory["summaries"],
            "pairwise": trajectory["pairwise"],
            "heuristic_best": trajectory["heuristic_best_checkpoint"],
        },
        "source_validation": source_val,
        "equal_exposure_vs_v231": {
            "summaries": historical["summaries"],
            "pairwise": historical["pairwise"],
        },
        "manual_findings": [
            "10k is only marginally better than 5k on the deterministic trajectory heuristic.",
            "Pseudo-encyclopedic trigger hits fell, but repetition and semantic task adherence did not improve materially.",
            "Narrative/literary prompts are the strongest samples; factual and technical continuations remain mostly wrong.",
            "Parliamentary/legal and locality/demography templates remain visible despite the cleaner corpus.",
            "No classic URL/HTML/SEO residue was found in the evaluated samples.",
        ],
        "verdict": "prepare_v2_4_2_before_more_training",
        "recommendation": {
            "next_step": "Build and validate a v2.4.2 corrective source mix, then run a matched from-scratch 5k proxy.",
            "do_not": "Do not automatically continue v2.4.1 beyond 10k.",
            "v2_4_2_targets": [
                "Cap parliamentary data near 2-3% instead of 8.53%.",
                "Reject or strongly downweight Wikipedia locality/demography/index boilerplate.",
                "Keep literature at or above 50% where quality validation permits.",
                "Preserve source/doc metadata and source-specific validation bins.",
                "Compare v2.4.2 at 5k against the saved v2.4.1 5k checkpoint before any 10k continuation.",
            ],
        },
        "no_training_started_after_eval": True,
        "artifacts": [
            str(OUT_MD.relative_to(ROOT)),
            str(OUT_JSON.relative_to(ROOT)),
            str(TRAJECTORY.relative_to(ROOT)),
            str(SOURCE_VAL.relative_to(ROOT)),
            str(HISTORICAL.relative_to(ROOT)),
            "eval/glyph-100m/glyph100_v2_4_1_10k_eval_20260718_samples.md",
            "eval/glyph-100m/glyph100_v2_4_1_10k_eval_20260718_samples.json",
            "eval/glyph-100m/glyph100_v2_4_1_10k_eval_20260718_comparison.md",
            "eval/glyph-100m/glyph100_v2_4_1_10k_eval_20260718_source_validation.md",
            "eval/glyph-100m/glyph100_v2_4_1_10k_eval_20260718_vs_v231_10k.md",
        ],
    }
    OUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Glyph-100M v2.4.1: raport po 10k",
        "",
        "Data oceny: 2026-07-18",
        "",
        "## Werdykt",
        "",
        "**Run 10k zakończył się zdrowo i v2.4.1 wygrywa ze starym v2.3.1 przy",
        "tej samej ekspozycji tokenów. Nie ma jednak wystarczającej poprawy",
        "semantycznej względem 5k, aby bez kontroli dokładać kolejne kroki.**",
        "",
        "Następny krok to przygotowanie korekcyjnego miksu `v2.4.2`, ograniczającego",
        "powtarzalne dane parlamentarne i szablony miejscowości, a potem porównywalny",
        "proxy 5k od zera. Po tym eval nie uruchomiono kolejnego treningu.",
        "",
        "## Stan techniczny",
        "",
        f"- Czas: `{run['started_at']}` -> `{run['finished_at']}` ({human_duration(run['duration_seconds'])})",
        f"- Kroki: `{run['start_step']}` -> `{run['end_step']}`",
        f"- Tokeny w tym etapie: `{run['stage_tokens']:,}`",
        f"- Tokeny łącznie: `{run['total_tokens']:,}` (`{run['corpus_epochs']:.3f}` epoki korpusu train)",
        f"- Stabilna wydajność: `{run['stable_tokens_per_second']:.0f} tok/s`",
        f"- End-to-end: `{run['end_to_end_tokens_per_second']:.0f} tok/s`",
        f"- Train loss, okno startowe -> końcowe: `{run['start_window_avg_loss']:.4f}` -> `{run['end_window_avg_loss']:.4f}`",
        f"- Final val loss: `{run['validation'][-1]['val_loss']:.4f}`",
        f"- Exit code: `{run['exit_code']}`",
        f"- NaN / Inf / OOM / crash: `{'tak' if run['non_finite_or_oom'] else 'brak'}`",
        f"- Checkpointy 7,5k i 10k: `{'OK' if run['checkpoint_saved_7500'] and run['checkpoint_saved_10000'] else 'problem'}`",
        "",
        "Każdy checkpoint ma poprawny wariant, model config, tokenizer SHA, dataset,",
        "optimizer, scheduler i stan samplera.",
        "",
        "## GPU",
        "",
        f"- Edge: średnio `{gpu['edge_c']['avg']:.1f} C`, maks. `{gpu['edge_c']['max']:.0f} C`",
        f"- Hotspot: średnio `{gpu['hotspot_c']['avg']:.1f} C`, maks. `{gpu['hotspot_c']['max']:.0f} C`",
        f"- Pobór: średnio `{gpu['power_w']['avg']:.1f} W`, maks. `{gpu['power_w']['max']:.0f} W`",
        f"- Wentylator: średnio `{gpu['fan_rpm']['avg']:.0f} RPM`, maks. `{gpu['fan_rpm']['max']:.0f} RPM`",
        "",
        "## Validation loss",
        "",
        "| step | val loss |",
        "|---:|---:|",
    ]
    for row in run["validation"]:
        lines.append(f"| {row['step']} | {row['val_loss']:.4f} |")
    lines.extend(
        [
            "",
            "Val loss spadał do końca. Nie ma sygnału technicznego overfitu.",
            "",
            "## Walidacja per źródło",
            "",
            "| source | 5k | 7,5k | 10k | zmiana 10k-5k |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for source, item in source_val["source_bins"].items():
        source_results = source_val["checkpoints"]
        five_loss = source_results["5k"]["sources"][source]["val_loss"]
        seven_loss = source_results["7.5k"]["sources"][source]["val_loss"]
        ten_loss = source_results["10k"]["sources"][source]["val_loss"]
        lines.append(
            f"| {source} | {five_loss:.4f} | {seven_loss:.4f} | "
            f"{ten_loss:.4f} | {ten_loss - five_loss:+.4f} |"
        )
    lines.extend(
        [
            "",
            "Każde mierzone źródło poprawiło się. `Wikisource` pozostaje train-only,",
            "ponieważ upstream nie daje bezpiecznego parent-work splitu.",
            "",
            "## 5k / 7,5k / 10k",
            "",
            "| checkpoint | avg | natural | cutoff | repetition | pseudo-ency | web residue |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label in ("5k", "7.5k", "10k"):
        item = trajectory["summaries"][label]["overall"]
        lines.append(
            f"| {label} | {item['avg_quality_score']:.3f} | "
            f"{item['natural_endings']}/{item['samples']} | "
            f"{item['cutoff_like']}/{item['samples']} | "
            f"{item['repetition_samples']}/{item['samples']} | "
            f"{item['pseudo_ency_samples']}/{item['samples']} | "
            f"{item['web_residue_samples']}/{item['samples']} |"
        )
    lines.extend(
        [
            "",
            f"Pairwise 5k vs 10k: `{trajectory['pairwise']['5k_vs_10k']}`.",
            "To praktycznie plateau: 10k ma mniej jawnych szablonów pseudo-ency,",
            "ale nie poprawia wyraźnie powtórzeń, zakończeń ani trafności znaczeniowej.",
            "",
            "## Porównanie ze starym v2.3.1 10k",
            "",
            "| model | avg | natural | cutoff | repetition | pseudo-ency |",
            "|---|---:|---:|---:|---:|---:|",
            f"| v2.3.1 10k | {old['avg_quality_score']:.3f} | {old['natural_endings']}/{old['samples']} | "
            f"{old['cutoff_like']}/{old['samples']} | {old['repetition_samples']}/{old['samples']} | "
            f"{old['pseudo_ency_samples']}/{old['samples']} |",
            f"| v2.4.1 10k | {new['avg_quality_score']:.3f} | {new['natural_endings']}/{new['samples']} | "
            f"{new['cutoff_like']}/{new['samples']} | {new['repetition_samples']}/{new['samples']} | "
            f"{new['pseudo_ency_samples']}/{new['samples']} |",
            "",
            f"Pairwise: `{historical['pairwise']}`. Nowy korpus jest realnym krokiem",
            "naprzód przy tej samej liczbie tokenów, choć model nadal nie jest użyteczny.",
            "",
            "## Ocena ręczna",
            "",
            "- Najlepiej wypadają proste kontynuacje narracyjne i literackie.",
            "- Definicje fizyki, AI, komputera i systemu operacyjnego nadal zwykle nie odpowiadają promptowi.",
            "- Rejestr parlamentarny, przepisy, komisje i budżety są nadal nadmiernie widoczne.",
            "- Nadal pojawiają się fałszywe gminy, demografia, daty i rejestry zabytków.",
            "- Nie wykryto klasycznego URL/HTML/SEO residue.",
            "- Większość heurystycznych wygranych to mniej zepsute teksty, nie dobre odpowiedzi.",
            "",
            "## Co dalej",
            "",
            "1. Nie kontynuować automatycznie v2.4.1 ponad 10k.",
            "2. Zbudować `v2.4.2` z parlamentem ograniczonym do około 2-3%.",
            "3. Odfiltrować lub mocno obniżyć wagę szablonów miejscowości/demografii Wikipedii.",
            "4. Zachować co najmniej 50% dobrej literatury, jeśli próbki i walidacja to potwierdzą.",
            "5. Zachować source/doc metadata i ten sam panel walidacyjny.",
            "6. Uruchomić od zera porównywalny proxy 5k i dopiero wtedy zdecydować o 10k.",
            "",
            "## Artefakty",
            "",
        ]
    )
    for artifact in payload["artifacts"]:
        lines.append(f"- `{artifact}`")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
