# Glyph-100M SFT v0.1 vs v0.2 best decoding

- mode: `no_repeat_ngram_size_3`
- rows: `150`
- pairwise: `{'sft_v0_2_vs_sft_v0_1': {'tie': 121, 'sft_v0_2': 17, 'sft_v0_1': 12}, 'sft_v0_2_vs_base44k': {'sft_v0_2': 137, 'tie': 9, 'base44k': 4}, 'sft_v0_1_vs_base44k': {'sft_v0_1': 139, 'tie': 9, 'base44k': 2}}`

## Model Summaries

- base44k: avg `0.95`, median `0.00`, rep `21`, end_rate `0.00`, web `3`, first `1`
- sft_v0_1: avg `5.16`, median `4.00`, rep `2`, end_rate `1.00`, web `2`, first `37`
- sft_v0_2: avg `5.35`, median `4.00`, rep `4`, end_rate `1.00`, web `6`, first `44`

## v0.2 Improvements over v0.1

### 1. mini_streszczenia

Prompt: Skróć tekst: W małym modelu krótki kontekst ogranicza zdolność utrzymania dłuższej wypowiedzi.

v0.1: Krótka wersja to długa wersja, która da się uruchomić po przerwie.

v0.2: długi kontekst zmienia się na zbyt krótki kontekstu.

### 2. anty_powtorzenia_i_konczenie

Prompt: Zakończ jasno: kiedy nie zgadywać? Nie dodawaj kolejnej wersji tej samej myśli.

v0.1: Zakończenie jasno pokazuje, czy dany model uczy się wzorców.

v0.2: Nie zgaduj. Zrób to, gdy brakuje informacji zwrotnych.

### 3. krotkie_poprawki_tekstu

Prompt: Skróć i popraw: Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.

v0.1: Zostaw tylko opis pracy.

v0.2: Nie zdążę dziś oddać wiedzy o pracy.

### 4. naturalne_zakonczenia

Prompt: Opisz krótko, co oznacza dobry raport techniczny. Krótkim akapitem.

v0.1: Raport techniczno-techniczny gwarantuje sprawdzenie, czy program działa poprawnie.

v0.2: Dobry raport Techniczny zapisuje dobry raporty, nie zgadując decyzji.

### 5. anty_powtorzenia_i_konczenie

Prompt: Zakończ jasno: kiedy nie zgadywać? Krótko.

v0.1: Najpierw sprawdź, czy punkt jest prosty, czy nie. Lepsza jest krótka, konkretna liczba i nie da się jej szybko dostrzec.

v0.2: Nie zgaduj.

### 6. anty_powtorzenia_i_konczenie

Prompt: Odpowiedz krótko: kiedy dataset jest za słaby? Zakończ po kompletnej odpowiedzi.

v0.1: Losowanie pomaga złagodzić problem.

v0.2: Dataset jest zbyt długa.

### 7. krotkie_definicje

Prompt: Co oznacza termin „inferencja”?

v0.1: Zapisuję informacje potrzebne do wyjaśnienia problemu i celu.

v0.2: Inferencja to stan modelu, który nie działa poprawnie.

### 8. naturalne_zakonczenia

Prompt: Opisz krótko, co oznacza dobry raport techniczny. Odpowiedz spokojnie.

v0.1: Raport technicy zwykle zakłada, że czas pracy jest krótki.

v0.2: Dobry raport wykonuje sam.

### 9. codzienne_proste_pytania

Prompt: Co zrobić, gdy odpowiedź jest zbyt długa? Daj prostą radę.

v0.1: Najpierw powtarzaj tekst i zostaw sam tekst, potem sprawdź prosty opis działania.

v0.2: Usuń ją ponownie i powtórz ją dopiero, gdy główna odpowiedź jest krótka.

### 10. anty_powtorzenia_i_konczenie

Prompt: Nie powtarzaj: jak kończyć odpowiedź? Jednym akapitem.

v0.1: Wybierz krótki tekst, który chcesz zrobić, gdy ta decyzja jest przypadkowa.

v0.2: Zakończ ją wtedy, gdy ją uruchomi.

### 11. brak_danych

Prompt: Czy ten projekt warto pokazać? Jednym akapitem.

v0.1: Powinna być proste, łatwe i łatwe zadanie, bez ryzyka błędów.

v0.2: Nie da się bez oczywistych danych ocenić jakości i zastosowania.

### 12. anty_powtorzenia_i_konczenie

Prompt: Zakończ naturalnie: czy większy model zawsze pomaga? Krótko.

v0.1: Nie. Model pozwala ocenić, czy model działająco, ale może być problematyczny, ale też problematyczny.

v0.2: Nie, większy model nadal zależy od jakości danych, treningu i treningu.

### 13. anty_powtorzenia_i_konczenie

Prompt: Jedna myśl: co oznacza brak danych? Krótko.

v0.1: Nie. Lepsza jest potrzebna do uczenia się, a nie do odtworzenia treści.

v0.2: Brak danych oznacza, że model może być potrzebny do użycia.

### 14. anty_powtorzenia_i_konczenie

Prompt: Jedna myśl: co daje czysty dataset? Bez powtarzania.

v0.1: To zależy od kontekstu i od kontekstów.

v0.2: Czysty datasetujące dane nie wystarczają do dalszego treningu.

### 15. brak_danych

Prompt: Czy mogę zaufać tej odpowiedzi? Zakończ naturalnie.

v0.1: Nie mogę dziś zaufać odpowiedzi.

v0.2: Zmierz strefę stref i powtórz wynik.

## v0.2 Regressions vs v0.1

### 1. mini_streszczenia

Prompt: Napisz sedno tego tekstu: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

v0.1: Zostaw tylko informacje potrzebne do decyzji.

v0.2: Jeśli czytasz odpowiedzi, warto pomylić tekst z czytelniejszymi słowami.

### 2. mvp_first_project_advice

Prompt: Podaj rozsądny następny krok: Mam dużo pomysłów i nie wiem od czego zacząć.

v0.1: Zacznij od początku, ale dopiero potem powtórz krótko.

v0.2: Zacznij od odpowiedzi i zostaw tylko informację potrzebną do decyzji.

### 3. anty_petle

Prompt: Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Bez drugiej myśli.

v0.1: Loss może wskazywać, czy loss jest zbyt duży, żeby poprawić jakość.

v0.2: Zmierz loss, loss i loss.

### 4. krotkie_poprawki_tekstu

Prompt: Napisz naturalniej: Proces treningu został zakończony w sposób poprawny.

v0.1: Proces treningowy zakończył się poprawnie.

v0.2: Na start próbowano poprawić jakość treningu.

### 5. krotkie_poprawki_tekstu

Prompt: Przeredaguj zdanie: Wyniki pokazują, że doszło do poprawy jakości.

v0.1: Wyniki pokazujące, że jakość byłaby zbyt dobra.

v0.2: Poprawa jakości nie wystarcza.

### 6. ostrozne_odpowiedzi_przy_niepewnosci

Prompt: Czy krótsze odpowiedzi zawsze są lepsze? Bez przesadnej pewności.

v0.1: Nie. Zostaw tylko te te fragmenty, które nie są potrzebne do pracy.

v0.2: Najpierw krótsze są krótkie odpowiedzi, później krótsze to bardziej wąskie odpowiedzi.

### 7. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych? Nie dodawaj przykładu.

v0.1: Bez danych nie dających się ocenić z góry.

v0.2: Nie da się tego ocenić bez informacji, kontekstu i kryteriów.

### 8. mini_streszczenia

Prompt: Podaj krótkie streszczenie: Najpierw warto sprawdzić, czy pipeline działa, zanim zwiększy się skalę eksperymentu.

v0.1: Skalę piperonową można sprawdzić tylko wtedy, gdy piperoline działa.

v0.2: Najpierw sprawdź, czy model działa, czy jest gotowy.

### 9. codzienne_proste_pytania

Prompt: Jak zaplanować naukę na jutro? Jednym akapitem.

v0.1: Wybierz jedną konkretną odpowiedź, którą można zrobić, i zaplanuj ją na późniejszych etapach.

v0.2: Zacznij od nauki na początku tego roku, potem sprawdź metodę oceny.

### 10. krotkie_definicje

Prompt: Co oznacza termin „zbiór walidacyjny”?

v0.1: Zbiór walikowy to zbiór walidów o charakterze logistyczno-fizycznym.

v0.2: Model oznacza, że model jest modelowany przez model, model i model pokazują, jak model działa.

### 11. not_in_dataset

Prompt: Czy krótsza odpowiedź zawsze jest lepsza?

v0.1: Nie, ale warto sprawdzić, czy jest poprawnie działająca odpowiedź. Trzeba wskazać, jakich informacji brakuje, i nie zgadywać wyniku.

v0.2: Nie, krótsza odpowiedzi nie gwarantuje lepszego zrozumienia.

### 12. base_lm_sanity

Prompt: Dobry raport techniczny

v0.1: ustalił, czy model uczy się wzorców wzorców. Dzięki temu model może pracować na różnych maszynach, a nie na różnych pasach, bo jest to prosty przykład. Raport techniczno-instrumentalny jest prosty. Model uczy się za to najmniejszego modelu. Model może pracować bez za to zbyt duży. Model pomaga w tworzeniu wzorców i model może wykonywać różne zadania.

v0.2: podaje, że model może pracować jako model optymalizujący wydajność pracy. Model może pracować w warunkach, w których model jest optymalizowany. Model optymalizuje bezpieczeństwo pracy i poprawę jakości. Model powinien pracować jako Model optymalizujący jakość pracy. Powtarzalny model może kontrolować koszt, jakość pracy i ograniczenia. Model ma duże ograniczenia. Dlatego model może nadal kontrolować ryzyko. Model...
