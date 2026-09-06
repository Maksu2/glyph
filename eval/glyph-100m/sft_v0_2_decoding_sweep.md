# Glyph-100M SFT v0.2 decoding sweep

## Summary

- rows: `150`
- checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt`
- best mode: `no_repeat_ngram_size_3`

## Modes

- greedy: avg `5.55`, median `6.00`, rep `17`, end_rate `0.98`, natural `139`, web `4`, first `57`, avg_tokens `80.0`
- greedy_repetition_penalty_1_1: avg `1.90`, median `1.00`, rep `0`, end_rate `0.00`, natural `0`, web `20`, first `26`, avg_tokens `80.0`
- greedy_repetition_penalty_1_2: avg `1.90`, median `1.00`, rep `0`, end_rate `0.00`, natural `0`, web `20`, first `26`, avg_tokens `80.0`
- topk40_temp07: avg `5.37`, median `5.50`, rep `17`, end_rate `0.99`, natural `140`, web `4`, first `53`, avg_tokens `80.0`
- topk40_temp07_repetition_penalty_1_1: avg `1.55`, median `1.00`, rep `0`, end_rate `0.00`, natural `1`, web `23`, first `20`, avg_tokens `80.0`
- topk40_temp08_repetition_penalty_1_15: avg `1.39`, median `1.00`, rep `0`, end_rate `0.00`, natural `0`, web `28`, first `19`, avg_tokens `80.0`
- no_repeat_ngram_size_3: avg `5.38`, median `4.00`, rep `1`, end_rate `1.00`, natural `142`, web `4`, first `43`, avg_tokens `80.0`
- no_repeat_ngram_size_4: avg `5.20`, median `4.00`, rep `6`, end_rate `1.00`, natural `142`, web `8`, first `44`, avg_tokens `80.0`

## Best 10 per sweep

### 1. greedy · anty_powtorzenia_i_konczenie · score=10

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Zakończ naturalnie.

Zakończ ją wtedy, gdy główna myśl jest jasna.

### 2. greedy · krotkie_poprawki_tekstu · score=10

Prompt: Skróć i popraw: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.

Proszę o informację zwrotną w tej sprawie.

### 3. greedy · krotkie_poprawki_tekstu · score=10

Prompt: Skróć i popraw: Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.

Nie zdążę dziś oddać pracy.

### 4. greedy · anty_petle · score=10

Prompt: Ten tekst nie powinien się zapętlać. Wyjaśnij krótko dlaczego. Bez drugiej myśli.

Zapętlenie utrudnia zrozumienie i nie dodaje nowych informacji.

### 5. greedy · anty_powtorzenia_i_konczenie · score=10

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Jednym akapitem.

Zakończ ją wtedy, gdy główna myśl jest jasna.

### 6. greedy · anty_powtorzenia_i_konczenie · score=10

Prompt: Zakończ naturalnie: czy większy model zawsze pomaga? Krótko.

Nie, większy model nadal zależy od jakości danych i treningu.

### 7. greedy · krotkie_poprawki_tekstu · score=10

Prompt: Przeredaguj zdanie: Należy dokonać sprawdzenia poprawności działania programu.

Trzeba sprawdzić, czy program działa poprawnie.

### 8. greedy · anty_petle · score=10

Prompt: Jedna myśl, bez listy: kiedy projekt jest za duży? Nie rozwijaj dalej.

Projekt jest za duży, gdy nie da się szybko pokazać jego głównej wartości.

### 9. greedy · anty_powtorzenia_i_konczenie · score=10

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Nie zaczynaj nowego tematu.

Zakończ ją wtedy, gdy główna myśl jest jasna.

### 10. topk40_temp07 · anty_powtorzenia_i_konczenie · score=10

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Zakończ naturalnie.

Zakończ ją wtedy, gdy główna myśl jest jasna.


## Worst 10 per sweep

### 1. greedy · mvp_first_project_advice · score=-3

Prompt: Odpowiedz praktycznie: Czy warto od razu robić konta użytkowników?

Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie,

### 2. greedy · brak_danych · score=-3

Prompt: Czy powinienem to kupić? Co trzeba wiedzieć?

Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie,

### 3. greedy_repetition_penalty_1_1 · anty_powtorzenia_i_konczenie · score=-2

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Zakończ naturalnie.

Najpierw sprawdź, czy model działa poprawnie i nie zgadywać wyniku po decyzji o dalszym locie albo błędzie w odpowiedzi na te pytania lub błędy podczas pracy nad projektem z użyciem promptów zamiast próbki jakościowej do oceny celu projektu bez kontekstu kryteriów bezpieczeństwa ani punktu odniesienia dla konkretnych potrzebnych zasobności danych; jeśli projekt jest stabilny to warto sprawdzić

### 4. greedy_repetition_penalty_1_1 · krotkie_poprawki_tekstu · score=-2

Prompt: Skróć i popraw: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.

Trzeba wskazane informacje potrzebne do ustalenia decyzji, oceny albo potwierdzenia tych samych danych bez odpowiedzi wynikuowej lub błędu z użyciem tego kryteriuzującego testu na podstawie wyników pomiarów celu po awarii systemu przez długi czas czasu nie wiadomo czy da się ocenić przyczynę wypadku? Sama odpowiedź powinna zawierała informację krótkookreślaną jako próbę wyjaśnienia przyczyn wystąpienia zdarzenia oraz

### 5. greedy_repetition_penalty_1_1 · mvp_first_project_advice · score=-2

Prompt: Podaj rozsądny następny krok: Mam dużo pomysłów i nie wiem od czego zacząć.

Najpierw sprawdź, czy model działa poprawnie bez kontekstu albo braku odpowiedzi na te pytania lub zgadywania w celu rozwiązania problemu z problemami zdrowotnymi? Nie mogę dziś tego powtarzać jako odpowiedź błędna dla mnie samych wtedy gdy mam problem ze znalezieniem nowych rozwiązań do oceny ryzyka uczenia się przez długi czas czasu po treningu niższym szczególe decyzji o dalszej diagnozie tych danych osobowych

### 6. greedy_repetition_penalty_1_1 · naturalne_zakonczenia · score=-2

Prompt: Wyjaśnij, dlaczego nie warto powtarzać tej samej frazy. Bez listy.

Nie trzeba znać celu i czasu odpowiedzi na te pytania albo poprosić o odpowiedź poprawnie działającą myślową decyzję lub zaproszenie do dalszego treningu w zespole niższym szczegółu wiedzy technicznej z punktu widzenia bezpieczeństwa pracy zespołu oraz sposobu wykonania tych samych zadań bez konieczności odtworzenia ich po awarii systemu przez długi czas trwania projektu jako jednego ze sprawdzonych źródeł ryzyka...

### 7. greedy_repetition_penalty_1_1 · brak_danych · score=-2

Prompt: Czy wynik evala jest wiarygodny? Krótko.

Nie da się ocenić bez kontekstu, kryteriów i odpowiedzi na te pytania albo nie zgadywać wyniku w konkretnym momencie lub czasie po decyzji o tym samym zestawieniu problemu z danym razem przez użytkownika błędem czy przypadkowym potwierdzeniu tych samych wyników poza działaniem projektu jako całościowego źródła informacji potrzebnej do wykonania zapisu danych wejściowych ani też brakujących źródeł wiedzy techniczne...

### 8. greedy_repetition_penalty_1_1 · anty_powtorzenia_i_konczenie · score=-2

Prompt: Jedno zdanie: dlaczego powtórzenia są problemem? Jednym akapitem.

Zacznij od odpowiedzi i zostaw tylko informację potrzebną do decyzji, którą trzeba podjąć po sprawdzeniu poprawności albo pomyłce z dalszym krokiem w celu rozwiązania problemu bez podstawowego wniosku o błędzie lub niepewność wyniku niż przewidywania testu przed podjęciem tej samej pracy przez czytelnika jako głównego kryteria oceny jakościowej projektu na podstawie wyników analizowanych wcześniej danych wejściowych

### 9. greedy_repetition_penalty_1_1 · naturalne_zakonczenia · score=-2

Prompt: Odpowiedz spokojnie: projekt nie działa, co teraz?

Projekt jest gotowy i wymaga od projektu decyzji o dalszym locie. Najpierw trzeba wskazać plan działania albo decyzję w celu wykonania scenariusza lub fragmentu tekstu bez kontekstu odpowiedzi na te pytania; model może być prosty do nauki z użyciem promptów zamiast jednego punktu startowego po awarii systemu operacyjnego Windows jako głównej funkcji programu dla potrzeb użytkownika końcowej generacji aplikacji biu...

### 10. greedy_repetition_penalty_1_1 · not_in_dataset · score=-2

Prompt: Czy krótsza odpowiedź zawsze jest lepsza?

Nie, krótka odpowiedzi nie wystarcza. Sama nazwa to zapis stanu modelu i jakości danych w środowisku naturalnym albo też poza danymi generacji niższego ryzyka dla bezpieczeństwa pracy lub nauki na tym samym poziomie wiedzy o świecie realnym czy problemie technicznym z punktu widzenia technologii bez używania tych samych informacji do dalszych testów przed uruchomieniem projektu przez długi czas czasu byłaby zbyt w...
