#!/usr/bin/env python3
"""Generate the local Glyph report download page.

The page is static HTML for browsing, with a tiny local backend endpoint
for downloading selected files as a ZIP archive.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = ROOT / "report-downloads"
OUTPUT = DOWNLOAD_DIR / "index.html"
DISPLAY_TZ = ZoneInfo("Europe/Warsaw")


@dataclass
class Section:
    title: str
    description: str
    patterns: tuple[str, ...]


SECTIONS = (
    Section(
        "Prompt 2026-09-05: Glyph - pelne podsumowanie projektu",
        "Jeden prompt roboczy: audyt calej historii Glyph, rzeczywisty stan modeli, datasetow, checkpointow, SFT, infrastruktury i stron oraz konkretna kolejnosc dalszych decyzji bez uruchamiania treningu.",
        ("glyph_project_state_20260905",),
    ),
    Section(
        "Prompt 2026-09-01: Glyph v2.4.2 run 10k do 15k",
        "Jeden prompt roboczy: decyzja o wartosciowym kolejnym kroku, preflight checkpointu 10k, bezpieczny start kontrolowanej kontynuacji do 15k, monitoring GPU oraz aktualizacja dashboardu bez automatycznego dalszego etapu.",
        ("glyph100_v2_4_2_15k_launch_20260901", "glyph100_status"),
    ),
    Section(
        "Prompt 2026-09-01: Another Name — produkcyjny budzik HA",
        "Jeden prompt roboczy: aktywny harmonogram pon-pt 06:00, pre-wake Bluetooth, monotoniczny runner audio/light, bezpieczny most MQTT, backup starych automatow, dry-run i raport wdrozenia bez fizycznego show.",
        ("another_name_alarm_runtime_20260901",),
    ),
    Section(
        "Prompt 2026-09-01: Another Name — finalny wake-up ramp",
        "Jeden prompt roboczy: rewizja koncowki choreografii do 100% neutralnej bieli, native white mode dla obu zarowek, XY white dla tasmy oraz bezpieczny Aqara target TBD bez sterowania urzadzeniami.",
        ("another_name_final_wakeup_20260901",),
    ),
    Section(
        "Prompt 2026-08-31: Another Name — analiza i cue sheet",
        "Jeden prompt roboczy: potwierdzenie pliku Ludwig Goransson, analiza waveform/RMS/onset/tempo/struktury, odczytowy audyt lamp HA oraz neutralna choreografia 14 macro cue i 4 grup micro cue bez automatyzacji.",
        ("another_name_choreography_20260831",),
    ),
    Section(
        "Prompt 2026-08-31: Tor audio budzika Bluetooth",
        "Jeden prompt roboczy: uruchomienie Sony SRS-XB33 i mikrofonu jack Realtek, testy reconnect/idle oraz automatyczny pomiar 24 prob opoznienia akustycznego wraz z surowymi danymi.",
        ("audio_alarm_lab_20260831",),
    ),
    Section(
        "Prompt 2026-08-31: Glyph HDD cleanup",
        "Jeden prompt roboczy: bezpieczne odchudzenie starej historii checkpointow, usuniecie nagran Bambu i Gemma oraz kompresja nieuzywanego korpusu z pelna weryfikacja checksum.",
        ("glyph_hdd_cleanup_20260831",),
    ),
    # Keep this list in user-facing newest-work-package -> oldest-work-package order.
    # Do not sort sections by raw mtime: touching an old decision note should not move
    # that whole section above the current work package.
    Section(
        "Prompt 2026-08-26 03: Gleboka diagnostyka Optiarc AD-5260S",
        "Jeden prompt roboczy: surowe SG_IO/MMC, sekwencje LOAD/START/READ, vendor-specific read-only CDB, sense i pomiary czasu rozdzielajace warstwe transportowa od focus/RF/spindle.",
        ("optiarc_deep_diagnostics_20260826",),
    ),
    Section(
        "Prompt 2026-08-26 02: Optiarc AD-5260S z tloczona plyta DVD",
        "Jeden prompt roboczy: powtorzona bezpieczna diagnostyka SCSI/MMC z tloczona DVD, niskopoziomowe statusy SG_IO, porownanie z audio CD oraz rozroznienie focus-lock od spindle/power.",
        ("optiarc_dvd_diagnostics_20260826",),
    ),
    Section(
        "Prompt 2026-08-26 01: Diagnostyka napedu Sony Optiarc AD-5260S",
        "Jeden prompt roboczy: bezpieczna diagnostyka SATA/ATAPI/SCSI/MMC, surowe sense codes, proby odczytu audio CD, logi i ocena prawdopodobnej usterki.",
        ("optiarc_diagnostics_20260826",),
    ),
    Section(
        "Prompt 2026-08-08 04: Glyph v2.4.2 gate and P100 run to 10k",
        "Jeden prompt roboczy: matched quality gate 5k, bezpieczny smoke na Kaggle P100, kontrolowana kontynuacja do 10k, walidacja checkpointu, eval per source i decyzja bez dalszego treningu.",
        (
            "glyph100_v2_4_2_5k_gate_20260808",
            "glyph100_v2_4_2_10k_gate_20260808",
            "glyph100_v2_4_2_p100_10k_20260808",
            "glyph100_v2_4_2_post_10k_decision_20260808",
        ),
    ),
    Section(
        "Prompt 2026-08-08 03: Kaggle P100 CUDA smoke PASS",
        "Jeden prompt roboczy: przydzial P100 po weryfikacji konta, zgodny PyTorch cu126, preflight, 25 krokow FP32, checkpoint round-trip i pomiar wzgledem RX 5500 XT.",
        ("glyph100_kaggle_p100_cuda_smoke_pass_20260808",),
    ),
    Section(
        "Prompt 2026-08-08 02: Kaggle GPU training launch",
        "Jeden prompt roboczy: bezpieczne proby uruchomienia Glyph na P100 i T4, kontrola quota/CUDA oraz diagnoza blokady schedulera przed pierwszym krokiem treningu.",
        ("glyph100_kaggle_gpu_launch_20260808",),
    ),
    Section(
        "Prompt 2026-08-08 01: Kaggle P100 CUDA smoke attempt",
        "Jeden prompt roboczy: ocena sensu powtorki v0.3, prywatny bundle Kaggle, trzy bezpieczne preflighty i diagnoza braku przydzielonego CUDA bez uruchomienia treningu.",
        ("glyph100_kaggle_p100_smoke_attempt",),
    ),
    Section(
        "Prompt 2026-08-02 02: Glyph Colab full upload bundle",
        "Jeden prompt roboczy: materializacja pelnej paczki Colab z base 44k, datasetem, tokenizerem i kodem, pelna weryfikacja oraz wygodny ZIP do pobrania.",
        (
            "glyph_colab_full_bundle_ready",
            "glyph_colab_upload_ready",
        ),
    ),
    Section(
        "Prompt 2026-08-02 01: Glyph Colab migration preparation",
        "Jeden prompt roboczy: audyt 44k, bezpieczny bundle, notebook CUDA, preflight, resume/export, dokumentacja i lokalna walidacja bez treningu ani uploadu.",
        (
            "glyph_colab",
            "colab_migration",
            "colab_bundle_utils",
            "colab_preflight",
            "colab_run_sft",
            "colab_export_results",
        ),
    ),
    Section(
        "Prompt 2026-07-27 03: Lowband Gateway — odporność EDGE",
        "Jeden prompt roboczy: diagnoza klienta, offline-first IndexedDB/PWA, odzyskiwanie utraconych odpowiedzi, testy Weak/Brutal EDGE i wdrożenie 0.1.1.",
        ("lowband_gateway_edge_resilience_20260727",),
    ),
    Section(
        "Prompt 2026-07-27 02: Wdrożenie Lowband Gateway",
        "Jeden prompt roboczy: produkcyjny stack, osobny tunel Cloudflare, izolowane logowanie Codexa, publiczny real E2E i backup odbiorczy.",
        ("lowband_gateway_deployment_20260727",),
    ),
    Section(
        "Prompt 2026-07-27 01: Lowband Gateway",
        "Jeden prompt roboczy: kompletne repozytorium odpornej kolejki researchowej, walidacja API/worker/PWA/izolacji oraz paczka źródłowa.",
        ("lowband_gateway_20260727",),
    ),
    Section(
        "Prompt 2026-07-18 02: Glyph dataset v2.4.2 i świeży run 5k",
        "Jeden prompt roboczy: korekta source mixu, pełna walidacja datasetu v2.4.2, raport readiness i start świeżego proxy 0→5k z automatycznym zatrzymaniem.",
        ("glyph100_v2_4_2", "glyph100_dataset_v2_4_2"),
    ),
    Section(
        "Prompt 2026-07-18 01: Glyph v2.4.1 raport i eval po 10k",
        "Jeden prompt roboczy: weryfikacja końca runu, eval 5k/7,5k/10k, walidacja per source, porównanie ze starym 10k i decyzja o v2.4.2.",
        ("glyph100_v2_4_1_10k_20260718", "glyph100_v2_4_1_10k_eval_20260718"),
    ),
    Section(
        "Prompt 2026-07-17 02: Glyph v2.4.1 run 5k do 10k",
        "Jeden prompt roboczy: preflight checkpointu 5k, start kontrolowanej kontynuacji do 10k, monitoring GPU oraz aktualizacja publicznego dashboardu.",
        ("glyph100_v2_4_1_10k_launch_20260717",),
    ),
    Section(
        "Prompt 2026-07-17 01: Glyph v2.4.1 checkpoint eval po 5k",
        "Jeden prompt roboczy: weryfikacja runu 5k, porownanie checkpointow 1k-5k, walidacja per source, reczna ocena generacji i decyzja o kolejnym kontrolowanym etapie.",
        ("glyph100_v2_4_1_5k_eval_20260717",),
    ),
    Section(
        "Prompt 2026-07-16 02: Glyph v2.4.1 from-scratch 1k",
        "Jeden prompt roboczy: kontrolowany run od zera do 1k, monitoring, checkpoint/resume, base-LM sanity eval i decyzja bez automatycznej kontynuacji do 5k.",
        ("glyph100_v2_4_1_1k_20260716",),
    ),
    Section(
        "Prompt 2026-07-16 01: Glyph next big step and dataset v2.4.1",
        "Jeden prompt roboczy: audyt zrodel, poprawki samplera/EOS/splitu, budowa i walidacja v2.4.1, GPU smoke oraz decyzja o proxy 1k/5k.",
        ("glyph100_next_step_20260716", "glyph100_dataset_v2_4_1"),
    ),
    Section(
        "Prompt 2026-07-07 03: Interstellar Samsung USB",
        "Jeden prompt roboczy: bezpieczne wykrycie i wyczyszczenie pendrive'a USB, exFAT, remux MKV bez rekompresji obrazu i kopia filmu.",
        ("interstellar_samsung_usb_report_20260707",),
    ),
    Section(
        "Prompt 2026-07-07 02: Homelab HA script run",
        "Jeden prompt roboczy: ręczne odpalenie wszystkich skryptow Home Assistanta i sprawdzenie stanow swiatel, logow HA/Zigbee2MQTT/Mosquitto oraz restart count.",
        ("homelab_ha_script_run_report",),
    ),
    Section(
        "Prompt 2026-07-07 01: Homelab core restore",
        "Jeden prompt roboczy: przywrocenie na homelabie HA, Mosquitto i Zigbee2MQTT po powrocie dongla oraz weryfikacja automatyzacji/skryptow przez check_config i logi.",
        ("homelab_core_restore_report",),
    ),
    Section(
        "Prompt 2026-07-05 04: Homelab core capture and shutdown",
        "Jeden prompt roboczy: spójny capture HA/MQTT/Zigbee2MQTT i zatrzymanie wyłącznie starego rdzenia przed przeniesieniem dongla.",
        ("homelab_core_capture_report", "homelab_migration_kit_capture_manifest"),
    ),
    Section(
        "Prompt 2026-07-05 03: Homelab migration kit phase 1 prepare-only",
        "Jeden prompt roboczy: kompletny szkielet migration kitu HA, MQTT i Zigbee2MQTT bez wykonywania capture live data.",
        ("migration_kit_phase1_prepare_report", "homelab_migration_kit_phase1_manifest"),
    ),
    Section(
        "Prompt 2026-07-05 02: Homelab migration USB preparation",
        "Jeden prompt roboczy: bezpieczna identyfikacja, formatowanie i przygotowanie pustego pendrive'a pod migration kit.",
        ("usb_prepare_report",),
    ),
    Section(
        "Prompt 2026-07-05 01: Homelab migration reconnaissance",
        "Jeden prompt roboczy: odczytowy rekonesans uslug, danych, zaleznosci i kandydatow do migracji na Raspberry Pi.",
        ("migration_recon_report", "migration_inventory"),
    ),
    Section(
        "Prompt 2026-07-04 02: Glyph cold-storage migration",
        "Jeden prompt roboczy: migracja nieaktywnych korpusow, datasetow, modeli pomocniczych i historycznych checkpointow na HDD 4 TB.",
        ("glyph_cold_storage_migration_20260704",),
    ),
    Section(
        "Prompt 2026-07-04 01: Glyph checkpoint cleanup",
        "Jeden prompt roboczy: audyt miejsca, bezpieczne usuniecie redundantnych checkpointow i manifest zachowanych modeli.",
        ("glyph_checkpoint_cleanup_20260704",),
    ),
    Section(
        "Prompt 2026-06-25 07: SFT smoke v0.3",
        "Jeden prompt roboczy: analiza v0.2, dataset naprawczy v0.3, trening smoke, eval base/v0.1/v0.2/v0.3 i decyzja koncowa.",
        (
            "sft_v0_3_dataset_plan",
            "glyph100_sft_smoke_v0_3",
            "44k_sft_smoke_v0_3",
            "sft_smoke_v0_3",
            "sft_v0_3_next_decision",
        ),
    ),
    Section(
        "Prompt 2026-06-25 06: SFT v0.2 decoding audit",
        "Jeden prompt roboczy: audit bledow v0.2, sweep dekodowania, porownanie v0.1/v0.2 na najlepszym prescie i finalna decyzja next-step.",
        (
            "sft_v0_2_error_and_decoding_audit",
            "sft_v0_2_decoding_sweep",
            "sft_v0_1_vs_v0_2_best_decoding",
            "sft_v0_2_final_next_decision",
        ),
    ),
    Section(
        "Prompt 2026-06-24 22: SFT smoke v0.2 fixed-mask ROCm",
        "Jeden prompt roboczy: analiza bledow v0.1, dataset v0.2, corrected SFT smoke v0.2, eval base/v0.1/v0.2 i decyzja next-step.",
        (
            "sft_v0_1_error_analysis",
            "glyph100_sft_smoke_v0_2",
            "sft_smoke_v0_2",
            "44k_sft_smoke_v0_2",
            "v0_2-fixedmask-rocm",
            "sft_v0_2_next_decision",
        ),
    ),
    Section(
        "Prompt 2026-06-24 21: Corrected SFT smoke v0.1 fixed-mask ROCm",
        "Jeden prompt roboczy: label-audit preflight, corrected SFT smoke v0.1 na 44k, raport treningu i eval before/after.",
        (
            "sft_label_mask_fix",
            "label_mask_fix",
            "sft_smoke_v0_1_fixedmask",
            "44k_sft_smoke_v0_1_fixedmask",
            "v0_1-fixedmask-rocm",
        ),
    ),
    Section(
        "Prompt 2026-06-24 21: ROCm fixed-mask safe-mode SFT stability",
        "Jeden prompt roboczy: ROCm safe50/safe200 po fixed-mask, raport stabilnosci i decyzja.",
        (
            "sft_tiny_overfit_rocm_fixedmask_safe",
            "sft_rocm_fixedmask_stability",
            "rocm_fixedmask_stability",
            "rocm-fixedmask-safe",
        ),
    ),
    Section(
        "Prompt 2026-06-24 20: SFT fixed-mask repair + CPU tiny overfit",
        "Jeden prompt roboczy: patch label mask, audyt labeli, tiny dataset, CPU tiny overfit, eval i raport decyzji.",
        (
            "sft_label_mask_fix",
            "label_mask_fix",
            "sft_tiny_overfit_cpu_fixedmask",
            "sft_tiny_overfit_fixedmask",
            "44k-sft-tiny-overfit-cpu-fixedmask",
        ),
    ),
    Section(
        "SFT postmortem / pipeline audit",
        "Audyt SFT: template, labels, maskowanie, ROCm NaN i decyzja po smoke tescie.",
        ("sft_postmortem", "pipeline_audit"),
    ),
    Section(
        "SFT smoke run",
        "Kontrolowany SFT smoke na best checkpoint 44k: raport treningu i eval before/after.",
        (
            "glyph100_44k_sft_smoke_report",
            "sft_smoke_44k",
        ),
    ),
    Section(
        "SFT smoke dataset",
        "Dataset SFT smoke v0: raport, walidacja i split train/val.",
        ("glyph100_sft_smoke_v0",),
    ),
    Section(
        "SFT smoke plan",
        "Plan SFT smoke na checkpoint 44k przed uruchomieniem testu.",
        ("sft_smoke_test_plan",),
    ),
    Section(
        "Final pretraining decision",
        "Ostateczna decyzja po v2.3.1: best checkpoint i zatrzymanie pretrainingu.",
        ("final_decision", "post_50k_decision", "v2_3_1-best", "glyph-100m_v2_3_1-best"),
    ),
    Section(
        "50k diagnostic",
        "Raport, eval i decyzja po kontrolnym runie 45k -> 50k.",
        ("50k", "0050000", "44k_45k_50k"),
    ),
    Section(
        "44k vs 45k audit",
        "Techniczny audyt spadku 45k, greedy eval i seed-sensitivity.",
        ("44k_45k", "44k-45k"),
    ),
    Section(
        "Broad eval / best checkpoint",
        "Szerszy eval checkpointow i decyzja o najlepszym punkcie treningu.",
        ("broad", "best_checkpoint", "inference_preset"),
    ),
    Section(
        "45k checkpoint",
        "Raport treningu, sample i porownania dla checkpointu 45k.",
        ("45k", "0045000"),
    ),
    Section(
        "35k checkpoint",
        "Raport treningu, sample i porownania dla checkpointu 35k.",
        ("35k", "0035000"),
    ),
    Section(
        "ROCm / benchmarks",
        "Testy ROCm, batch benchmarki i benchmarki inferencji GPU.",
        ("batch8", "vulkan_context", "rocm", "benchmark"),
    ),
    Section(
        "25k checkpoint",
        "Raport treningu, sample i porownania dla checkpointu 25k.",
        ("25k", "0025000"),
    ),
    Section(
        "10k / 15k preflight",
        "Stage 2, preflight v2.3.1 i porownania 10k -> 15k.",
        ("stage2", "preflight_15k", "10k_vs_15k", "preflight_report"),
    ),
    Section(
        "Dataset v2.x",
        "Raporty budowy i decyzji datasetow Glyph-100M v2.1, v2.2, v2.3 i v2.3.1.",
        (
            "dataset_v2",
            "v2_1_preflight_proposal",
            "finetext",
            "fineweb",
            "wikisource",
            "glyph100_v2_1",
        ),
    ),
    Section(
        "Readiness / approval",
        "Przygotowanie Glyph-100M, approval request, parameter count i decyzje przed treningiem.",
        ("approval_request", "parameter_report", "rocm_smoke", "stage2_attempt", "stage2_recovery"),
    ),
    Section(
        "SFT v0 legacy",
        "Wczesne raporty SFT v0 dla poprzedniego etapu projektu.",
        ("sft_v0",),
    ),
    Section(
        "Archives",
        "Paczki zbiorcze do pobrania jednym plikiem.",
        (".tar.gz", ".zip"),
    ),
    Section(
        "Training snapshots",
        "Automatyczne snapshoty statusu i statystyk treningu.",
        (".summary.json", ".training_stats.json", "latest", "status"),
    ),
)


def fmt_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def file_type(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".tar.gz"):
        return "archive"
    if name.endswith(".json"):
        return "json"
    if name.endswith(".jsonl"):
        return "jsonl"
    if name.endswith(".md"):
        return "markdown"
    if name.endswith(".html"):
        return "report"
    if name.endswith(".sql"):
        return "sql"
    if name.endswith(".ipynb"):
        return "notebook"
    if name.endswith(".py"):
        return "python"
    if name.endswith(".txt"):
        return "text"
    return path.suffix.lstrip(".") or "file"


def display_name(path: Path) -> str:
    name = path.name
    for suffix in (".tar.gz", ".jsonl", ".json", ".html", ".sql", ".ipynb", ".py", ".txt", ".md"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    name = name.replace("glyph100_", "").replace("v2_3_1_", "v2.3.1 ")
    name = name.replace("_", " ").replace("-", " ")
    return " ".join(name.split())


def slug(value: str) -> str:
    safe = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in safe.split("-") if part)


def collect_files() -> list[Path]:
    return sorted(
        p
        for p in DOWNLOAD_DIR.iterdir()
        if p.is_file() and p.name != "index.html" and not p.name.startswith(".")
    )


def load_status() -> dict[str, object] | None:
    path = DOWNLOAD_DIR / "glyph100_status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def assign_sections(files: list[Path]) -> dict[str, list[Path]]:
    remaining = list(files)
    grouped: dict[str, list[Path]] = {section.title: [] for section in SECTIONS}
    grouped["Other files"] = []

    for section in SECTIONS:
        matched: list[Path] = []
        for path in remaining:
            lower = path.name.lower()
            if any(pattern in lower for pattern in section.patterns):
                matched.append(path)
        grouped[section.title].extend(matched)
        remaining = [path for path in remaining if path not in matched]

    grouped["Other files"].extend(remaining)
    return grouped


def render_file(path: Path, section_slug: str) -> str:
    stat = path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime, DISPLAY_TZ).strftime("%Y-%m-%d %H:%M %Z")
    href = html.escape(path.name)
    label = html.escape(display_name(path))
    raw_name = html.escape(path.name)
    size = html.escape(fmt_size(stat.st_size))
    kind = html.escape(file_type(path))
    searchable = html.escape(f"{path.name} {display_name(path)} {kind}".lower())
    value = html.escape(path.name)
    return f"""
          <div class="file-row" data-search="{searchable}" data-section="{html.escape(section_slug)}">
            <label class="check">
              <input class="file-check" type="checkbox" value="{value}" aria-label="Zaznacz {raw_name}">
            </label>
            <span class="file-name">
              <a href="{href}"><strong>{label}</strong></a>
              <small>{raw_name}</small>
            </span>
            <span class="meta"><b>{kind}</b><b>{size}</b><b>{modified}</b></span>
          </div>"""


def render() -> str:
    files = collect_files()
    grouped = assign_sections(files)
    status = load_status()
    generated = datetime.now(DISPLAY_TZ).strftime("%Y-%m-%d %H:%M %Z")
    total_size = sum(path.stat().st_size for path in files)

    sections_html: list[str] = []
    descriptions = {section.title: section.description for section in SECTIONS}
    descriptions["Other files"] = "Pozostale pliki raportowe w katalogu pobierania."

    section_order = []
    for section in SECTIONS:
        paths = grouped.get(section.title, [])
        if paths:
            section_order.append((section.title, paths))
    if grouped.get("Other files"):
        paths = grouped["Other files"]
        section_order.append(("Other files", paths))

    for title, paths in section_order:
        if not paths:
            continue
        section_slug = slug(title)
        ordered = sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)
        items = "\n".join(render_file(path, section_slug) for path in ordered)
        sections_html.append(
            f"""
      <section class="panel" data-section="{html.escape(section_slug)}">
        <div class="section-head">
          <div>
            <h2>{html.escape(title)}</h2>
            <p>{html.escape(descriptions[title])}</p>
          </div>
          <div class="section-actions">
            <button type="button" class="ghost-button" data-select-section="{html.escape(section_slug)}">Zaznacz sekcje</button>
            <button type="button" class="dark-button" data-download-section="{html.escape(section_slug)}" data-name="{html.escape(section_slug)}.zip">Pobierz sekcje</button>
          </div>
        </div>
        <div class="file-list">{items}
        </div>
      </section>"""
        )

    sections = "\n".join(sections_html)
    status_html = ""
    if status:
        avg_quality = status.get("avg_quality") or {}
        avg_items = ""
        if isinstance(avg_quality, dict):
            avg_items = "".join(
                f"<span class=\"pill\"><strong>{html.escape(str(k))}</strong> avg {html.escape(str(v))}</span>"
                for k, v in avg_quality.items()
            )
        status_html = f"""
    <section class="status-card">
      <div>
        <p class="eyebrow">Aktualny status</p>
        <h2>{html.escape(str(status.get("model", "Glyph")))} · {html.escape(str(status.get("status", "unknown")))}</h2>
        <p>{html.escape(str(status.get("verdict", "")))}</p>
        <p class="warning">{html.escape(str(status.get("warning", "")))}</p>
      </div>
      <div class="status-meta">
        <span class="pill"><strong>best</strong> {html.escape(str(status.get("best_checkpoint", "unknown")))}</span>
        <span class="pill"><strong>latest</strong> {html.escape(str(status.get("latest_checkpoint", "unknown")))}</span>
        {avg_items}
      </div>
    </section>"""
    return f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Glyph reports</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f5f2;
      --panel: #ffffff;
      --text: #151515;
      --muted: #696a6a;
      --line: #dedbd4;
      --soft: #efede8;
      --accent: #222;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 15px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 34px 0 48px;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: flex-end;
      padding-bottom: 22px;
      border-bottom: 1px solid var(--line);
      margin-bottom: 22px;
    }}
    h1, h2, p {{ margin: 0; }}
    h1 {{
      font-size: clamp(30px, 5vw, 56px);
      line-height: 0.95;
      letter-spacing: 0;
    }}
    .lead {{
      margin-top: 12px;
      max-width: 700px;
      color: var(--muted);
      font-size: 16px;
    }}
    .stats {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
      min-width: 220px;
    }}
    .pill {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 999px;
      padding: 7px 10px;
      color: var(--muted);
      white-space: nowrap;
    }}
    .pill strong {{ color: var(--text); }}
    .toolbar {{
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}
    .search {{
      width: min(520px, 100%);
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--panel);
      color: var(--text);
      padding: 11px 13px;
      font: inherit;
      outline: none;
    }}
    .search:focus {{
      border-color: #a7a39a;
      box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
    }}
    .hint {{
      color: var(--muted);
      font-size: 13px;
    }}
    button {{
      border: 0;
      font: inherit;
      cursor: pointer;
    }}
    .dark-button, .ghost-button {{
      border-radius: 9px;
      padding: 10px 12px;
      white-space: nowrap;
    }}
    .dark-button {{
      background: var(--accent);
      color: #fff;
    }}
    .dark-button:disabled {{
      opacity: 0.45;
      cursor: not-allowed;
    }}
    .ghost-button {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
    }}
    .section-actions {{
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      margin-top: 14px;
      overflow: hidden;
    }}
    .status-card {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(260px, 0.8fr);
      gap: 18px;
      align-items: start;
      background: #151515;
      color: #fff;
      border-radius: 12px;
      padding: 18px 20px;
      margin: 0 0 16px;
    }}
    .status-card h2 {{
      font-size: 21px;
      margin: 4px 0 8px;
    }}
    .status-card p {{
      color: #d4d2cc;
    }}
    .status-card .warning {{
      margin-top: 8px;
      color: #f2d7a0;
    }}
    .status-card .pill {{
      background: #202020;
      border-color: #383838;
      color: #d4d2cc;
      max-width: 100%;
      overflow-wrap: anywhere;
      white-space: normal;
    }}
    .status-card .pill strong {{
      color: #fff;
    }}
    .eyebrow {{
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 12px;
      color: #aaa !important;
    }}
    .status-meta {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .section-head {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      background: #fbfaf8;
    }}
    h2 {{
      font-size: 17px;
      letter-spacing: 0;
    }}
    .section-head p {{
      color: var(--muted);
      max-width: 580px;
      margin-top: 4px;
    }}
    .file-list {{ display: grid; }}
    .file-row {{
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
      padding: 13px 20px;
      color: inherit;
      border-bottom: 1px solid var(--soft);
    }}
    .file-row:last-child {{ border-bottom: 0; }}
    .file-row:hover {{ background: #f7f6f3; }}
    .check {{
      display: grid;
      place-items: center;
      width: 22px;
      height: 22px;
    }}
    .check input {{
      width: 17px;
      height: 17px;
      accent-color: #151515;
    }}
    .file-name a {{
      color: inherit;
      text-decoration: none;
    }}
    .file-name a:hover {{
      text-decoration: underline;
    }}
    .file-row strong {{
      display: block;
      font-size: 15px;
      font-weight: 650;
      overflow-wrap: anywhere;
    }}
    .file-row small {{
      display: block;
      margin-top: 2px;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .meta {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    .meta b {{
      font-weight: 500;
      color: var(--muted);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 7px;
      background: #fff;
      white-space: nowrap;
      font-size: 12px;
    }}
    footer {{
      color: var(--muted);
      margin-top: 22px;
      font-size: 13px;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      background: #e9e6df;
      border-radius: 5px;
      padding: 2px 5px;
    }}
    @media (max-width: 760px) {{
      header, .section-head, .file-row, .toolbar, .status-card {{
        display: block;
      }}
      .stats, .meta {{
        justify-content: flex-start;
        margin-top: 12px;
      }}
      .section-head p {{
        text-align: left;
        margin-top: 6px;
      }}
      .section-actions {{
        justify-content: flex-start;
        margin-top: 12px;
      }}
      .check {{
        display: inline-grid;
        margin-right: 8px;
      }}
      .hint {{ margin-top: 8px; }}
      .status-meta {{
        justify-content: flex-start;
        margin-top: 12px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Glyph reports</h1>
        <p class="lead">Lokalna strona do pobierania raportow, evali i paczek zwiazanych z treningiem Glyph-100M. Nowe pliki z katalogu <code>report-downloads/</code> sa listowane po regeneracji indeksu.</p>
      </div>
      <div class="stats">
        <span class="pill"><strong>{len(files)}</strong> plikow</span>
        <span class="pill"><strong>{html.escape(fmt_size(total_size))}</strong> lacznie</span>
        <span class="pill">update <strong>{html.escape(generated)}</strong></span>
      </div>
    </header>
{status_html}
    <div class="toolbar">
      <input class="search" id="search" type="search" placeholder="Szukaj raportu, np. 44k, broad, samples, json" autocomplete="off">
      <button type="button" class="dark-button" id="download-selected" disabled>Pobierz zaznaczone ZIP</button>
      <button type="button" class="ghost-button" id="clear-selected">Odznacz</button>
      <p class="hint" id="result-count">{len(files)} plikow</p>
    </div>
{sections}
    <footer>
      Serwowane lokalnie. Publikacja raportow: <code>python3 scripts/publish_report_downloads.py</code>.
    </footer>
  </main>
  <script>
    const search = document.getElementById('search');
    const rows = [...document.querySelectorAll('.file-row')];
    const sections = [...document.querySelectorAll('.panel')];
    const count = document.getElementById('result-count');
    const downloadSelected = document.getElementById('download-selected');
    const clearSelected = document.getElementById('clear-selected');
    const checks = [...document.querySelectorAll('.file-check')];

    function applyFilter() {{
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      for (const row of rows) {{
        const match = !query || row.dataset.search.includes(query);
        row.style.display = match ? '' : 'none';
        if (match) visible += 1;
      }}
      for (const section of sections) {{
        const anyVisible = [...section.querySelectorAll('.file-row')].some(row => row.style.display !== 'none');
        section.style.display = anyVisible ? '' : 'none';
      }}
      count.textContent = query ? `${{visible}} / ${{rows.length}} plikow` : `${{rows.length}} plikow`;
      updateSelection();
    }}

    function selectedFiles(section = null) {{
      return checks
        .filter(input => input.checked)
        .filter(input => !section || input.closest('.file-row').dataset.section === section)
        .map(input => input.value);
    }}

    function visibleSectionFiles(section) {{
      return rows
        .filter(row => row.dataset.section === section && row.style.display !== 'none')
        .map(row => row.querySelector('.file-check').value);
    }}

    function updateSelection() {{
      const selected = selectedFiles();
      downloadSelected.disabled = selected.length === 0;
      const visible = rows.filter(row => row.style.display !== 'none').length;
      const prefix = search.value.trim() ? `${{visible}} / ${{rows.length}} plikow` : `${{rows.length}} plikow`;
      count.textContent = selected.length ? `${{prefix}} · zaznaczone: ${{selected.length}}` : prefix;
    }}

    async function downloadZip(files, name) {{
      if (!files.length) return;
      const response = await fetch('/api/download-zip', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ files, name }})
      }});
      if (!response.ok) {{
        let message = 'Nie udalo sie przygotowac ZIP.';
        try {{
          const error = await response.json();
          if (error.message) message = error.message;
        }} catch {{}}
        alert(message);
        return;
      }}
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = name || 'glyph-reports.zip';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }}

    search.addEventListener('input', applyFilter);
    checks.forEach(input => input.addEventListener('change', updateSelection));
    downloadSelected.addEventListener('click', () => downloadZip(selectedFiles(), 'glyph-selected-reports.zip'));
    clearSelected.addEventListener('click', () => {{
      checks.forEach(input => input.checked = false);
      updateSelection();
    }});
    document.querySelectorAll('[data-select-section]').forEach(button => {{
      button.addEventListener('click', () => {{
        const section = button.dataset.selectSection;
        const visibleFiles = new Set(visibleSectionFiles(section));
        checks.forEach(input => {{
          if (visibleFiles.has(input.value)) input.checked = true;
        }});
        updateSelection();
      }});
    }});
    document.querySelectorAll('[data-download-section]').forEach(button => {{
      button.addEventListener('click', () => {{
        const section = button.dataset.downloadSection;
        downloadZip(visibleSectionFiles(section), button.dataset.name || 'glyph-section.zip');
      }});
    }});
    updateSelection();
  </script>
</body>
</html>
"""


def main() -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
