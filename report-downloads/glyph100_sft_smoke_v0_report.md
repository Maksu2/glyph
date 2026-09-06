# Glyph-100M SFT smoke v0 dataset report

## Summary

- examples: 1500
- avg instruction words: 8.74
- avg response words: 10.66
- max template tokens: 65
- over context 512: 0
- duplicate instructions extra: 0
- duplicate instruction+response extra: 0

## Categories

- anty_petle: 150
- brak_danych: 150
- codzienne_proste_pytania: 150
- krotkie_definicje: 150
- krotkie_poprawki_tekstu: 150
- mini_streszczenia: 150
- mvp_first_project_advice: 150
- naturalne_zakonczenia: 150
- ostrozne_odpowiedzi_przy_niepewnosci: 150
- proste_techniczne_wyjasnienia: 150

## Suspicious Phrases

- `w latach 1975-1998`: 0
- `w latach 1975–1998`: 0
- `gminie`: 0
- `powiecie`: 0
- `strona główna`: 0
- `cookies`: 0
- `kup teraz`: 0
- `dodaj do koszyka`: 0
- `zaloguj`: 0
- `zarejestruj`: 0
- `polityka prywatności`: 0
- `jako model językowy`: 0
- `jako sztuczna inteligencja`: 0

## Examples Per Category

### anty_petle

- prompt: Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Jednym zdaniem.
  response: Loss pokazuje, czy model uczy się przewidywać dane treningowe lub walidacyjne.
- prompt: Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?
  response: Nie. Lepsza jest krótka, konkretna odpowiedź niż długi tekst bez treści.
- prompt: Zakończ odpowiedź po drugim zdaniu: czym jest tokenizer? Tylko sedno.
  response: Tokenizer dzieli tekst na tokeny. Dzięki temu model może pracować na liczbach zamiast bezpośrednio na znakach.

### brak_danych

- prompt: Czy powinienem to kupić? Podaj uczciwą odpowiedź.
  response: Brakuje informacji o produkcie, cenie, stanie i twoich potrzebach. Bez tego można tylko zgadywać.
- prompt: Czy mam za mało RAM-u? Wskaż brakujące informacje.
  response: Trzeba znać użycie pamięci pod obciążeniem. Sam rozmiar RAM-u nie mówi, czy jest problem.
- prompt: Czy powinienem to kupić? Jak odpowiedzieć bez danych?
  response: Brakuje informacji o produkcie, cenie, stanie i twoich potrzebach. Bez tego można tylko zgadywać.

### codzienne_proste_pytania

- prompt: Co zrobić, gdy wynik mnie zaskakuje? Odpowiedz krótko.
  response: Sprawdź dane wejściowe, metodę pomiaru i powtórz test w tych samych warunkach.
- prompt: Jak dbać o jakość danych? Jednym akapitem.
  response: Zbieraj źródła, usuwaj duplikaty i sprawdzaj losowe próbki.
- prompt: Co zrobić, gdy odpowiedź jest zbyt długa? Odpowiedz krótko.
  response: Usuń powtórzenia i zostaw tylko informacje potrzebne do decyzji.

### krotkie_definicje

- prompt: Podaj prostą definicję: wersjonowanie.
  response: Wersjonowanie pozwala śledzić zmiany i wracać do wcześniejszych stanów projektu.
- prompt: Co oznacza termin „interfejs”?
  response: Interfejs to sposób komunikacji użytkownika albo programu z systemem.
- prompt: Podaj prostą definicję: latencja.
  response: Latencja to czas oczekiwania na odpowiedź systemu.

### krotkie_poprawki_tekstu

- prompt: Popraw tekst: Projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.
  response: Projekt jest ciekawy, ale ma zbyt szeroki zakres na start.
- prompt: Usuń lanie wody: Warto byłoby dokonać porównania kilku wariantów.
  response: Warto porównać kilka wariantów.
- prompt: Napisz naturalniej: Aplikacja nie posiada jeszcze pełnej funkcjonalności.
  response: Aplikacja nie ma jeszcze wszystkich funkcji.

### mini_streszczenia

- prompt: Streść w jednym zdaniu: Częste checkpointy pomagają przy ryzyku awarii, ale zajmują dużo miejsca.
  response: Checkpointy zwiększają bezpieczeństwo kosztem miejsca.
- prompt: Skróć tekst: Dobre metryki muszą być czytane razem z próbkami jakościowymi.
  response: Metryki i próbki powinny być analizowane razem.
- prompt: Wyciągnij najważniejszą myśl: Model bazowy kontynuuje tekst, więc nie należy oceniać go jak asystenta po instrukcyjnym tuningu.
  response: Model bazowy ocenia się jako generator kontynuacji.

### mvp_first_project_advice

- prompt: Co zrobić, gdy pomysł nie działa?
  response: Nazwij konkretny problem i sprawdź, czy da się uprościć założenia. Jeśli nie, warto zmienić kierunek wcześnie.
- prompt: Mam dużo pomysłów i nie wiem od czego zacząć.
  response: Wybierz jeden mierzalny cel na najbliższy etap. Po jego wykonaniu łatwiej zdecydować, co ma sens dalej.
- prompt: Jak zrobić projekt portfolio?
  response: Pokaż działający efekt, decyzje techniczne, ograniczenia i wnioski. To jest cenniejsze niż lista technologii.

### naturalne_zakonczenia

- prompt: Zakończ naturalnie: czym jest prototyp? Bez listy.
  response: Prototyp to wczesna wersja rozwiązania używana do sprawdzenia, czy pomysł ma sens.
- prompt: Napisz krótko, dlaczego warto robić backup. Zakończ po sensownej myśli.
  response: Backup chroni przed utratą danych po awarii, błędzie lub przypadkowym usunięciu.
- prompt: Napisz prostą odpowiedź: czy wynik loss wystarczy do oceny modelu? Jednym akapitem.
  response: Nie. Loss trzeba połączyć z próbkami generacji i ewaluacją jakościową.

### ostrozne_odpowiedzi_przy_niepewnosci

- prompt: Czy ta diagnoza jest pewna? Wskaż ograniczenie.
  response: Nie. Bez pełnych danych można mówić tylko o najbardziej prawdopodobnym wyjaśnieniu.
- prompt: Czy większy model zawsze daje lepszy wynik? Bez przesadnej pewności.
  response: Nie. Większy model nadal zależy od jakości danych, treningu i sposobu ewaluacji.
- prompt: Czy jedna metryka wystarczy? Krótko.
  response: Rzadko. Lepiej użyć kilku metryk i sprawdzić przykłady ręcznie.

### proste_techniczne_wyjasnienia

- prompt: Co robi repetition penalty?
  response: Repetition penalty zmniejsza szansę powtarzania tych samych tokenów lub fraz.
- prompt: Po co mierzy się temperaturę GPU?
  response: Temperatura GPU pomaga ocenić, czy obciążenie jest bezpieczne i stabilne.
- prompt: W jednym akapicie: Czym jest scheduler learning rate?
  response: Scheduler zmienia learning rate w czasie, na przykład po rozgrzewce stopniowo go zmniejsza.
