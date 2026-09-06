# Glyph-100M v2.3.1 preflight report

## Checkpointy

- 10k: `checkpoints/glyph-100m/latest.pt` · step `10000` · variant `glyph-100m`
- 15k: `checkpoints/glyph-100m-v2_3_1-preflight/latest.pt` · step `15000` · variant `glyph-100m`
- tokenizer: `data/processed/tokenizer.model`
- tokenizer sha256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## Ustawienia generacji

- base LM continuation, nie assistant/instruction eval
- seed base: `20260531`
- presety: conservative, normal, creative
- max_new_tokens: 120

## Wyniki

- 15k wins: 10
- 10k wins: 9
- ties: 17

## Interpretacja ręczna

- 15k jest **lekko lepsze**, ale nie jest to jakościowy przełom.
- Największa poprawa: 15k praktycznie usuwa jawne wiki-headery typu `Przypisy`, `Bibliografia`, `Linki zewnętrzne`, `Zobacz też` w tym zestawie próbek.
- Normal/creative wypadają lepiej niż conservative. Conservative przy 15k często wpada w pętle typu `Strata`, `BB`, `w Polsce`, `bezpieczeństwa`.
- 15k nadal produkuje dużo pseudo-encyklopedycznych halucynacji: fikcyjne wsie, lata, gminy, instytuty, wojskowo-techniczne opisy bez związku z promptem.
- Temat jest trzymany słabo. Prompty edukacyjne typu `Sztuczna inteligencja jest` albo `Uczenie maszynowe polega na` często dryfują w losowe teksty o depresji, pojazdach, silnikach albo administracji.
- Naturalne zakończenia praktycznie nie występują, bo generacja dobija do `max_new_tokens=120`. To jest problem dekodowania/stopowania, nie tylko jakości checkpointu.
- Brak wyraźnego commerce/cookie residue. Web residue jest dużo mniejszym problemem niż wiki/pseudo-encyklopedyczny styl.

## Zmiany 10k → 15k

- Repetition samples: `19 → 15`, czyli lekka poprawa.
- Wiki residue samples: `6 → 0`, wyraźna poprawa.
- Web residue samples: `0 → 1`, bez istotnego problemu; jeden hit jest słaby/heurystyczny.
- Pseudo-ency samples: `6 → 12`, regresja lub ujawnienie mocniejszego stylu pseudo-ency.
- Conservative avg quality: `1.75 → 1.17`, gorzej.
- Normal avg quality: `3.33 → 4.17`, lepiej.
- Creative avg quality: `4.67 → 5.25`, lepiej.

## Decyzja praktyczna

15k potwierdza, że czystszy v2.3.1 pomaga ograniczać najbrzydsze wiki-residue, ale nie wystarcza do decyzji o długim treningu. Model nadal uczy się formy encyklopedycznej bez stabilnego rozumienia tematu. Przed kolejnym długim etapem trzeba poprawić dataset/eval oraz rozważyć dekodowanie z lepszym stopowaniem i repetition controls.

## Summary 10k

```json
{
  "conservative": {
    "count": 12,
    "avg_tokens_per_second": 12.7,
    "repetition_samples": 10,
    "natural_endings": 1,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 3,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 1,
    "avg_quality_score": 1.75
  },
  "normal": {
    "count": 12,
    "avg_tokens_per_second": 12.46,
    "repetition_samples": 6,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 2,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 3,
    "avg_quality_score": 3.33
  },
  "creative": {
    "count": 12,
    "avg_tokens_per_second": 12.49,
    "repetition_samples": 3,
    "natural_endings": 1,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 1,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 2,
    "avg_quality_score": 4.67
  }
}
```

## Summary 15k

```json
{
  "conservative": {
    "count": 12,
    "avg_tokens_per_second": 12.43,
    "repetition_samples": 11,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 4,
    "avg_quality_score": 1.17
  },
  "normal": {
    "count": 12,
    "avg_tokens_per_second": 12.21,
    "repetition_samples": 3,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 1,
    "pseudo_ency_samples": 5,
    "avg_quality_score": 4.17
  },
  "creative": {
    "count": 12,
    "avg_tokens_per_second": 12.14,
    "repetition_samples": 1,
    "natural_endings": 0,
    "web_garbage_samples": 0,
    "wiki_residue_samples": 0,
    "web_residue_samples": 0,
    "pseudo_ency_samples": 3,
    "avg_quality_score": 5.25
  }
}
```

## Werdykt

**B) 15k trochę lepsze, ale najpierw poprawić dataset/eval.**

## Uwagi jakościowe

- Ten eval jest heurystyczny i jakościowy; najważniejsze próbki są w `eval/glyph-100m/v2_3_1_10k_vs_15k.md`.
- Model nadal jest base LM, więc pseudo-encyklopedyczne completions nie są tym samym co odpowiedzi asystenta.
- Dalszy trening wymaga osobnej zgody; ten raport nie uruchamia stage 3.
