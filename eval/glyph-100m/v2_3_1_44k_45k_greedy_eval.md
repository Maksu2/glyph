# Glyph-100M v2.3.1 44k vs 45k greedy eval

Deterministic base LM continuation eval. `temperature=0.0`, no top-k/top-p sampling.

- prompts: `60`
- generations: `240`

## Summary

- 45k wins: `18`
- 44k wins: `19`
- ties: `83`

## By Checkpoint

```json
{
  "44k": {
    "count": 120,
    "avg_quality_score": 1.058,
    "median_quality_score": 1.0,
    "avg_tokens_per_second": 70.81,
    "repetition_samples": 116,
    "natural_endings": 2,
    "cutoff_like_samples": 118,
    "web_garbage_samples": 2,
    "web_residue_samples": 4,
    "wiki_residue_samples": 2,
    "pseudo_ency_samples": 12,
    "geo_history_suspect_samples": 12,
    "topic_drift_samples": 54,
    "avg_topic_overlap": 0.157
  },
  "45k": {
    "count": 120,
    "avg_quality_score": 1.192,
    "median_quality_score": 1.0,
    "avg_tokens_per_second": 71.11,
    "repetition_samples": 117,
    "natural_endings": 5,
    "cutoff_like_samples": 115,
    "web_garbage_samples": 2,
    "web_residue_samples": 4,
    "wiki_residue_samples": 0,
    "pseudo_ency_samples": 10,
    "geo_history_suspect_samples": 10,
    "topic_drift_samples": 54,
    "avg_topic_overlap": 0.16
  }
}
```

## By Preset

```json
{
  "greedy_120": {
    "count": 120,
    "avg_quality_score": 0.825,
    "median_quality_score": 0.0,
    "avg_tokens_per_second": 68.04,
    "repetition_samples": 120,
    "natural_endings": 3,
    "cutoff_like_samples": 117,
    "web_garbage_samples": 2,
    "web_residue_samples": 4,
    "wiki_residue_samples": 1,
    "pseudo_ency_samples": 12,
    "geo_history_suspect_samples": 12,
    "topic_drift_samples": 54,
    "avg_topic_overlap": 0.161
  },
  "greedy_80": {
    "count": 120,
    "avg_quality_score": 1.425,
    "median_quality_score": 1.0,
    "avg_tokens_per_second": 73.88,
    "repetition_samples": 113,
    "natural_endings": 4,
    "cutoff_like_samples": 116,
    "web_garbage_samples": 2,
    "web_residue_samples": 4,
    "wiki_residue_samples": 1,
    "pseudo_ency_samples": 10,
    "geo_history_suspect_samples": 10,
    "topic_drift_samples": 54,
    "avg_topic_overlap": 0.156
  }
}
```

## Largest 45k regressions

### broad-051 · greedy_80 · delta=-10

- 44k score: `0`
- 45k score: `-10`

**44k:**
```text
Wisła przepływa przez Wisłę, a następnie przez Wisłę. W latach 1975–1998 miejscowość administracyjnie należała do województwa bielskiego. W miejscowości znajduje się kościół parafialny pw. św. Stanisława Biskupa i Męczennika, który został poświęcony w 1830 r. przez ks. proboszcza Józefa Gąsiorowskiego. Gąsiorowo – wieś w Polsce położona w województwie wielkopolskim, w powiecie kro
```
**45k:**
```text
Wisła przepływa przez Wisłę. W latach 1975–1998 miejscowość administracyjnie należała do województwa piotrkowskiego. Wierni Kościoła rzymskokatolickiego należą do parafii św. Stanisława Biskupa i Męczennika w Wiślicy. Wiślica – wieś w Polsce położona w województwie lubelskim, w powiecie łukowskim, w gminie Łuków. W latach 1975–1998 miejscowość administracyjnie należała do województwa siedleckiego. Wieś stanowi sołectwo w
```

### broad-043 · greedy_80 · delta=-5

- 44k score: `6`
- 45k score: `1`

**44k:**
```text
Według najnowszych danych, w tym: gęstość zaludnienia wynosiła 79,1 osób/km2 (wśród 2290 gmin Akwitanii Saint-Martin-de-Villages plasuje się na 712. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 1332.). Saint-Martin-de-Villages – miejscowość i gmina we Francji, w regionie Nowa Akwitania
```
**45k:**
```text
Według najnowszych danych na rok 1990 gminę zamieszkiwało 311 osób, a gęstość zaludnienia wynosiła 28 osób/km2 (wśród 2290 gmin Akwitanii Saint-Martin-de-Calais Saint-Martin-de-Calais Saint-Martin-de-Calais Saint-Martin-de-Calais Saint-Martin-de-Cala
```

### broad-010 · greedy_80 · delta=-4

- 44k score: `4`
- 45k score: `0`

**44k:**
```text
Sieć komputerowa pozwala na szybkie i łatwe korzystanie z usług takich jak: - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputer
```
**45k:**
```text
Sieć komputerowa pozwala na tworzenie i odtwarzanie dźwięku w dowolnym miejscu. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu, może to być konieczne, aby nie było podłączenia do komputera. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu, może to być konieczne, aby nie było podłączenia do komputera. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu
```

### broad-025 · greedy_80 · delta=-4

- 44k score: `4`
- 45k score: `0`

**44k:**
```text
Rano wyszedłem z domu i z powrotem do domu. W tym samym czasie, gdy w domu mieszkał, wstąpił do szkoły, a następnie do szkoły, gdzie uczył się gry na fortepianie. W wieku 15 lat, w wieku 15 lat, został przyjęty do szkoły muzycznej, a następnie do szkoły muzycznej. W wieku 15 lat, w wieku 15 lat, został przyjęty do szkoły muzycznej w Warszawie
```
**45k:**
```text
Rano wyszedłem z domu i poszedł do pracy. W końcu, gdy w końcu, gdy w końcu, gdy się nie skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem,
```

### broad-034 · greedy_80 · delta=-4

- 44k score: `4`
- 45k score: `0`

**44k:**
```text
Powtarzanie słów sprawia, że tekst jest bardziej skomplikowany i bardziej skomplikowany. W tym artykule przyjrzymy się bliżej temu, jak napisać tekst, aby dowiedzieć się więcej o tym, jak napisać tekst, aby dowiedzieć się więcej o tym, jak napisać tekst. W tym artykule przyjrzymy się bliżej temu, jak przygotować odpowiednie materiały do budowy domu. W tym artykule przyjrzymy się bliżej temu, jak przygotować odpowiednie
```
**45k:**
```text
Powtarzanie słów sprawia, że tekst jest w pełni zrozumiały dla czytelnika. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyj
```

### broad-010 · greedy_120 · delta=-4

- 44k score: `4`
- 45k score: `0`

**44k:**
```text
Sieć komputerowa pozwala na szybkie i łatwe korzystanie z usług takich jak: - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sieć komputerowa, - Sie
```
**45k:**
```text
Sieć komputerowa pozwala na tworzenie i odtwarzanie dźwięku w dowolnym miejscu. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu, może to być konieczne, aby nie było podłączenia do komputera. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu, może to być konieczne, aby nie było podłączenia do komputera. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu, może to być konieczne, aby nie było podłączenia do komputera. W przypadku podłączenia do komputera, w którym nie ma dostępu do Internetu, może to być konieczne, aby nie było podłączenia do
```

### broad-025 · greedy_120 · delta=-4

- 44k score: `4`
- 45k score: `0`

**44k:**
```text
Rano wyszedłem z domu i z powrotem do domu. W tym samym czasie, gdy w domu mieszkał, wstąpił do szkoły, a następnie do szkoły, gdzie uczył się gry na fortepianie. W wieku 15 lat, w wieku 15 lat, został przyjęty do szkoły muzycznej, a następnie do szkoły muzycznej. W wieku 15 lat, w wieku 15 lat, został przyjęty do szkoły muzycznej w Warszawie, gdzie uczył się gry na fortepianie. W wieku 15 lat, w wieku 15 lat, został przyjęty do Szkoły Muzycznej w Warszawie, gdzie uczył się gry na fortepianie
```
**45k:**
```text
Rano wyszedłem z domu i poszedł do pracy. W końcu, gdy w końcu, gdy w końcu, gdy się nie skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było już tak, jak się skończyło. W końcu, gdy się skończyłem, nie było
```

### broad-034 · greedy_120 · delta=-4

- 44k score: `4`
- 45k score: `0`

**44k:**
```text
Powtarzanie słów sprawia, że tekst jest bardziej skomplikowany i bardziej skomplikowany. W tym artykule przyjrzymy się bliżej temu, jak napisać tekst, aby dowiedzieć się więcej o tym, jak napisać tekst, aby dowiedzieć się więcej o tym, jak napisać tekst. W tym artykule przyjrzymy się bliżej temu, jak przygotować odpowiednie materiały do budowy domu. W tym artykule przyjrzymy się bliżej temu, jak przygotować odpowiednie materiały do budowy domu. W tym artykule przyjrzymy się bliżej temu, jak przygotować odpowiednie materiały do budowy domu. W tym artykule przyjrzymy się bliżej temu, jak przygotować odpowiednie materiały do
```
**45k:**
```text
Powtarzanie słów sprawia, że tekst jest w pełni zrozumiały dla czytelnika. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W tym artykule przyjrzymy się bliżej temu tematowi. W artykule przyjrzymy się bliżej temu tematowi. W artykule przyjrzymy się
```
