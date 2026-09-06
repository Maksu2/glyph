# Glyph-100M SFT smoke v0.3 before/after eval

## Summary

- rows: `200`
- best mode: `no_repeat_ngram_size_3`

## Mode: greedy

- base44k: avg `-1.33`, median `-2.00`, rep `136`, end `0.00`, real_web `1`, pseudo `0`, first `2`
- sft_v0_1: avg `4.44`, median `4.00`, rep `51`, end `0.91`, real_web `1`, pseudo `0`, first `74`
- sft_v0_2: avg `5.10`, median `6.00`, rep `31`, end `0.93`, real_web `4`, pseudo `0`, first `83`
- sft_v0_3_final: avg `5.26`, median `5.50`, rep `26`, end `0.97`, real_web `4`, pseudo `0`, first `84`
- sft_v0_3_best: avg `5.18`, median `4.50`, rep `16`, end `0.98`, real_web `4`, pseudo `0`, first `76`
- pairwise: `{'sft_v0_3_best_vs_sft_v0_2': {'sft_v0_2': 27, 'tie': 146, 'sft_v0_3_best': 27}, 'sft_v0_3_best_vs_sft_v0_1': {'sft_v0_1': 19, 'tie': 128, 'sft_v0_3_best': 53}, 'sft_v0_3_best_vs_base44k': {'sft_v0_3_best': 190, 'base44k': 1, 'tie': 9}, 'sft_v0_3_best_vs_sft_v0_3_final': {'sft_v0_3_final': 16, 'tie': 165, 'sft_v0_3_best': 19}, 'sft_v0_3_final_vs_sft_v0_2': {'sft_v0_3_final': 32, 'tie': 137, 'sft_v0_2': 31}}`

## Mode: no_repeat_ngram_size_3

- base44k: avg `0.55`, median `0.00`, rep `28`, end `0.00`, real_web `10`, pseudo `1`, first `0`
- sft_v0_1: avg `4.92`, median `4.00`, rep `3`, end `0.99`, real_web `2`, pseudo `0`, first `61`
- sft_v0_2: avg `5.10`, median `4.00`, rep `2`, end `1.00`, real_web `7`, pseudo `0`, first `64`
- sft_v0_3_final: avg `5.05`, median `4.00`, rep `1`, end `0.99`, real_web `6`, pseudo `0`, first `64`
- sft_v0_3_best: avg `4.79`, median `4.00`, rep `4`, end `0.99`, real_web `5`, pseudo `0`, first `59`
- pairwise: `{'sft_v0_3_best_vs_sft_v0_2': {'sft_v0_2': 29, 'tie': 151, 'sft_v0_3_best': 20}, 'sft_v0_3_best_vs_sft_v0_1': {'sft_v0_1': 23, 'tie': 162, 'sft_v0_3_best': 15}, 'sft_v0_3_best_vs_base44k': {'sft_v0_3_best': 186, 'tie': 12, 'base44k': 2}, 'sft_v0_3_best_vs_sft_v0_3_final': {'tie': 166, 'sft_v0_3_best': 12, 'sft_v0_3_final': 22}, 'sft_v0_3_final_vs_sft_v0_2': {'sft_v0_2': 24, 'tie': 152, 'sft_v0_3_final': 24}}`

## Mode: no_repeat_ngram_size_4

- base44k: avg `0.14`, median `0.00`, rep `73`, end `0.00`, real_web `8`, pseudo `2`, first `3`
- sft_v0_1: avg `5.05`, median `4.00`, rep `9`, end `0.99`, real_web `1`, pseudo `0`, first `68`
- sft_v0_2: avg `5.18`, median `4.00`, rep `5`, end `1.00`, real_web `7`, pseudo `0`, first `69`
- sft_v0_3_final: avg `5.10`, median `4.00`, rep `11`, end `0.99`, real_web `5`, pseudo `0`, first `68`
- sft_v0_3_best: avg `5.18`, median `4.00`, rep `12`, end `1.00`, real_web `2`, pseudo `0`, first `72`
- pairwise: `{'sft_v0_3_best_vs_sft_v0_2': {'sft_v0_3_best': 24, 'tie': 157, 'sft_v0_2': 19}, 'sft_v0_3_best_vs_sft_v0_1': {'sft_v0_1': 17, 'tie': 157, 'sft_v0_3_best': 26}, 'sft_v0_3_best_vs_base44k': {'sft_v0_3_best': 191, 'tie': 7, 'base44k': 2}, 'sft_v0_3_best_vs_sft_v0_3_final': {'tie': 164, 'sft_v0_3_best': 21, 'sft_v0_3_final': 15}, 'sft_v0_3_final_vs_sft_v0_2': {'sft_v0_3_final': 18, 'tie': 161, 'sft_v0_2': 21}}`

## Mode: topk40_temp07

- base44k: avg `-1.02`, median `-1.00`, rep `140`, end `0.00`, real_web `2`, pseudo `0`, first `3`
- sft_v0_1: avg `4.71`, median `4.00`, rep `37`, end `0.98`, real_web `1`, pseudo `0`, first `72`
- sft_v0_2: avg `5.25`, median `5.00`, rep `19`, end `1.00`, real_web `9`, pseudo `0`, first `76`
- sft_v0_3_final: avg `5.13`, median `4.00`, rep `18`, end `0.99`, real_web `1`, pseudo `0`, first `70`
- sft_v0_3_best: avg `5.01`, median `4.00`, rep `19`, end `1.00`, real_web `6`, pseudo `0`, first `69`
- pairwise: `{'sft_v0_3_best_vs_sft_v0_2': {'sft_v0_2': 31, 'tie': 155, 'sft_v0_3_best': 14}, 'sft_v0_3_best_vs_sft_v0_1': {'sft_v0_1': 29, 'tie': 129, 'sft_v0_3_best': 42}, 'sft_v0_3_best_vs_base44k': {'sft_v0_3_best': 190, 'tie': 8, 'base44k': 2}, 'sft_v0_3_best_vs_sft_v0_3_final': {'sft_v0_3_final': 29, 'tie': 151, 'sft_v0_3_best': 20}, 'sft_v0_3_final_vs_sft_v0_2': {'tie': 142, 'sft_v0_2': 27, 'sft_v0_3_final': 31}}`

## Mode: topk40_temp07_no_repeat_ngram_size_3

- base44k: avg `0.60`, median `0.00`, rep `32`, end `0.00`, real_web `9`, pseudo `2`, first `3`
- sft_v0_1: avg `5.00`, median `4.00`, rep `7`, end `1.00`, real_web `3`, pseudo `0`, first `62`
- sft_v0_2: avg `5.12`, median `4.00`, rep `3`, end `1.00`, real_web `6`, pseudo `0`, first `63`
- sft_v0_3_final: avg `5.15`, median `4.00`, rep `2`, end `1.00`, real_web `5`, pseudo `0`, first `64`
- sft_v0_3_best: avg `4.81`, median `3.00`, rep `3`, end `0.99`, real_web `6`, pseudo `0`, first `60`
- pairwise: `{'sft_v0_3_best_vs_sft_v0_2': {'sft_v0_2': 30, 'tie': 155, 'sft_v0_3_best': 15}, 'sft_v0_3_best_vs_sft_v0_1': {'sft_v0_1': 30, 'tie': 148, 'sft_v0_3_best': 22}, 'sft_v0_3_best_vs_base44k': {'sft_v0_3_best': 188, 'base44k': 3, 'tie': 9}, 'sft_v0_3_best_vs_sft_v0_3_final': {'sft_v0_3_final': 20, 'tie': 167, 'sft_v0_3_best': 13}, 'sft_v0_3_final_vs_sft_v0_2': {'tie': 157, 'sft_v0_2': 22, 'sft_v0_3_final': 21}}`

## Highest-scoring 20 outputs by automated format heuristic

> This ranking measures formatting, stopping and surface-level failure signals. Manual review found semantic errors even among high-scoring outputs, so it must not be read as a list of genuinely correct answers.

### 1. anty_powtorzenia_i_konczenie · score=10

Prompt: Odpowiedz krótko i zakończ naturalnie: czym jest backup? Tylko sedno.

Backup to kopia danych potrzebna do odtworzenia tych danych po awarii.

### 2. poprawki_tekstu · score=10

Prompt: Przeredaguj zdanie: Została przeprowadzona walidacja poprawności działania systemu.

Sprawdzono poprawność działania systemu od początku do końca.

### 3. anty_web_residue · score=9

Prompt: Odpowiedz bez stylu sklepu: czym jest backup?

Backup to kopia danych potrzebna do odtworzenia ich po awarii.

### 4. anty_web_residue · score=9

Prompt: Wyjaśnij tokenizer bez marketingu i bez tekstu strony firmowej.

Zacznij od marketingu, modelu, zasobów i zasobów.

### 5. anty_web_residue · score=9

Prompt: Napisz technicznie, bez reklamy: po co jest checkpoint?

Checkpointy są checkpotliwe, ale checkpolishment nadal jest checkupoint, a checkporty są Checkpotl.

### 6. anty_powtorzenia_i_konczenie · score=9

Prompt: Odpowiedz jednym zdaniem i nie powtarzaj: po co jest eval?

Eval to procesor graficzny, który pozwala na projektowanie nowych funkcji.

### 7. anty_powtorzenia_i_konczenie · score=9

Prompt: Zakończ po jednej myśli: kiedy odpowiedź jest kompletna?

Zakończona wersja to liczba promptów, liczba to liczba całkowita liczba całkowita.

### 8. anty_powtorzenia_i_konczenie · score=9

Prompt: Nie powtarzaj pierwszego słowa: czym jest smoke test?

Smoke test to zestaw błędów, które można sprawdzić bez ich powtarzania.

### 9. brak_danych_bez_petli · score=9

Prompt: Czy ten laptop jest dobry? Nie podaję modelu.

Nie. Trzeba znać jakość, jakość i zastosowanie laptopa.

### 10. brak_danych_bez_petli · score=9

Prompt: Czy wynik jest poprawny? Nie podaję oczekiwanego wyniku.

Nie wiadomo dokładnie czy wynik jest błędny, czy błędny.

### 11. brak_danych_bez_petli · score=9

Prompt: Czy powinienem kontynuować trening? Nie podaję evala.

Nie mogę pokazać, czy mogę sprawdzić trening, czy dana osoba wykonuje trening.

### 12. techniczne_proste_wyjasnienia · score=9

Prompt: Czym różni się train loss od val loss?

Train lose loss to liczba całkowita używana do odtworzenia trainów.

### 13. techniczne_proste_wyjasnienia · score=9

Prompt: Czym jest gradient accumulation?

Gradient Accumulations wykonuje jedną generację, która wymaga jednego przelicznika, kolejnego przelicznik albo przeliczniki.

### 14. techniczne_proste_wyjasnienia · score=9

Prompt: Czym jest no-repeat ngram w generacji?

No-replet ng generacji to liczba promptów, a liczba propertów to liczba zbyt wąska.

### 15. sanity_fakty_podstawowe · score=9

Prompt: Fakt różni się od opinii tym, że

Fakt jest prosty i niepewny, więc trzeba go uogólnić.

### 16. sanity_fakty_podstawowe · score=9

Prompt: Kilometr to

Kilomet to po prostu pocisk zapisujący dane wejściowe, ale nie zapisujące ich później.

### 17. codzienne_proste_pytania · score=9

Prompt: Poproś krótko o ponowne przesłanie pliku.

Zakończ się nie później niż do końca, ale nadal nie dodawaj nowych funkcji.

### 18. mvp_first_project_advice · score=9

Prompt: Czy zaczynać projekt od UI czy od logiki?

Najpierw kończyć go w jednym toksie, potem od logików.

### 19. mvp_first_project_advice · score=9

Prompt: Czy robić od razu backend, frontend, dashboard i AI?

Nie. Najpierw trzeba znać jakość, jakość i jakość.

### 20. not_in_dataset_style_generalization · score=9

Prompt: Czy SFT automatycznie dodaje modelowi wiedzę?

SFT pokazuje, co robi model i jak ją oceniasz.

## Worst 20 v0.3 Best Outputs

### 1. mini_streszczenia · score=1 · issues=['real web residue']

Prompt: Streść: Niższy loss może wyglądać dobrze, ale sample mogą pokazywać pętle i słabe odpowiedzi.

Niższa loss nie dodaje nowych odpowiedzi. Samaple mogą być bardziej odległe.

### 2. ostrozne_odpowiedzi · score=1 · issues=['real web residue']

Prompt: Czy krótsze odpowiedzi zawsze są lepsze? Odpowiedz ostrożnie.

Nie. Najpierw trzeba znać ostatnią metodę, która pozwala ocenić jakość odpowiedzi, metrykę i jakość odpowiedzi.

### 3. codzienne_proste_pytania · score=1 · issues=['real web residue']

Prompt: Co zrobić, gdy odpowiedź jest zbyt długa? Jednym akapitem.

Nie. Najpierw sprawdź dokładnie, czy tekst jest zbyt wąski, żeby odpowiedzieć dokładnie.

### 4. anty_powtorzenia_i_konczenie · score=1 · issues=['real web residue']

Prompt: Napisz krótką odpowiedź i nie powtarzaj tej samej myśli. Zwięźle.

Ten ostatni krok ułatwia zrozumienie i powtórzenie tej samej odpowiedzi.

### 5. not_in_dataset_style_generalization · score=1 · issues=['real web residue']

Prompt: Czy ładna odpowiedź zawsze jest poprawna?

Odpowiedź nie jest poprawną odpowiedzią.

### 6. base_lm_sanity · score=1 · issues=['word loop', 'too long / no stop']

Prompt: Najważniejszym problemem tego projektu jest

liczba bazy danych, które potrzebują nowych danych. Dzięki temu dane mogą być stabilniejsze i łatwiejsze do zapisu. Dzięki tej technologii można zwiększyć liczbę bazy danych. Zalety generacji i zastosowanie Model model modelu Model Model model Model Model Model jest dostępny poza granicami projektu. Model Model pozwala sprawdzić, czy model jest stabilniejszy i lepiej działa. Model ten działa dobrze. Model działa d...

### 7. sanity_fakty_podstawowe · score=2 · issues=['too long / no stop']

Prompt: Plik różni się od folderu tym, że

Folder to jeden z folderów. Folder dzieli się na foldery, foldery i foldery. Foldery dzieli się ze względu na to, że foldery są ustalone. Foldel dzieli się wtedy na folderowe i folderskie. Fold dzieli się zwykle na foldry i foldki. Folding dzieli się też na foldki, folder i foldy.

### 8. ostrozne_odpowiedzi · score=2 · issues=['phrase loop']

Prompt: Czy można ufać jednej próbce generacji?

Nie da się tego przekonać, jeśli nie da się stwierdzić.

### 9. krotkie_definicje_poprawne · score=3 · issues=['low semantic score']

Prompt: Podaj prostą definicję: prototyp.

Samolot był pierwszym myśliwcem, który nie zgadzał się na tym teście.

### 10. ostrozne_odpowiedzi · score=3 · issues=['low semantic score']

Prompt: Czy można zgadywać brakujące parametry? Krótko.

Nie. Ograniczenie ustawień generacji i kryteriów oceny daje znać sensownie.

### 11. techniczne_proste_wyjasnienia · score=3 · issues=['low semantic score']

Prompt: Odpowiedz prosto: Czym jest overfitting w modelu językowym?

Overfit to podstawowy sposób odtworzenia modelu od podstawowego modelu językowego.

### 12. mini_streszczenia · score=3 · issues=['low semantic score']

Prompt: Napisz sedno tego tekstu: Nie każdy problem wymaga aplikacji, kont użytkowników i dashboardu. Czasem wystarczy prosty skrypt albo plik tekstowy.

Zmniejsza to liczba i nie trzeba pomiarów.

### 13. brak_danych_bez_petli · score=3 · issues=['low semantic score']

Prompt: Czy ta decyzja jest bezpieczna? Zakończ naturalnie.

Zakończenie nie wystarczy, gdy brakuje informacji o błędzie.

### 14. anty_powtorzenia_i_konczenie · score=3 · issues=['low semantic score']

Prompt: Wyjaśnij, dlaczego nie warto powtarzać tej samej frazy. Bez lania wody.

Sprawdź, czy model działa poprawnie.

### 15. brak_danych_bez_petli · score=3 · issues=['low semantic score']

Prompt: Czy ta optymalizacja ma sens? Nie zgaduj.

Sama optymalizacja zależy od kontekstu i kryteriów treningu.

### 16. brak_danych_bez_petli · score=3 · issues=['low semantic score']

Prompt: Czy to jest bezpieczne? Nie udawaj pewności.

Nie, duże obciążenie może być utrudnione.

### 17. mini_streszczenia · score=3 · issues=['low semantic score']

Prompt: Podaj krótkie streszczenie: Częste checkpointy pomagają przy ryzyku awarii, ale zajmują dużo miejsca.

Powinien pozwolić na start.

### 18. ostrozne_odpowiedzi · score=3 · issues=['low semantic score']

Prompt: Czy trzeba trenować do końca planu? Bez przesadnej pewności.

Nie. Najpierw trzeba trenowanie do końca.

### 19. krotkie_definicje_poprawne · score=3 · issues=['low semantic score']

Prompt: Wyjaśnij krótko pojęcie: ryzyko.

Bez celu zależy od konkretnego modelu, modelu, jakości i sposobu treningu.

### 20. mvp_first_project_advice · score=3 · issues=['low semantic score']

Prompt: Krótko doradź: Projekt robi się za duży.

Projekt robi wszystko, żeby poprawić jakość danych i jednocześnie poprawić jakość.
