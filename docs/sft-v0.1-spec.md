# Specyfikacja Glyph-27M SFT v0.1

To jest plan korekcyjnego SFT, nie dataset i nie uruchomienie treningu.

## Cel

SFT v0.1 ma naprawić główne problemy widoczne po SFT v0:

- schematyczny ton,
- dryf do porad projektowych przy pytaniach faktograficznych lub edycyjnych,
- brak wykonania zadań typu popraw / streść / napisz,
- słabe krótkie definicje,
- powtarzanie fraz z datasetu v0,
- odpowiedzi, które formalnie kończą się poprawnie, ale nie odpowiadają na pytanie.

Nie chodzi o dodanie dużej ilości wiedzy o świecie. Celem jest lepsze wykonywanie prostych instrukcji przez mały model 27M.

## Rozmiar

Startowo: 400-700 bardzo dobrych przykładów.

Nie warto robić od razu dużego datasetu. Model jest mały i ma context 256, więc ważniejsza jest gęsta korekta konkretnych błędów niż objętość.

## Kategorie

Proponowany miks:

- 150 direct factual answers / proste definicje,
- 120 rewrite/summarize output-only,
- 120 brak danych z różnymi sformułowaniami,
- 100 korekta błędnych założeń bez project-advice,
- 80 anty-pętle i krótkie zakończenia,
- 50 techniczne proste, ostrożne.

Razem daje to 620 przykładów. Wariant 400 przykładów też ma sens, jeśli będzie lepiej kuratorowany.

## Frazy zakazane lub mocno ograniczane

Eval v0 pokazał nadużywanie:

- `najkrótszy ruch`,
- `mały test`,
- `podejdź do tego jak do...`,
- `jeśli po tym dalej`,
- `w praktyce warto`,
- `rdzeń projektu`,
- `zacznij od małego kroku`.

To nie jest absolutny ban na zawsze. Chodzi o odtrucie v0.1 z tych manier, żeby model przestał używać ich jako uniwersalnej odpowiedzi na wszystko.

## Wymagania stylu

- Krótkie odpowiedzi.
- Bez lania wody.
- Bez zamieniania pytań faktograficznych w porady projektowe.
- Definicje: definicja, ewentualnie mały przykład, koniec.
- Rewrite: tylko poprawiony tekst, chyba że prompt prosi o komentarz.
- Streszczanie: tylko streszczenie.
- Brak danych: jasno powiedzieć, czego brakuje.
- Korekta założenia: poprawić założenie i krótko uzasadnić.
- Tematy potencjalnie ryzykowne: nie udawać pewności, prosić o kontekst.

## Format datasetu

JSONL:

```json
{
  "id": "sft-v0.1-000001",
  "category": "...",
  "instruction": "...",
  "response": "...",
  "source": "synthetic_curated",
  "quality": "approved"
}
```

Template treningowy zostaje taki sam:

```text
<|user|>
{instruction}
<|assistant|>
{response}
<|end|>
```

Bez system promptu. Context length zostaje 256 tokenów.

## Typy przykładów obowiązkowych

### Brak danych

Używać różnych sformułowań:

- `Nie mam wystarczających informacji, żeby to ocenić. Podaj model, cenę i zastosowanie.`
- `Tego nie da się rozstrzygnąć z samego opisu. Potrzebne są dane wejściowe i kryterium poprawności.`
- `Nie widzę zdjęcia, więc nie mogę ocenić wyglądu. Opisz je albo prześlij plik.`

Nie zaczynać każdego przykładu tak samo.

### Rewrite i streszczanie

Przy rewrite odpowiedź powinna być output-only:

```json
{
  "instruction": "Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.",
  "response": "Ten projekt jest dopracowany, ma wiele przydatnych funkcji i działa sprawnie."
}
```

Przy streszczaniu odpowiedź nie powinna tłumaczyć, czym jest streszczenie.

### Proste definicje

Krótkie przykłady:

- pogoda vs klimat,
- inflacja,
- fakt vs opinia,
- grawitacja,
- backup,
- tokenizer,
- checkpoint,
- walidacja,
- trening vs inferencja.

Każda odpowiedź: 1-3 zdania.

### Korekta błędnych założeń

Poprawiać założenie wprost:

```text
Nie. Droższy sprzęt nie zawsze jest lepszy; liczy się zastosowanie, jakość i cena względem potrzeb.
```

Nie dryfować w ogólne zarządzanie projektem, jeśli prompt nie dotyczy projektu.

### Anty-pętle

Dodać przykłady:

- jedno zdanie,
- maksymalnie pięć słów,
- odpowiedz dokładnie `nie wiem`,
- zakończ po jednej myśli,
- nie powtarzaj wskazanego słowa.

## Walidacja przed treningiem

Przed jakimkolwiek SFT v0.1:

- walidacja JSONL,
- wymagane pola,
- duplikaty instruction,
- liczba tokenów realnym SentencePiece,
- odrzucenie lub skrócenie przykładów powyżej context 256 po template,
- raport proporcji kategorii,
- scan zakazanych / ograniczanych fraz,
- ręczna inspekcja minimum 50 losowych przykładów.

## Strategie treningowe do przetestowania

Nie trenować teraz. Później porównać dwa warianty.

### A: base final -> pełny poprawiony dataset SFT v0 + v0.1

Start z `checkpoints/final.pt`, trening na oczyszczonym połączonym zbiorze.

Hipoteza: mniej stylowego skażenia z v0 i mniej utrwalonych manier.

Ryzyko: jeśli stare dane nie zostaną odfiltrowane, model może ponownie nauczyć się części problemów.

### B: sft-v0-final -> sam corrective patch v0.1

Start z `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`, trening tylko na przykładach korekcyjnych.

Hipoteza: szybciej naprawi konkretne błędy.

Ryzyko: może utrwalić maniery v0 i przestylizować model jeszcze mocniej.

## Rekomendacja przed treningiem

Najpierw krótkie smoke testy obu wariantów:

- maks. 50-100 kroków,
- ten sam prompt set eval v0.1,
- porównać Base, SFT v0, wariant A i wariant B,
- wybrać dopiero po obejrzeniu sampli.

Wstępna preferencja: najpierw test A, bo celem v0.1 jest ograniczenie skażenia stylem v0, a nie tylko naklejenie małej łatki na już przestylizowany checkpoint.
