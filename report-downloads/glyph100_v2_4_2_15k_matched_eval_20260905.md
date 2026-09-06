# Glyph-100M v2.4.2: matched eval 10k vs 12.5k vs 15k — wyniki zmierzone

Data: 2026-09-05. Oba przebiegi wykonane na **CPU** (host torch 2.11.0+cu130 zgłasza
brak CUDA; brak GPU ROCm na tym hoście; backend sdpa). Zero pending — wszystkie komórki
poniżej to realne pomiary z tego samego panelu (20 promptów, presety conservative/normal,
seed 20260717 + prompt_index). Treningu nie uruchamiano, wag nie ruszono, nic nie usunięto.

## Tabela matched eval (przebieg 1, CPU, exit 0, 120 próbek)

| checkpoint | avg | mediana | naturalne | ucięcia | pętle | pseudo-ency | web |
|---|---:|---:|---:|---:|---:|---:|---:|
| v242_10k | 3.450 | 4.0 | 6/40 | 34/40 | 13/40 | 0/40 | 0/40 |
| v242_12_5k | 2.350 | 1.0 | 5/40 | 36/40 | 24/40 | 0/40 | 0/40 |
| v242_15k | 3.525 | 4.0 | 10/40 | 33/40 | 13/40 | 0/40 | 0/40 |

Per-preset: conservative avg 2.75 / 1.45 / 3.25; normal avg 4.15 / 3.25 / 3.80
(10k / 12.5k / 15k). Pairwise: 10k vs 12.5k 17–5–18; 12.5k vs 15k 4–19–17;
10k vs 15k 9–12–19. Heurystyczny best: **v242_15k**.

Uwaga o dryfie 10k: tu 10k mierzy 3.450 vs 3.200 w gate z 2026-08-08 (ROCm, inny backend
uwagi). Mały dryf numeryczny między backendami jest oczekiwany; porównujemy tylko
komórki wewnątrz tego samego przebiegu.

## Panel z v2.3.1 44k (przebieg 2, `--with-v231-44k`, CPU, exit 0, 160 próbek)

| checkpoint | avg | mediana | naturalne | ucięcia | pętle | pseudo-ency | web |
|---|---:|---:|---:|---:|---:|---:|---:|
| v231_44k | 3.350 | 4.0 | 12/40 | 30/40 | 20/40 | 0/40 | 0/40 |

Komórki trajektorii identyczne jak w przebiegu 1 (determinizm CPU potwierdzony).
Pairwise: 10k vs 44k 12–12–16; 12.5k vs 44k 9–18–13; **15k vs 44k 13–11–16**.
Kontrakty: strict v2.4.2 dla trzech kandydatów + relaxed (step+wariant+tokenizer SHA)
dla 44k — wszystkie ważne.

## Ręczny przegląd (wymiary ze specyfikacji)

- Składnia: ortografia czysta wszędzie (odd_word_ratio 0.0, zero pseudo/web trafień);
  dominant_word_share 10k 0.1445 / 12.5k 0.1800 / 15k 0.1419 — pik pętli na 12.5k.
- Temat: słaby base-LM na wszystkich; 44k częściej otwiera w temacie (ramki miejskie /
  spisowe) i dryfuje; v242 dryfuje w literackość/dialogi lub spam dat. Bez różnicowania.
- Pętle: 12.5k zapadnięty (24/40), 44k często (20/40), 10k/15k umiarkowanie (13/40).
- Ucięcia: limit 80 tokenów wiąże prawie wszystko (34/36/33/40 v242, 30/40 44k).
- Naturalne zakończenia: 44k 12/40 > 15k 10/40 > 10k 6/40 > 12.5k 5/40.
- Pseudo-ency/web: 0/40 wszędzie, z zastrzeżeniem pokrycia wzorców (tekst spiso-podobny
  44k nie wyzwolił regexów — zero to pokrycie, nie dowód nieobecności).
- Błędy faktograficzne: powszechne wszędzie. 10k zmyśla daty/instytucje (1863, Polski
  Związek Pisarzy, programy BBC, Puchar Davisa); 12.5k zmyśla byty (Marek Kobeński,
  Kinformator) i spamuje listami dat; 15k leje wodę, wciąż błędnie (ML = silniki
  elektryczne, eksperyment z 1966); 44k zmyśla liczby spisowe (89.1%, droga 666,
  średnica Ziemi 119.6 km, „Woda trująca"). Żaden checkpoint nie nadaje się faktograficznie.

## Kanoniczny best v2.4.2

**`checkpoints/glyph-100m-v2_4_2-15k/step_0015000.pt`** (wagi identyczne z `latest.pt` —
zweryfikowano rekurencyjnie 413/413 tensorów 2026-09-05; pliki różnią się tylko
metadanymi). Uzasadnienie: najwyższy avg (3.525), wygrywa pairwise z oboma
rodzeństwami (12–9 z 10k, 19–4 z 12.5k), najwięcej naturalnych zakończeń w v2.4.2
(10/40), a przegląd ręczny potwierdza brak regresji semantycznej względem 10k i wyraźnie
czystszy obraz niż zapętlony 12.5k. Ukoronowany na generacji mimo val 3.9755 powyżej
minimum 11k (3.9538) — zgodnie z regułą decyzji.

## Werdykt vs v2.3.1 44k

**Parzystość w granicach szumu**: 15k (3.525) vs 44k (3.350), pairwise 13–11–16 przy
16 remisach. Brak podstaw do twierdzenia, że v2.4.2 bije historyczny 44k — 15k dorównuje
mu na tym panelu (mniej pętli, ale mniej naturalnych zakończeń). Historyczne 6.198 dla
44k to inna skala/panel — nie porównywać wprost.

## Rekomendacja

**STOP dla treningu v2.4.2**: generacja potwierdza plateau val (zapadnięcie 12.5k;
15k wraca tylko do poziomu ~10k, pairwise 12–9 blisko remisu). Żadnego 20k bez
zweryfikowanej zmiany harmonogramu LR i nowego zapisu decyzji.

Pliki: `eval/glyph-100m/glyph100_v2_4_2_15k_trajectory_20260905[_with_v23144k]_{samples,comparison}.{json,md}`
(8 plików). Szczegóły liczbowe: `reports/glyph100_v2_4_2_15k_matched_eval_20260905.json`.
