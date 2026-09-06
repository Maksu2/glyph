# Glyph-100M SFT smoke v0.3 dataset report

## Summary

- examples: 2753
- split train/val/test: {'train': 2341, 'val': 275, 'test': 137}
- max template tokens: 76 / 512
- over context: 0
- exact duplicate pairs: 0
- near duplicate samples: 80
- label audit: `{'first_token_supervised': True, 'end_token_supervised': True, 'prompt_masked': True, 'padding_ignore_index': True, 'examples_without_labels': 0}`

## Categories

- anty_powtorzenia_i_konczenie: 820
- anty_web_residue: 56
- brak_danych_bez_petli: 326
- codzienne_proste_pytania: 185
- krotkie_definicje_poprawne: 286
- mini_streszczenia: 175
- mvp_first_project_advice: 185
- not_in_dataset_style_generalization: 64
- ostrozne_odpowiedzi: 185
- poprawki_tekstu: 213
- sanity_fakty_podstawowe: 60
- techniczne_proste_wyjasnienia: 198

## First Response Words

- `nie`: 275
- `trzeba`: 92
- `checkpoint`: 59
- `backup`: 54
- `walidacja`: 50
- `tokenizer`: 49
- `zacznij`: 46
- `raczej`: 45
- `odpowiedź`: 43
- `bez`: 42
- `to`: 41
- `smoke`: 40
- `model`: 39
- `raport`: 35
- `sprawdź`: 32
- `potrzebne`: 32
- `wybierz`: 30
- `sft`: 30
- `potrzebny`: 29
- `na`: 28
- `loss`: 28
- `ten`: 27
- `tak`: 25
- `zostaw`: 23
- `log`: 22
- `usuń`: 22
- `overfit`: 22
- `gpu`: 21
- `projekt`: 20
- `eval`: 20
- `dataset`: 20
- `powtórzenia`: 20
- `czysty`: 19
- `ram`: 19
- `potrzebna`: 19
- `uważam`: 17
- `gradient`: 17
- `dobry`: 17
- `zakończ`: 17
- `powiedz`: 17

## Top Response 4-grams

- `backup to kopia danych`: 44
- `nie da się tego`: 44
- `checkpoint to zapis stanu`: 39
- `do odtworzenia ich po`: 34
- `odtworzenia ich po awarii`: 34
- `to zapis stanu modelu`: 32
- `do którego można wrócić`: 29
- `którego można wrócić później`: 29
- `tokenizer dzieli tekst na`: 28
- `dzieli tekst na tokeny`: 28
- `to kopia danych potrzebna`: 27
- `kopia danych potrzebna do`: 27
- `danych potrzebna do odtworzenia`: 27
- `potrzebna do odtworzenia ich`: 27
- `potrzebny jest model cena`: 24
- `smoke test to krótka`: 23
- `test to krótka próba`: 23
- `to krótka próba sprawdzająca`: 23
- `krótka próba sprawdzająca czy`: 23
- `nie mogę dziś przyjść`: 22
- `raport zapisuje wynik ustawienia`: 22
- `zapisuje wynik ustawienia i`: 22
- `jakość danych jest ważniejsza`: 22
- `danych jest ważniejsza niż`: 22
- `overfit oznacza że model`: 22
- `dopasował się do danych`: 22
- `się do danych treningowych`: 22
- `do danych treningowych i`: 22
- `większy model nadal zależy`: 22
- `model nadal zależy od`: 22
- `nadal zależy od jakości`: 22
- `zależy od jakości danych`: 22
- `da się tego ocenić`: 22
- `się tego ocenić bez`: 22
- `zapis stanu modelu do`: 22
- `stanu modelu do którego`: 22
- `modelu do którego można`: 22
- `nie da się ocenić`: 20
- `da się ocenić bez`: 20
- `śmieci duplikaty albo zbyt`: 20

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
- `skontaktuj się z nami`: 0
- `na naszej stronie`: 0

## Random Examples Per Category

### anty_powtorzenia_i_konczenie

- prompt: Bez rozwijania: co zrobić z dziwnym wynikiem? Nie dodawaj kolejnej wersji tej samej myśli.
  response: Sprawdź metodę, dane i powtórz test na tym samym zestawie.
- prompt: Wyjaśnij jednym akapitem, po co robi się raport po eksperymencie. Jednym akapitem.
  response: Raport zapisuje wynik, ustawienia i wnioski, dzięki czemu można później podjąć lepszą decyzję.
- prompt: Jednym zdaniem: po co raport? Jednym akapitem.
  response: Raport zapisuje wynik, ustawienia i decyzję po eksperymencie.
- prompt: Nie powtarzaj frazy: czy warto trenować dalej bez evala? Bez powtarzania.
  response: Nie warto, bo bez evala nie wiadomo, czy model faktycznie się poprawia.
- prompt: Wyjaśnij prosto, czym jest log. Zakończ po sensownej myśli.
  response: Log to zapis zdarzeń z działania programu, przydatny przy diagnozowaniu błędów.
- prompt: Bez pętli: dlaczego powtórzenia są złe?
  response: Powtórzenia obniżają czytelność i zwykle nie dodają treści.
- prompt: Odpowiedz krótko i zakończ naturalnie: czym jest backup? Bez dygresji.
  response: Backup to kopia danych potrzebna do odtworzenia ich po awarii.
- prompt: Bez pętli: co zrobić, gdy odpowiedź jest kompletna? Bez powtarzania.
  response: Zakończyć ją i nie dopisywać kolejnych wersji tej samej myśli.
- prompt: Nie rozwijaj bez końca: dlaczego warto mierzyć loss?
  response: Loss pokazuje, czy model uczy się przewidywać dane treningowe lub walidacyjne.
- prompt: Nie dopisuj drugiej myśli: co zrobić po awarii? Jednym akapitem.
  response: Najpierw zabezpiecz logi i ostatni poprawny checkpoint.

### anty_web_residue

- prompt: Nie używaj marketingu: czym jest checkpoint?
  response: Checkpoint to zapis stanu treningu, do którego można wrócić później.
- prompt: Usuń styl SEO: dlaczego czysty dataset jest ważny? Naturalnie.
  response: Czysty dataset zmniejsza ryzyko, że model nauczy się spamu, menu i reklam.
- prompt: Nie używaj marketingu: czym jest checkpoint? Bez linków.
  response: Checkpoint to zapis stanu treningu, do którego można wrócić później.
- prompt: Napisz odpowiedź techniczną bez tekstu sklepu: czym jest backup?
  response: Backup to kopia danych używana do odtworzenia ich po awarii.
- prompt: Nie używaj marketingu: czym jest checkpoint? Bez reklam.
  response: Checkpoint to zapis stanu treningu, do którego można wrócić później.
- prompt: Odpowiedz bez wezwania do kontaktu: co zrobić po błędzie? Bez linków.
  response: Zapisz log, sprawdź ostatnią zmianę i odtwórz problem w kontrolowany sposób.
- prompt: Nie pisz jak strona firmowa: czym jest tokenizer? Bez reklam.
  response: Tokenizer dzieli tekst na tokeny, które model przetwarza jako liczby.
- prompt: Nie rób z tego oferty handlowej: po co jest raport?
  response: Raport zapisuje ustawienia, wynik i decyzję po eksperymencie.
- prompt: Napisz odpowiedź techniczną bez tekstu sklepu: czym jest backup? Jednym zdaniem.
  response: Backup to kopia danych używana do odtworzenia ich po awarii.
- prompt: Napisz odpowiedź techniczną bez tekstu sklepu: czym jest backup? Naturalnie.
  response: Backup to kopia danych używana do odtworzenia ich po awarii.

### brak_danych_bez_petli

- prompt: Czy model działa dobrze?
  response: Trzeba zobaczyć próbki, metryki i zestaw testowy. Sama informacja, że działa, nie wystarcza.
- prompt: Czy ten projekt warto pokazać? Powiedz, czego brakuje.
  response: Nie wiadomo bez celu, odbiorcy i aktualnego stanu projektu.
- prompt: Czy ta strona wygląda dobrze? Nie zgaduj.
  response: Nie da się ocenić bez zrzutu ekranu albo opisu celu i odbiorców.
- prompt: Czy ten komputer wystarczy? Podaj uczciwą odpowiedź.
  response: To zależy od zastosowania. Podaj programy, budżet i wymagania, wtedy da się ocenić sensownie.
- prompt: Czy wynik benchmarku jest dobry? Podaj uczciwą odpowiedź.
  response: Trzeba znać sprzęt, ustawienia testu i punkt odniesienia. Sama liczba nie wystarcza.
- prompt: Czy ten wynik jest poprawny? Nie udawaj pewności.
  response: Nie mam danych wejściowych ani oczekiwanego wyniku, więc nie da się tego rzetelnie sprawdzić.
- prompt: Czy mogę zaufać tej odpowiedzi? Odpowiedz uczciwie.
  response: Bez źródeł, kontekstu i kryteriów nie należy traktować odpowiedzi jako pewnej.
- prompt: Czy ta optymalizacja ma sens? Odpowiedz ostrożnie.
  response: Zacznij od trzeba zmierzyć wąskie gardło. Bez pomiaru optymalizacja może być przypadkowa.
- prompt: Czy ta optymalizacja ma sens? Krótko.
  response: Na start trzeba zmierzyć wąskie gardło. Bez pomiaru optymalizacja może być przypadkowa.
- prompt: Czy ta optymalizacja ma sens? Nie dopowiadaj faktów.
  response: Na start trzeba zmierzyć wąskie gardło. Bez pomiaru optymalizacja może być przypadkowa.

### codzienne_proste_pytania

- prompt: Co zrobić, gdy coś działa wolno? Bez listy.
  response: Zacznij od zmierz, co jest wąskim gardłem, zamiast zgadywać przyczynę.
- prompt: Jak kończyć odpowiedź? Odpowiedz krótko.
  response: Zakończ wtedy, gdy główna myśl jest jasna i nie dodawaj nowych wątków na siłę.
- prompt: Jak poprosić o feedback? Odpowiedz krótko.
  response: Pokaż konkretny fragment i zapytaj o jedną rzecz, którą chcesz poprawić.
- prompt: Jak zacząć porządkować pliki? Bez listy.
  response: Zacznij od utwórz kilka głównych folderów i przenieś do nich oczywiste pliki.
- prompt: Jak ocenić, czy tekst jest jasny?
  response: Sprawdź, czy po pierwszym czytaniu wiadomo, o co chodzi i co trzeba zrobić.
- prompt: Napisz neutralnie, że nie mogę dziś przyjść. Bez tłumaczenia się.
  response: Nie mogę dziś przyjść. Dam znać, kiedy będę dostępny.
- prompt: Jak ocenić, czy tekst jest jasny? Odpowiedz krótko.
  response: Sprawdź, czy po pierwszym czytaniu wiadomo, o co chodzi i co trzeba zrobić.
- prompt: Jak pisać prościej? Daj prostą radę.
  response: Używaj krótszych zdań i konkretnych czasowników.
- prompt: Napisz neutralnie, że nie mogę dziś przyjść.
  response: Nie mogę dziś przyjść. Dam znać, kiedy będę dostępny.
- prompt: Jak wybrać priorytet? Bez listy.
  response: Wybierz zadanie, które usuwa największą blokadę albo daje najwięcej informacji.

### krotkie_definicje_poprawne

- prompt: Co oznacza termin „model językowy”?
  response: Model językowy przewiduje kolejne fragmenty tekstu na podstawie wcześniejszego kontekstu.
- prompt: Czym jest przepustowość?
  response: Przepustowość mówi, ile pracy system wykonuje w jednostce czasu.
- prompt: Podaj prostą definicję: repozytorium.
  response: Repozytorium przechowuje kod oraz historię zmian projektu.
- prompt: Czym jest checkpoint best?
  response: Checkpoint best to zapis modelu wybrany na podstawie ewaluacji, a nie tylko najnowszy zapis.
- prompt: Czym jest backup? (2)
  response: Backup to kopia danych przygotowana po to, żeby dało się je odtworzyć po awarii lub pomyłce.
- prompt: Czym jest split testowy? Odpowiedz krótko.
  response: Split testowy to część danych odłożona do końcowej oceny, bez używania jej w treningu.
- prompt: Czym jest ewaluacja jakościowa?
  response: Ewaluacja jakościowa sprawdza konkretne odpowiedzi modelu, a nie tylko liczbę loss.
- prompt: Podaj prostą definicję: dokumentacja.
  response: Dokumentacja opisuje, jak projekt działa, jak go uruchomić i jakie ma ograniczenia.
- prompt: Czym jest prompt? Prosto.
  response: Prompt to tekst wejściowy przekazany modelowi przed generacją odpowiedzi.
- prompt: Wyjaśnij krótko pojęcie: proces.
  response: Proces to uruchomiony program wraz z pamięcią i zasobami systemu.

### mini_streszczenia

- prompt: Streść w jednym zdaniu: Dobre raporty zapisują nie tylko wynik, ale też założenia i ograniczenia eksperymentu.
  response: Raport powinien opisywać wynik, założenia i ograniczenia.
- prompt: Skróć sens tekstu: Niższy loss może wyglądać dobrze, ale sample mogą pokazywać pętle i słabe odpowiedzi.
  response: Loss trzeba sprawdzać razem z jakością generacji.
- prompt: Wyciągnij najważniejszą myśl: Nie każdy problem wymaga aplikacji, kont użytkowników i dashboardu. Czasem wystarczy prosty skrypt albo plik tekstowy.
  response: Najprostsze rozwiązanie bywa wystarczające.
- prompt: Skróć tekst: W małym modelu krótki kontekst ogranicza zdolność utrzymania dłuższej wypowiedzi.
  response: Krótki kontekst ogranicza długie generacje.
- prompt: Napisz sedno tego tekstu: Nie każdy wzrost liczby parametrów rozwiązuje problemy danych.
  response: Większy model nadal zależy od jakości danych.
- prompt: Podaj krótkie streszczenie: Mały test SFT ma sprawdzić reakcję modelu, a nie stworzyć gotowego chatbota.
  response: Smoke SFT jest testem reakcji modelu.
- prompt: Streść w jednym zdaniu: Instrukcyjny tuning nie dodaje magicznej wiedzy, tylko uczy model formatu odpowiedzi.
  response: SFT poprawia format odpowiedzi, ale nie zastępuje wiedzy.
- prompt: Streść w jednym zdaniu: Najpierw warto sprawdzić, czy pipeline działa, zanim zwiększy się skalę eksperymentu.
  response: Skalę zwiększa się po sprawdzeniu pipeline’u.
- prompt: Skróć tekst: Instrukcyjny tuning nie dodaje magicznej wiedzy, tylko uczy model formatu odpowiedzi.
  response: SFT poprawia format odpowiedzi, ale nie zastępuje wiedzy.
- prompt: Streść jednym zdaniem: Niższy loss może wyglądać dobrze, ale sample mogą pokazywać pętle i słabe odpowiedzi.
  response: Loss trzeba sprawdzać razem z jakością generacji.

### mvp_first_project_advice

- prompt: Podaj rozsądny następny krok: Czy pisać testy od początku?
  response: Napisz testy dla krytycznej logiki i przypadków, które łatwo zepsuć. Nie musisz testować każdego szczegółu prototypu.
- prompt: Co zrobić, gdy projekt się rozrasta? Odpowiedz konkretnie.
  response: Odetnij funkcje poboczne i zostaw rdzeń, który można szybko sprawdzić.
- prompt: Co zrobić? Jak ograniczyć zakres projektu?
  response: Usuń wszystko, czego nie trzeba do pierwszego działającego scenariusza.
- prompt: Odpowiedz praktycznie: Czy dokumentacja jest potrzebna w małym projekcie?
  response: Tak, ale krótka. Wystarczy opis uruchomienia, decyzji i ograniczeń.
- prompt: Co zrobić? Co jest lepsze: mniej funkcji czy więcej niedokończonych?
  response: Mniej funkcji, ale działających. Niedokończone funkcje zwykle obniżają wiarygodność projektu.
- prompt: Odpowiedz praktycznie: Czy warto zmieniać stack w połowie?
  response: Tylko przy konkretnym problemie. Sama ciekawość nowej technologii zwykle opóźnia projekt.
- prompt: Czy większy zakres zwiększa szansę sukcesu? Nie rób listy.
  response: Nie zawsze. Duży zakres często utrudnia dowiezienie pierwszej działającej wersji.
- prompt: Krótko doradź: Nie wiem, czy zacząć projekt od UI czy od logiki.
  response: Zacznij od logiki i jednego prostego przepływu. UI dopracuj wtedy, gdy wiadomo już, co naprawdę ma działać.
- prompt: Krótko doradź: Jak rozbić duży projekt?
  response: Podziel go na etapy: dane, główna logika, prosty widok, test, dopiero potem dodatki.
- prompt: Co zrobić, gdy projekt się rozrasta? Zakończ naturalnie.
  response: Odetnij funkcje poboczne i zostaw rdzeń, który można szybko sprawdzić.

### not_in_dataset_style_generalization

- prompt: Czy ładna odpowiedź zawsze jest poprawna?
  response: Nie. Odpowiedź może brzmieć dobrze, ale nadal być błędna semantycznie.
- prompt: Czy model po SFT automatycznie zna więcej faktów? Odpowiedz jasno.
  response: Nie. SFT głównie uczy sposobu odpowiadania, a wiedza nadal zależy od bazy i danych.
- prompt: Czy model po SFT automatycznie zna więcej faktów? Bez marketingu.
  response: Nie. SFT głównie uczy sposobu odpowiadania, a wiedza nadal zależy od bazy i danych.
- prompt: Czy krótsza odpowiedź zawsze jest lepsza? W dwóch zdaniach.
  response: Nie zawsze. Ma być tak krótka, jak pozwala na pełną i poprawną odpowiedź.
- prompt: Czy ładna odpowiedź zawsze jest poprawna? Bez szablonu.
  response: Nie. Odpowiedź może brzmieć dobrze, ale nadal być błędna semantycznie.
- prompt: Czy repetition penalty rozwiązuje wszystkie pętle? Krótko.
  response: Nie. Może pomóc, ale dane i trening też muszą uczyć kończenia odpowiedzi.
- prompt: Czy repetition penalty rozwiązuje wszystkie pętle? W dwóch zdaniach.
  response: Nie. Może pomóc, ale dane i trening też muszą uczyć kończenia odpowiedzi.
- prompt: Czy krótsza odpowiedź zawsze jest lepsza?
  response: Nie zawsze. Ma być tak krótka, jak pozwala na pełną i poprawną odpowiedź.
- prompt: Czy warto skalować SFT po słabym smoke teście? Bez marketingu.
  response: Nie. Najpierw trzeba poprawić przyczynę błędów w danych lub ewaluacji.
- prompt: Czy model bazowy jest chatbotem? Krótko.
  response: Nie. Model bazowy głównie kontynuuje tekst, a nie musi dobrze wykonywać instrukcji.

### ostrozne_odpowiedzi

- prompt: Czy jedna metryka wystarczy? Krótko.
  response: Rzadko. Lepiej użyć kilku metryk i sprawdzić przykłady ręcznie.
- prompt: Czy test na małej próbce wystarcza? Odpowiedz ostrożnie.
  response: Wystarcza do wstępnej decyzji, ale nie do mocnego wniosku jakościowego.
- prompt: Czy wynik z jednego seeda jest pewny?
  response: Raczej nie. Dla samplingu warto sprawdzić kilka seedów.
- prompt: Czy ta diagnoza jest pewna? Wskaż ograniczenie.
  response: Bez pełnych danych można mówić tylko o najbardziej prawdopodobnym wyjaśnieniu.
- prompt: Czy trzeba robić pełny rebuild danych? Wskaż ograniczenie.
  response: Tylko jeśli obecne dane blokują dalszą poprawę albo wnoszą powtarzalne błędy.
- prompt: Czy zawsze warto wybrać szybsze rozwiązanie?
  response: Nie zawsze. Szybsze rozwiązanie ma sens, jeśli nie zwiększa zbyt mocno ryzyka i długu technicznego.
- prompt: Czy niski loss oznacza dobry model?
  response: Nie zawsze. Loss jest ważny, ale trzeba też sprawdzić jakość generacji.
- prompt: Czy brak błędu technicznego oznacza sukces? Krótko.
  response: Trening może być stabilny technicznie, ale nadal dawać słaby model.
- prompt: Czy mam zgadywać brakujące dane? Odpowiedz ostrożnie.
  response: Nie. Lepiej jasno wskazać, czego brakuje.
- prompt: Czy mam zgadywać brakujące dane?
  response: Nie. Lepiej jasno wskazać, czego brakuje.

### poprawki_tekstu

- prompt: Napisz prościej: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.
  response: Proszę o informację zwrotną w tej sprawie.
- prompt: Napisz naturalniej: Projekt został wykonany przeze mnie i działa on dobrze.
  response: Samodzielnie wykonałem projekt, który działa poprawnie.
- prompt: Skróć: Dokonano wykonania testu działania systemu.
  response: Przetestowano działanie systemu.
- prompt: Przeredaguj: Należy dokonać sprawdzenia poprawności działania programu.
  response: Trzeba sprawdzić, czy program działa poprawnie.
- prompt: Skróć i popraw: Została przeprowadzona walidacja poprawności działania systemu.
  response: Sprawdzono poprawność działania systemu.
- prompt: Skróć: Ten projekt posiada zbyt dużą ilość zaplanowanych funkcji.
  response: Ten projekt ma zbyt wiele zaplanowanych funkcji.
- prompt: Napisz naturalniej: W celu uruchomienia programu należy nacisnąć przycisk start.
  response: Aby uruchomić program, naciśnij przycisk Start.
- prompt: Przeredaguj zdanie: Ten fragment można napisać w sposób bardziej naturalny.
  response: Ten fragment można napisać naturalniej.
- prompt: Napisz naturalniej: W przypadku wystąpienia błędu należy ponownie uruchomić usługę.
  response: Jeśli wystąpi błąd, uruchom usługę ponownie.
- prompt: Usuń lanie wody: Aplikacja posiada możliwość wykonywania wielu rzeczy naraz.
  response: Aplikacja pozwala wykonywać kilka zadań jednocześnie.

### sanity_fakty_podstawowe

- prompt: Wisła to
  response: Wisła to najdłuższa rzeka w Polsce.
- prompt: Fakt różni się od opinii tym, że Jednym zdaniem.
  response: Fakt można sprawdzić, a opinia wyraża czyjąś ocenę lub pogląd.
- prompt: Stolicą Polski jest
  response: Stolicą Polski jest Warszawa.
- prompt: CPU to Naturalnie.
  response: CPU to główny procesor wykonujący instrukcje programu.
- prompt: Woda zamarza w temperaturze
  response: Woda zamarza w temperaturze około 0°C przy normalnym ciśnieniu.
- prompt: Grawitacja to Jednym zdaniem.
  response: Grawitacja to oddziaływanie, które przyciąga masy do siebie.
- prompt: Wisła to Jednym zdaniem.
  response: Wisła to najdłuższa rzeka w Polsce.
- prompt: Kilometr to Naturalnie.
  response: Kilometr to tysiąc metrów.
- prompt: Wisła to Dokończ krótko.
  response: Wisła to najdłuższa rzeka w Polsce.
- prompt: Stolicą Polski jest Jednym zdaniem.
  response: Stolicą Polski jest Warszawa.

### techniczne_proste_wyjasnienia

- prompt: Odpowiedz prosto: Czym jest learning rate?
  response: Learning rate określa, jak duży krok wykonuje optimizer przy aktualizacji wag modelu.
- prompt: Po co robi się eval na tych samych promptach?
  response: Stałe prompty pozwalają porównać checkpointy bez mieszania zmian modelu ze zmianami testu.
- prompt: Czym jest smoke test?
  response: Smoke test to krótka próba sprawdzająca, czy cały pipeline działa bez oczywistych błędów.
- prompt: W jednym akapicie: Co oznacza train loss?
  response: Train loss mierzy błąd modelu na przykładach używanych podczas treningu.
- prompt: Po co jest gradient clipping? W dwóch zdaniach.
  response: Gradient clipping ogranicza zbyt duże gradienty, żeby zmniejszyć ryzyko niestabilnego treningu.
- prompt: Czym różni się train loss od val loss? W dwóch zdaniach.
  response: Train loss mierzy dopasowanie do danych treningowych, a val loss sprawdza model na odłożonych danych.
- prompt: W jednym akapicie: Co oznacza resume treningu?
  response: Resume oznacza wznowienie treningu z checkpointu zamiast startu od zera.
- prompt: Odpowiedz prosto: Czym różni się RAM od dysku?
  response: RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera.
- prompt: Dlaczego sam loss nie wystarczy? W dwóch zdaniach.
  response: Loss jest metryką pomocniczą; generacje mogą być słabe mimo niższego loss.
- prompt: Czym jest smoke test? (2)
  response: Smoke test to krótka próba sprawdzająca, czy cały mechanizm działa bez oczywistych awarii.
