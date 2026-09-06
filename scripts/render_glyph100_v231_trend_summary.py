#!/usr/bin/env python3
"""Render 25k/35k/45k trend summary for Glyph-100M v2.3.1 evals."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "eval" / "glyph-100m" / "v2_3_1_25k_35k_45k_summary.md"
EVAL_35K = ROOT / "eval" / "glyph-100m" / "v2_3_1_35k_samples.json"
EVAL_45K = ROOT / "eval" / "glyph-100m" / "v2_3_1_45k_samples.json"
REPORTS = {
    "25k": ROOT / "reports" / "glyph100_v2_3_1_25k_report.json",
    "35k": ROOT / "reports" / "glyph100_v2_3_1_35k_report.json",
    "45k": ROOT / "reports" / "glyph100_v2_3_1_45k_report.json",
}


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def aggregate(summary: dict) -> dict:
    rows = list(summary.values())
    count = sum(row["count"] for row in rows)
    if not count:
        return {}
    return {
        "count": count,
        "repetition_samples": sum(row["repetition_samples"] for row in rows),
        "natural_endings": sum(row["natural_endings"] for row in rows),
        "cutoff_like_samples": sum(row["cutoff_like_samples"] for row in rows),
        "pseudo_ency_samples": sum(row["pseudo_ency_samples"] for row in rows),
        "web_residue_samples": sum(row["web_residue_samples"] for row in rows),
        "wiki_residue_samples": sum(row["wiki_residue_samples"] for row in rows),
        "avg_quality_score": round(
            sum(row["avg_quality_score"] * row["count"] for row in rows) / count,
            2,
        ),
    }


def final_val_loss(report: dict) -> str:
    values = report.get("val_losses") or []
    if not values:
        return "n/a"
    return str(values[-1].get("val_loss", "n/a"))


def main() -> None:
    eval35 = read_json(EVAL_35K)
    eval45 = read_json(EVAL_45K)
    reports = {label: read_json(path) for label, path in REPORTS.items() if path.exists()}

    checkpoint_summary = {
        "25k": aggregate(eval35["summaries"]["25k"]),
        "35k": aggregate(eval45["summaries"]["35k"]),
        "45k": aggregate(eval45["summaries"]["45k"]),
    }

    lines = [
        "# Glyph-100M v2.3.1 trend: 25k -> 35k -> 45k",
        "",
        "Base LM continuation eval. To nie jest ocena modelu jako asystenta.",
        "",
        "## Aggregate Metrics",
        "",
        "| checkpoint | repetition | natural endings | cutoff-like | pseudo-ency | web residue | wiki residue | avg quality | final val_loss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ["25k", "35k", "45k"]:
        row = checkpoint_summary[label]
        report = reports.get(label, {})
        lines.append(
            "| {label} | {rep}/{count} | {end}/{count} | {cut}/{count} | {pseudo}/{count} | "
            "{web}/{count} | {wiki}/{count} | {quality} | {val} |".format(
                label=label,
                rep=row["repetition_samples"],
                end=row["natural_endings"],
                cut=row["cutoff_like_samples"],
                pseudo=row["pseudo_ency_samples"],
                web=row["web_residue_samples"],
                wiki=row["wiki_residue_samples"],
                quality=row["avg_quality_score"],
                count=row["count"],
                val=final_val_loss(report),
            )
        )

    lines.extend(
        [
            "",
            "## Pairwise Comparisons",
            "",
            "### 25k vs 35k",
            "",
            f"- 35k wins: `{eval35['winner_counts'].get('35k', 0)}`",
            f"- 25k wins: `{eval35['winner_counts'].get('25k', 0)}`",
            f"- ties: `{eval35['winner_counts'].get('tie', 0)}`",
            "",
            "### 35k vs 45k",
            "",
            f"- 45k wins: `{eval45['winner_counts'].get('45k', 0)}`",
            f"- 35k wins: `{eval45['winner_counts'].get('35k', 0)}`",
            f"- ties: `{eval45['winner_counts'].get('tie', 0)}`",
            "",
            "## Read",
            "",
            "- 35k was the clear improvement step: fewer repetitions than 25k and much better pairwise score.",
            "- 45k does not improve as strongly as 35k did over 25k; in this eval it loses more often than it wins.",
            "- 45k keeps web/wiki residue near zero, but pseudo-ency patterns increase and natural endings do not improve.",
            "- Cutoff-like completions remain the dominant issue across all checkpoints.",
            "- The final validation loss at 45k is lower than the noisy 35k endpoint, but sample quality does not clearly track that improvement.",
            "",
            "## Decision Implication",
            "",
            "The 45k checkpoint should not automatically justify a 50k continuation. The next decision should be based on either a broader eval/inference sweep or a deliberate stop/pre-SFT branch, not momentum alone.",
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
