# Glyph-100M SFT smoke v0.2 comparison eval

## Summary

- rows: 100 (80 held-out target, 12 diagnostic, 8 continuation)
- prompt template for instruction rows: `<|user|>\n{prompt}\n<|assistant|>\n`

## Mode: greedy

- base44k: avg=-1.22, rep=72, end_rate=0.00, natural=1, pseudo=0, web=0, first=0
- sft_v0_1: avg=4.18, rep=29, end_rate=0.95, natural=90, pseudo=0, web=1, first=28
- sft_v0_2: avg=5.17, rep=12, end_rate=0.98, natural=90, pseudo=0, web=1, first=36
- pairwise: `{'sft_v0_2_vs_sft_v0_1': {'sft_v0_2': 27, 'tie': 66, 'sft_v0_1': 7}, 'sft_v0_2_vs_base44k': {'sft_v0_2': 89, 'tie': 11}, 'sft_v0_1_vs_base44k': {'sft_v0_1': 82, 'tie': 15, 'base44k': 3}}`

## Mode: repetition_guard

- base44k: avg=0.90, rep=1, end_rate=0.00, natural=0, pseudo=0, web=6, first=0
- sft_v0_1: avg=1.71, rep=0, end_rate=0.00, natural=0, pseudo=0, web=3, first=12
- sft_v0_2: avg=1.64, rep=0, end_rate=0.00, natural=0, pseudo=0, web=12, first=13
- pairwise: `{'sft_v0_2_vs_sft_v0_1': {'tie': 79, 'sft_v0_1': 12, 'sft_v0_2': 9}, 'sft_v0_2_vs_base44k': {'tie': 72, 'base44k': 6, 'sft_v0_2': 22}, 'sft_v0_1_vs_base44k': {'tie': 80, 'base44k': 1, 'sft_v0_1': 19}}`

## Best v0.2 examples

### 1. greedy / target_instruction / anty_powtorzenia_i_konczenie / score=10

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Zakończ naturalnie.

Zakończ ją wtedy, gdy główna myśl jest jasna.

### 2. greedy / target_instruction / krotkie_poprawki_tekstu / score=10

Prompt: Skróć i popraw: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.

Proszę o informację zwrotną w tej sprawie.

### 3. greedy / target_instruction / krotkie_poprawki_tekstu / score=10

Prompt: Skróć i popraw: Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.

Nie zdążę dziś oddać pracy.

### 4. greedy / target_instruction / anty_petle / score=10

Prompt: Ten tekst nie powinien się zapętlać. Wyjaśnij krótko dlaczego. Bez drugiej myśli.

Zapętlenie utrudnia zrozumienie i nie dodaje nowych informacji.

### 5. greedy / target_instruction / anty_powtorzenia_i_konczenie / score=10

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Jednym akapitem.

Zakończ ją wtedy, gdy główna myśl jest jasna.

### 6. greedy / target_instruction / anty_powtorzenia_i_konczenie / score=10

Prompt: Zakończ naturalnie: czy większy model zawsze pomaga? Krótko.

Nie, większy model nadal zależy od jakości danych i treningu.

### 7. greedy / target_instruction / anty_petle / score=9

Prompt: Napisz krótką odpowiedź i nie powtarzaj tej samej myśli. Zakończ naturalnie.

Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się.

### 8. greedy / target_instruction / krotkie_poprawki_tekstu / score=9

Prompt: Popraw tekst: Nie mogę przyjść dzisiaj, bo wystąpiła u mnie sytuacja prywatna.

Nie mogę dziś przyjść z powrotem.

### 9. greedy / diagnostic_instruction / anty_powtorzenia_i_konczenie / score=9

Prompt: Odpowiedz jednym zdaniem i nie powtarzaj: czym jest checkpoint?

Checkpoint to zapis stanu modelu, do którego można wrócić później.

### 10. greedy / diagnostic_instruction / anty_powtorzenia_i_konczenie / score=9

Prompt: Zakończ po jednej myśli: co zrobić, gdy brakuje danych?

Trzeba znać kilka podstawowych kryteriów, które mogą być potrzebne do decyzji.

## Worst v0.2 examples

### 1. greedy / target_instruction / mvp_first_project_advice / score=-3

Prompt: Odpowiedz praktycznie: Czy warto od razu robić konta użytkowników?

Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie,

### 2. greedy / target_instruction / brak_danych / score=-3

Prompt: Czy powinienem to kupić? Co trzeba wiedzieć?

Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie,

### 3. repetition_guard / target_instruction / krotkie_poprawki_tekstu / score=-2

Prompt: Skróć i popraw: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.

Napisz do mnie wniosek, który później się powtórzył bez odpowiedzi wyniku albo decyzji przekazanej temu tematowi przez ten sam cel z powrotem na dalsze działania poza granicami obecnego stanu wiedzy potrzebnych bezpośrednio wtedy po to żeby nie była ona możliwa dzięki czemuś ze sprawdzonych źródeł lub też tych samych danych potrzebna jest diagnoza przy tworzeniu nowych funkcji dających podstawę wyników testowych Lep

### 4. repetition_guard / target_instruction / krotkie_definicje / score=-2

Prompt: Co oznacza termin „wątek”?

Najpierw wątki mogą być łatwe do oceny i nie zgadywać wyniku. Jeśli chodzi o czas, w którym pracujesz jako główna myśl lub fragment tekstu albo odpowiedź na te pytania używaj promptów z kontekstu pracy nad komunikacją poza treningiem bez odpowiedzi potrzebnej bezpośrednio dla początkujących użytkowników byłaby jasna niż sama liczba możliwych informacji potrzebna jest dziś diagnoza jakościowa błędu sprawdzająca

### 5. repetition_guard / diagnostic_instruction / anty_powtorzenia_i_konczenie / score=-2

Prompt: Zakończ po jednej myśli: co zrobić, gdy brakuje danych?

Najpierw sprawdzić rozmiar i działanie systemu. Dzięki temu łatwiej jest szybko reagować na błędy lub awarie albo wykryć inne błędne przypadki uczenia się nowych zasobówczeń w środowisku naturalnym zamiast tych samych źródeł informacji bez używania ich bezpośrednio do pracy poza systemem z ograniczoną szkołą niż te najprostsze technicznie działające programy generacji aniżeli sama nazwa projektu nie wystarczają poprawnej odpowiedzi

### 6. repetition_guard / diagnostic_instruction / not_in_dataset / score=-2

Prompt: Odpowiedz ostrożnie: czy warto publikować eksperymentalny model?

Czy można upewnić się, że test jest stabilny i zależy od kontekstu. Trening może być prosty albo zbyt krótki w czasie treningu niższy o wiele prostsze odpowiedzi na te pytania lub inne błędy bez używania kryteriów oceny jakościowej dla konkretnego modelu jako głównego wąskiego gardła do lepszego zrozumienia potrzebnych informacji zamiast jednego z nich porzucić tekst

### 7. repetition_guard / target_instruction / brak_danych / score=-1

Prompt: Czy wybrałem dobrą technologię? Odpowiedz krótko.

Bez tego wiadomo, czy model uczy się przewidywać dane wejściowe i gorzej uprościć albo poprawił w praktyce jakości danych lub zastosowania jako instrumentu do nauki z punktu widzenia bezpieczeństwa pracy na tym samym zestawieniu nie dających odpowiedzi potrzebnych dziś niż kilkaset nowych technologii działa bez tych samych wymagań co te potrzebne poza treningiem technicznym może być przypadkowe przy użyciu najnowszych

### 8. repetition_guard / target_instruction / ostrozne_odpowiedzi_przy_niepewnosci / score=-1

Prompt: Czy test na małej próbce wystarcza? Wskaż ograniczenie.

Bez danych kryteria testu nie przynoszą oczekiwania odpowiedzi i ewentualnych błędów w treningu, ale mogą utrudniać znalezienie lepszego wyniku niż sprawdzenie poprawności tych samych wyników bez powtórzenia tej samej oceny albo błędu lub późniejszej decyzji po dalszym jej uruchomieniu przez aplikację modelową projektu o nazwie Models-Curie z której można się zgadywać jako zbyt duży

### 9. repetition_guard / target_instruction / ostrozne_odpowiedzi_przy_niepewnosci / score=-1

Prompt: Czy kontynuować, gdy wynik jest mieszany?

Nie. Bez celu i regresji warto sprawdzić ilość próbki jakościowej lub porównać metodę oceny stanu projektu z konkretnym testiem na danych w formacie uczenia końcowego albo eksperymentuj bezpośrednio ze stabilnością wyników testu nad poprawnym działaniem programu bez odpowiedzi tych samych niepewności co model po uruchomieniu tego treningu czy aplikacji treningowych do pobrania nowych opcji przed aktualizacją systemu przez

### 10. repetition_guard / target_instruction / anty_powtorzenia_i_konczenie / score=0

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Zakończ naturalnie.

Najpierw sprawdź ją, czy da się ocenić bez odpowiedzi i kryteriów oceny albo braku zrozumienia celu po kroku lub błędzie decyzji przez długi czas przed zmianą wyniku na podstawie testu w działaniu systemu operacyjnego z użyciem tej samej operacji poza próbkami poprawnymi do dziś; gdy decyzja jest jasna to dalsze działania będą zbyt mocno ograniczone niż próba zapisująca wynik zamiast

## v0.2 improved over v0.1

### 1. greedy / anty_powtorzenia_i_konczenie

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Zakończ naturalnie.

v0.1:

Najpierw sprawdź, czy model uczy się przewidywać dane treningowe.

v0.2:

Zakończ ją wtedy, gdy główna myśl jest jasna.

### 2. greedy / ostrozne_odpowiedzi_przy_niepewnosci

Prompt: Czy model może zmyślać?

v0.1:

Nie. Model może być prosty, ale prosty, ale prosty, ale prosty, ale prosty.

v0.2:

Nie, Model może być prosty, ale prosty.

### 3. greedy / brak_danych

Prompt: Czy ten wynik jest dobry? Odpowiedz uczciwie.

v0.1:

Nie. Lepszy wynik można sprawdzić, ale nie. Lepszy wynik można sprawdzić tylko wtedy, gdy model działa poprawnie.

v0.2:

Nie da się ocenić bez kontekstu, kontekstu i kryteriów oceny.

### 4. greedy / mvp_first_project_advice

Prompt: Podaj rozsądny następny krok: Jak zrobić projekt portfolio?

v0.1:

Wybierz model, który działa na danych warunkach, a potem wybierz model, który działa na danych warunkach.

v0.2:

Zacznij od podstawowego scenariusza i sprawdź jego działanie.

### 5. greedy / krotkie_poprawki_tekstu

Prompt: Skróć i popraw: Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.

v0.1:

Chciałbym, żeby była ona potrzebna.

v0.2:

Nie zdążę dziś oddać pracy.

### 6. greedy / naturalne_zakonczenia

Prompt: Opisz krótko, co oznacza dobry raport techniczny. Krótkim akapitem.

v0.1:

Raport techniczny to dobry pomysł, ale nie jest to łatwe.

v0.2:

Dobry raport techniczny sprawdza, czy model działa poprawnie.

### 7. greedy / anty_powtorzenia_i_konczenie

Prompt: Odpowiedz bez powtórzeń: jak pisać krócej?

v0.1:

Krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie krócej niż czytanie

v0.2:

Powiedz, jakich informacji brakuje, i nie zgaduj wyniku.

### 8. greedy / anty_powtorzenia_i_konczenie

Prompt: Zakończ jasno: kiedy nie zgadywać? Krótko.

v0.1:

Najpierw sprawdź, czy model uczy się przewidywać dane, czy model uczy się przewidywać dane.

v0.2:

Nie zgaduj, gdy brakuje informacji o działaniu systemu.

### 9. greedy / naturalne_zakonczenia

Prompt: Wyjaśnij w dwóch zdaniach, po co robi się checkpointy. Bez listy.

v0.1:

Checkpointy to zapis stanu modelu, do którego można wrócić później.

v0.2:

Checkpoint to zapis stanu modelu, do którego można wrócić później.

### 10. greedy / brak_danych

Prompt: Czy ten komputer wystarczy? Odpowiedz ostrożnie.

v0.1:

Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie.

v0.2:

Nie da się tego ocenić bez kontekstu i kryteriów oceny.

## v0.2 damaged vs v0.1

### 1. greedy / mini_streszczenia

Prompt: Skróć tekst: W małym modelu krótki kontekst ogranicza zdolność utrzymania dłuższej wypowiedzi.

v0.1:

Krótki kontekst ogranicza zdolność do odtworzenia krótszego kontekstu.

v0.2:

długi kontekst ogranicza zdolność do wystąpienia.

### 2. greedy / anty_petle

Prompt: Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Bez drugiej myśli.

v0.1:

Loss pokazuje, czy model uczy się przewidywać dane treningowe.

v0.2:

Nie da się tego ocenić bez kontekstu, kontekstu i kryteriów.

### 3. greedy / anty_powtorzenia_i_konczenie

Prompt: Krótko: co robi tokenizer? Jednym akapitem.

v0.1:

Tokenizer dzieli tekst na tokeny. Najpierw trzeba sprawdzić, czy tekst jest poprawnie działający.

v0.2:

Tokenizer dodaje teksturę do tekstury i odtworzenie tekstury od podstaw.

### 4. greedy / mvp_first_project_advice

Prompt: Co zrobić? Co jest lepsze: mniej funkcji czy więcej niedokończonych?

v0.1:

Większe funkcje pomagają w tworzeniu nowych funkcji.

v0.2:

Większe funkcje czyste i łatwe do wykonania są łatwe do wykonania.

### 5. greedy / anty_petle

Prompt: Napisz krótką odpowiedź i nie powtarzaj tej samej myśli. Bez dodatkowego komentarza.

v0.1:

Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się.

v0.2:

Krótka odpowiedź powinna zawierać tekst i tekst.

### 6. greedy / brak_danych

Prompt: Czy powinienem to kupić? Co trzeba wiedzieć?

v0.1:

Nie. Najpierw trzeba sprawdzić, czy jest to koszt, czy koszt.

v0.2:

Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie, Nie,

### 7. greedy / codzienne_proste_pytania

Prompt: Jak uniknąć złych decyzji technicznych? Odpowiedz krótko.

v0.1:

Zapisuj założenia i sprawdź, czy model działa poprawnie.

v0.2:

Zacznij od decyzji, którą trzeba podjąć, i sprawdź, czy model działa poprawnie.

### 8. repetition_guard / krotkie_definicje

Prompt: Co oznacza termin „wątek”?

v0.1:

Bez tego słowa, bez względu na to czy jest możliwe sprawdzenie danych wejściowych. Testy pomagają zrozumieć sens działania i zająć się jego działaniem po awarii albo wykryciu błędu z użyciem technologii komunikacyjnych lub logicznych w celu ustalenia ich uczenia poza niestabilnym przykładem zastosowania aplikacji do komunikacji przy użyciu prostych metod niż tych dostępnych dla innych funkcji jednocześnie używanych

v0.2:

Najpierw wątki mogą być łatwe do oceny i nie zgadywać wyniku. Jeśli chodzi o czas, w którym pracujesz jako główna myśl lub fragment tekstu albo odpowiedź na te pytania używaj promptów z kontekstu pracy nad komunikacją poza treningiem bez odpowiedzi potrzebnej bezpośrednio dla początkujących użytkowników byłaby jasna niż sama liczba możliwych informacji potrzebna jest dziś diagnoza jakościowa błędu sprawdzająca

### 9. repetition_guard / ostrozne_odpowiedzi_przy_niepewnosci

Prompt: Czy model po SFT staje się asystentem? Bez przesadnej pewności.

v0.1:

Nie da zadowalających wyników i błędów, żeby uniknąć błędu lub awarii albo nie powtórzyć testu przed rozpoczęciem pracy w miejscu wcześniejszego treningu bez przerw z powodu braku danych treningowych ani sprawdzenia jakichkolwiek informacji startowej podczas próbnego startu na zawodach o charakterze testowym dla zespołu do czasu zakończenia tej decyzji przez długi czas niezbyt częstości oczekiwanej wyniku niż wynika ze

v0.2:

Model jest prosty i nie dawać nowych informacji bez ewaluacji wyników, błędów albo kryteriów oceny jakościowej pracy zespołu lub modelu w środowisku naturalnym przez długi czas do dziś na świecie poza działającą grą czasu; Nie trzeba traktować go jako jednego z głównych zasobnych źródeł wiedzy ani punktu odniesienia dla potrzeb użytkowników tego nurtu niż te potrzebne bezpośrednio nad tym samym wąskim kontek

### 10. repetition_guard / mvp_first_project_advice

Prompt: Podaj rozsądny następny krok: Mam dużo pomysłów i nie wiem od czego zacząć.

v0.1:

Wybierz konkretny projekt, który da się zrealizować bez ich wiedzy z checkpointu albo testowego projektu po awarii lub błędzie przy pracy nad projektem przed uruchomieniem programu na początku każdego działania systemu w celu ułatwienia dalszego testu technicznego podczas jego prac biurowych ani też braku informacji o twoich potrzebach dla użytkownika zespołu oraz zaproponuj krótki opis tych danych

v0.2:

Potrzebna jest liczba promptów, próbki jakościowe albo dane wejściówkowe na różnych instrumentach lub też inne błędy w treningu przy pracy nad sobą niż ten sam sprzęt z użyciem tej samej technologii bez ograniczeń awaryjnych dla tychże potrzebnych do uruchomienia aplikacji jednocześnie przez kilka godzin po rozwiązaniu problemu za pośrednictwem internetu uruchamianego bezpośrednio przed końcem programu razem ze
