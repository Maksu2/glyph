# Glyph-27M dashboard - instrukcja obsługi

## Dla osoby oglądającej

Otwórz:

```text
https://trening.maksu.online
```

Strona pokazuje postęp treningu Glyph-27M Base, loss, throughput, checkpoint, tryb zasobów oraz ostatnie próbki ocenione przez Gemmę. Dane odświeżają się w tle co 20 sekund, bez przeładowania strony.

## Promptowanie modelu

Panel `Inferencja Glyph-27M` pozwala wpisać krótki prompt, czyli początek tekstu do dokończenia, np.:

```text
Warszawa to
```

Glyph-27M Base jest bazowym modelem kontynuującym tekst, nie asystentem po instruction tuningu. Najlepiej działają początki zdań albo krótkie fragmenty tekstu do dokończenia.

Dobre prompty dla tego etapu:

```text
Warszawa to
Dawno temu w Krakowie
Uczeń zapytał nauczyciela:
Model językowy działa tak, że
```

Gorsze prompty dla tego etapu:

```text
Napisz mi kompletną odpowiedź na pytanie...
Zachowuj się jak asystent i wykonaj instrukcję...
```

Polecane parametry startowe:

```text
Tokeny: 50
Temp: 0.75
Top-k: 50
Top-p: 0.92
Rep: 1.10
N-gram: 4
```

Znaczenie parametrów:

- `Tokeny`: maksymalna długość dopisanej odpowiedzi. Więcej tokenów daje dłuższy tekst, ale zwiększa ryzyko pętli i dłużej obciąża CPU.
- `Temp`: temperatura losowania. Wyżej = odważniej i dziwniej, niżej = bardziej zachowawczo. Dla publicznego testowania `0.75` jest przyjemnym startem.
- `Top-k`: model losuje tylko z `k` najbardziej prawdopodobnych następnych tokenów. `0` wyłącza ten filtr, `50` daje trochę swobody bez pełnego chaosu.
- `Top-p`: nucleus sampling. Model bierze najmniejszy zestaw tokenów, których łączne prawdopodobieństwo dobija do `p`. `0.92` daje kompromis między stabilnością i różnorodnością.
- `Rep`: repetition penalty, czyli kara za powtarzanie tokenów z kontekstu. `1.00` wyłącza, `1.08-1.15` może ograniczyć pętle, ale za wysoko może psuć naturalność.
- `N-gram`: blokada powtarzania tej samej sekwencji tokenów. `4` zwykle pomaga na frazy powtarzane w kółko, np. `Muzeum Narodowe w Warszawie`. `0` wyłącza.

Praktycznie:

- Jeśli model odpływa w losowe tematy, spróbuj `Temp 0.65-0.70`, `Top-p 0.85-0.90`, `Top-k 30-40`.
- Jeśli model się zapętla, zmniejsz `Tokeny`, zostaw `N-gram 4` albo ustaw `Rep 1.12-1.15`.
- Jeśli odpowiedzi są nudne i zbyt podobne, spróbuj `Temp 0.85` albo `Top-p 0.95`.

## Limity

Żeby dashboard nie stał się publicznym botem/API:

```text
Prompt: maks. 500 znaków
Generacja: maks. 80 tokenów
Równolegle: 1 generacja naraz
Per przeglądarka: 6 generacji / 30 min
Per IP: 12 generacji / 1 h
Globalnie: 40 generacji / 1 h
Timeout: 120 s
CPU: niski priorytet, 1 wątek CPU
```

Limit `per przeglądarka` korzysta z lokalnego identyfikatora w `localStorage`, więc jest to ochrona przed przypadkowym spamem, nie kryptograficzna autoryzacja.

## Gemma eval

Automatyczne testy Gemmą są uruchamiane wyłącznie w nocy, w oknie 01:00-05:00 Europe/Warsaw. Ręczne uruchomienie testu Gemmy wymaga kodu właściciela. Nie udostępniaj kodu osobom, które mają tylko oglądać statystyki i promptować Glyph-27M.

## Jak interpretować odpowiedzi

Ten model jest jeszcze w treningu bazowym. Przy około 40% planu umie często zacząć po polsku, ale nadal traci kontekst, powtarza frazy i przechodzi w losowe domeny. Lepsze odpowiedzi nie oznaczają jeszcze, że model potrafi stabilnie odpowiadać jak chatbot.
