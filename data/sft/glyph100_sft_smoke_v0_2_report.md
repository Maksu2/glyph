# Glyph-100M SFT smoke v0.2 dataset report

## Summary

- examples: 2176
- split train/val/test: {'train': 1846, 'val': 218, 'test': 112}
- max template tokens: 76
- over context 512: 0
- duplicate pair extra: 0
- near duplicate examples: 50
- `<|end|>` supervised sanity: {'checked_examples': 100, 'end_token_as_last_predictable_token': 100, 'end_token_id': 6}

## Categories

- anty_petle: 150
- anty_powtorzenia_i_konczenie: 360
- brak_danych: 270
- codzienne_proste_pytania: 150
- krotkie_definicje: 214
- krotkie_poprawki_tekstu: 186
- mini_streszczenia: 150
- mvp_first_project_advice: 150
- naturalne_zakonczenia: 246
- ostrozne_odpowiedzi_przy_niepewnosci: 150
- proste_techniczne_wyjasnienia: 150

## First Response Words

- `Nie`: 155
- `Nie,`: 75
- `Trzeba`: 75
- `Checkpoint`: 46
- `Walidacja`: 44
- `Bez`: 42
- `Backup`: 41
- `Model`: 39
- `Najpierw`: 36
- `Tokenizer`: 36
- `Smoke`: 34
- `Brakuje`: 32
- `Wybierz`: 30
- `Raport`: 28
- `Zacznij`: 27
- `To`: 25
- `Usuń`: 22
- `Potrzebny`: 22
- `Potrzebne`: 22
- `Log`: 22
- `Sprawdź`: 22
- `Ten`: 21
- `Odpowiedź`: 21
- `Projekt`: 20
- `Raczej`: 20
- `Na`: 18
- `Powiedz,`: 17
- `SFT`: 17
- `Loss`: 17
- `Zakończ`: 17

## Top Response 4-grams

- `nie da się tego`: 37
- `backup to kopia danych`: 31
- `to kopia danych potrzebna`: 27
- `kopia danych potrzebna do`: 27
- `danych potrzebna do odtworzenia`: 27
- `potrzebna do odtworzenia ich`: 27
- `do odtworzenia ich po`: 27
- `odtworzenia ich po awarii`: 27
- `checkpoint to zapis stanu`: 26
- `to zapis stanu modelu`: 26
- `potrzebny jest model cena`: 24
- `zapis stanu modelu do`: 22
- `stanu modelu do którego`: 22
- `modelu do którego można`: 22
- `do którego można wrócić`: 22
- `którego można wrócić później`: 22
- `raport zapisuje wynik ustawienia`: 22
- `zapisuje wynik ustawienia i`: 22
- `da się tego ocenić`: 22
- `się tego ocenić bez`: 22
- `większy model nadal zależy`: 22
- `model nadal zależy od`: 22
- `nadal zależy od jakości`: 22
- `zależy od jakości danych`: 22
- `nie da się ocenić`: 20
- `da się ocenić bez`: 20
- `zmniejsza szansę powtarzania tych`: 17
- `szansę powtarzania tych samych`: 17
- `powtarzania tych samych tokenów`: 17
- `tych samych tokenów lub`: 17

## Suspicious Phrases

- `w latach 1975-1998`: 0
- `w latach 1975–1998`: 0
- `gminie`: 0
- `powiecie`: 0
- `województwie`: 0
- `strona główna`: 0
- `cookies`: 0
- `kup teraz`: 0
- `dodaj do koszyka`: 0
- `zaloguj`: 0
- `zarejestruj`: 0
- `polityka prywatności`: 0
- `jako model językowy`: 0
- `jako sztuczna inteligencja`: 0
- `kliknij`: 0

## Examples Per Category

### anty_petle

- prompt: Zakończ po jednej myśli: po co robi się testy? Bez dygresji.
  response: Testy pomagają wykrywać błędy i upewnić się, że zmiany nie psują działania.
- prompt: Napisz krótką odpowiedź i nie powtarzaj tej samej myśli. Bez listy.
  response: Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się, gdy ta myśl jest jasna.
- prompt: Odpowiedz krótko i zakończ naturalnie: czym jest backup? Bez drugiej myśli.
  response: Backup to kopia danych potrzebna do odtworzenia ich po awarii.
- prompt: Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Bez dygresji.
  response: Loss pokazuje, czy model uczy się przewidywać dane treningowe lub walidacyjne.

### anty_powtorzenia_i_konczenie

- prompt: Nie powtarzaj frazy: czy warto trenować dalej bez evala? Jednym akapitem.
  response: Nie warto, bo bez evala nie wiadomo, czy model faktycznie się poprawia.
- prompt: Nie rozwijaj dalej: po co jest zbiór walidacyjny? Krótko.
  response: Zbiór walidacyjny pokazuje, jak model działa poza danymi treningowymi.
- prompt: Bez pętli: co zrobić, gdy model powtarza tekst? Bez powtarzania.
  response: Zmierz skalę problemu, popraw dane i sprawdź ustawienia generacji.
- prompt: Odpowiedz jednym zdaniem i zakończ: co zrobić, gdy brakuje danych? Bez powtarzania.
  response: Powiedz, jakich danych brakuje, i nie zgaduj wyniku.

### brak_danych

- prompt: Czy ta konfiguracja jest optymalna? W jednym akapicie.
  response: Nie wiadomo bez obciążenia, celu i pomiarów. Najpierw trzeba sprawdzić realne metryki.
- prompt: Czy ten wynik jest dobry? Zakończ naturalnie.
  response: Brakuje punktu odniesienia i kryteriów oceny. Bez nich nie da się powiedzieć, czy wynik jest dobry.
- prompt: Czy moja odpowiedź jest dobra? Nie zgaduj.
  response: Nie da się ocenić bez treści odpowiedzi i kryteriów oceny.
- prompt: Czy ten komputer wystarczy? Co trzeba wiedzieć?
  response: To zależy od zastosowania. Podaj programy, budżet i wymagania, wtedy da się ocenić sensownie.

### codzienne_proste_pytania

- prompt: Jak wybrać temat projektu? Bez listy.
  response: Wybierz temat, który da się zrealizować w dostępnym czasie i który możesz pokazać działająco.
- prompt: Jak zaplanować naukę na jutro? Odpowiedz krótko.
  response: Wybierz dwa najważniejsze tematy i zaplanuj krótkie bloki pracy z przerwami.
- prompt: Co zrobić, gdy coś działa wolno? Jednym akapitem.
  response: Najpierw zmierz, co jest wąskim gardłem, zamiast zgadywać przyczynę.
- prompt: Jak powiedzieć, że nie mam czasu?
  response: Napisz krótko, że teraz nie możesz się tym zająć, i podaj możliwy termin.

### krotkie_definicje

- prompt: Co oznacza termin „checkpoint”?
  response: Checkpoint to zapis stanu modelu, z którego można wznowić trening albo uruchomić ewaluację.
- prompt: Wyjaśnij krótko pojęcie: algorytm.
  response: Algorytm to opis kolejnych kroków prowadzących do rozwiązania problemu.
- prompt: Podaj prostą definicję: hipoteza.
  response: Hipoteza to sprawdzalne przypuszczenie, które można potwierdzić albo odrzucić testem.
- prompt: Co oznacza termin „cache”?
  response: Cache to szybka pamięć podręczna używana po to, żeby nie liczyć lub pobierać tych samych danych ponownie.

### krotkie_poprawki_tekstu

- prompt: Skróć i popraw: Kod powinien zostać uporządkowany przed dalszym rozwojem.
  response: Przed dalszym rozwojem warto uporządkować kod.
- prompt: Przeredaguj zdanie: Dokonano wykonania testu działania systemu.
  response: Przetestowano działanie systemu.
- prompt: Skróć i popraw: Nie jest możliwe jednoznaczne stwierdzenie bez dodatkowych informacji.
  response: Bez dodatkowych informacji nie da się tego jednoznacznie stwierdzić.
- prompt: Usuń lanie wody: Wprowadzone zmiany mają na celu poprawę jakości wyników.
  response: Zmiany mają poprawić jakość wyników.

### mini_streszczenia

- prompt: Podaj krótkie streszczenie: Jeśli test zależy od losowego samplingu, trzeba sprawdzić kilka seedów.
  response: Kilka seedów pomaga odróżnić jakość od losowości.
- prompt: Skróć tekst: Niska temperatura może ograniczyć chaos, ale nie naprawi braku wiedzy ani złych danych.
  response: Decoding pomaga, ale nie zastępuje jakości danych.
- prompt: Streść w jednym zdaniu: Dashboard ma pomagać w decyzjach, a nie tylko pokazywać dużo liczb.
  response: Dashboard powinien wspierać decyzje.
- prompt: Streść w jednym zdaniu: Ewaluacja jakościowa nie jest idealna, ale pokazuje problemy niewidoczne w samym loss.
  response: Eval jakościowy uzupełnia loss.

### mvp_first_project_advice

- prompt: Krótko doradź: Czy warto zmieniać stack w połowie?
  response: Tylko przy konkretnym problemie. Sama ciekawość nowej technologii zwykle opóźnia projekt.
- prompt: Podaj rozsądny następny krok: Nie wiem, czy zacząć projekt od UI czy od logiki.
  response: Zacznij od logiki i jednego prostego przepływu. UI dopracuj wtedy, gdy wiadomo już, co naprawdę ma działać.
- prompt: Krótko doradź: Jak uniknąć utknięcia w projekcie?
  response: Ustal mały punkt kontrolny i sprawdź go szybko. Jeśli nie działa, zawęź zakres zamiast dokładać kolejne funkcje.
- prompt: Krótko doradź: Chcę dodać AI, bo projekt będzie wyglądał lepiej.
  response: Dodaj AI tylko wtedy, gdy rozwiązuje konkretny problem. Sama obecność AI nie poprawia projektu.

### naturalne_zakonczenia

- prompt: Opisz krótko, po co robi się smoke test SFT. Naturalnie.
  response: Smoke test SFT sprawdza, czy model reaguje na format instrukcji i czy trening jest stabilny. Nie jest jeszcze dowodem, że model nadaje się do użycia jako asystent.
- prompt: Wyjaśnij w dwóch zdaniach, po co robi się checkpointy. Bez powtórzeń.
  response: Checkpoint zapisuje stan modelu i optimizera w konkretnym momencie. Dzięki temu można wznowić trening albo wrócić do lepszego punktu.
- prompt: Odpowiedz bez lania wody: czym jest checkpoint? Odpowiedź ma być krótka.
  response: Checkpoint to zapis stanu modelu, do którego można wrócić później.
- prompt: Wyjaśnij w dwóch zdaniach, po co robi się checkpointy. Bez listy.
  response: Checkpoint zapisuje stan modelu i optimizera w konkretnym momencie. Dzięki temu można wznowić trening albo wrócić do lepszego punktu.

### ostrozne_odpowiedzi_przy_niepewnosci

- prompt: Czy model bazowy powinien odpowiadać na instrukcje? Krótko.
  response: Nie musi. Model bazowy głównie kontynuuje tekst.
- prompt: Czy można ocenić bezpieczeństwo bez kontekstu? Krótko.
  response: Bez kontekstu da się najwyżej wskazać możliwe ryzyka.
- prompt: Czy kontynuować, gdy wynik jest mieszany? Bez przesadnej pewności.
  response: W pierwszym kroku trzeba ustalić, czy problem wynika z danych, modelu, czy sposobu oceny.
- prompt: Czy krótsze odpowiedzi zawsze są lepsze? Odpowiedz ostrożnie.
  response: Są lepsze wtedy, gdy odpowiadają na pytanie bez utraty potrzebnych informacji.

### proste_techniczne_wyjasnienia

- prompt: Wyjaśnij krótko: Po co zapisuje się metadata checkpointu?
  response: Metadata checkpointu opisuje model, dataset i ustawienia, żeby uniknąć pomyłek przy resume albo ewaluacji.
- prompt: Krótko i konkretnie: Co oznacza limit RAM dla kontenera?
  response: Limit RAM ogranicza ilość pamięci, którą kontener może zużyć, żeby nie zajął całego hosta.
- prompt: Odpowiedz prosto: Po co są logi treningu?
  response: Logi treningu pokazują kroki, loss, prędkość, checkpointy i błędy.
- prompt: Wyjaśnij krótko, czym różni się RAM od dysku?
  response: RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera.
