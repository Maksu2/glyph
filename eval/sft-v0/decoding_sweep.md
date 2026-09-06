# Glyph-27M SFT v0 decoding sweep

This sweep tests decoding settings only. No training was run.

- prompts: 16
- presets: 10
- best overall preset: `creative_controlled`
- recommended public-demo preset: `creative_controlled`

## Summary

| preset | usable | weak | repeat | drift | avg_sem | avg_task | avg_tok | score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `creative_controlled` | 5 | 10 | 3 | 5 | 1.50 | 1.50 | 48.1 | 24.9 |
| `balanced_current` | 4 | 12 | 4 | 5 | 1.19 | 1.19 | 54.7 | 5.2 |
| `mid_temp_anti_repeat` | 4 | 12 | 3 | 7 | 1.38 | 1.31 | 48.4 | 4.5 |
| `anti_repeat` | 4 | 12 | 5 | 7 | 1.00 | 1.06 | 51.8 | -1.2 |
| `balanced_100` | 4 | 12 | 5 | 6 | 0.94 | 1.00 | 52.7 | -1.4 |
| `strict_100` | 3 | 13 | 4 | 8 | 1.00 | 1.00 | 45.6 | -11.1 |
| `low_temp_k40` | 2 | 14 | 6 | 1 | 0.75 | 0.69 | 41.4 | -17.4 |
| `balanced_low_temp` | 2 | 14 | 3 | 6 | 1.00 | 0.94 | 45.4 | -18.3 |
| `strict_medium` | 2 | 14 | 6 | 5 | 0.88 | 0.88 | 44.9 | -25.2 |
| `strict_short` | 2 | 14 | 7 | 5 | 0.75 | 0.81 | 42.9 | -27.4 |

## Prompt-level outputs

## Preset: strict_short

Settings: `{"temperature": 0.45, "top_k": 20, "top_p": 0.85, "max_new_tokens": 60, "repetition_penalty": 1.2, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

Czy ten laptop jest dobry?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, sprawdź czy działa. Jeśli nie działa, sprawdź czy działa. Jeśli nie działa, sprawdź czy działa. Jeśli nie działa, sprawdź czy działa. Jeśli nie działa, sprawdź czy działa. Jeśli nie działa, sprawdź czy działa. Jeśli nie działa, sprawdź czy działa.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy to jest bezpieczne?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, wybierz opcję, która działa. Jeśli nie działa, wybierz opcję. Jeśli po tym dalej masz pewność, że działa. Jeśli po tym dalej masz energię, wtedy dopiero potem dokładaj kolejne elementy.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu. Najpierw zacząć od najkrótszego ruchu, który tylko działa. Najpierw zacząć od najtrudniejszego ruchu, który tylko wygląda jak najgorszy wariant. Jeśli nie wiesz, co zrobić, to poczekać.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę po tym jak dokładać kolejne elementy, a nie tylko czytać notatki. Jeśli nie ma sensu, to warto zacząć od najkrótszego ruchu. Jeśli nie działa, najlepiej zacząć od najtrudniejszych zadań. Nie chodzi o to, żeby zrobić wszystko w porządku.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test to dobry przykład, który szybko i łatwo ocenić. Nie chodzi o to, żeby oceniać te elementy. W praktyce warto sprawdzić, czy trzeba robić więcej.

Score: sem=0 task=0 coh=2 rep=1 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wyciągaj wnioski, a nie popełniaj błędów. Nie musisz oceniać tego jak dobrze wygląda. Jeśli masz problemy z czytaniem, to najpierw sprawdź, czy warto zacząć od najkrótszego ruchu.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyobraź sobie, że temperatura jest mniejsza niż temperatura. Jeśli temperatura nie zmienia koloru, to warto sprawdzić, czy temperatura jest większa. Nie musi być zbyt ciężka i trudniejszy do zrozumienia. W praktyce wystarczy czekać na odpowiedź.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź do tego jak do małego testu. Najpierw wybrać jedną kategorię, a dopiero potem ją odkładać. Najpierw wybrać jedną kategorię, a dopiero potem ją odłożyć. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu, który po tym dalej.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

czym różni się fakt, że warto zacząć od najkrótszego ruchu. W praktyce warto wybrać jedną z najbardziej popularnych opcji, a nie tylko konkretnej definicji. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Najpierw sprawdź, czy po tym dalej działa.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

sprawdź, czy pojęcie jest ważne. Jeśli nie działa, trzeba najpierw zacząć od najkrótszego ruchu, a dopiero potem dokładać kolejne elementy. Najpierw zacząć od najprostszej i najbardziej konkretnej wersji. Najpierw zacząć od najtrudniejszych zadań, które nie są w stanie zrozumieć.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego testu. Najpierw najpierw doprecyzuj kolejne elementy i wybierz jedną wersję. Jeśli po tym dalej masz energię, a nie tylko poprawkę, dopiero wtedy dokładaj kolejne elementy. Jeśli po tym dalej masz energię, to musisz zacząć od najkrótszego

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: czego nie da się oceniać bez danych?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

Odpowiedz krótko i krótko. Jeśli nie działa, to można zacząć od najkrótszego ruchu. Najpierw sprawdzić, czy działa. Najpierw sprawdzić, czy działa. Jeśli działa, rozbudujesz. Jeśli działa, to najpierw sprawdź, czy działa. Jeśli działa, rozbudowujesz. Jeśli działa, roz

Score: sem=1 task=1 coh=1 rep=2 can_win=False

## Preset: strict_medium

Settings: `{"temperature": 0.55, "top_k": 30, "top_p": 0.9, "max_new_tokens": 80, "repetition_penalty": 1.2, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

Czy ten laptop jest dobry?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Jeśli nie działa, sprawdź, czy działa, albo po jego wykonaniu.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem, który nie ma sensu w projektowaniu. Jeśli tylko masz pomysł, wybierz jedną wersję, którą chcesz zacząć. Jeśli coś działa, a nie stać się osobnym projektem, to łatwiej ocenić, czy wygląda jak najlepsza wersja.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. Jeśli nie działa, wybierz jedną kategorię, a dopiero potem rozbudowę. Jeśli po tym dalej masz energię, wtedy dokładaj kolejne elementy. Jeśli po tym dalej nie wiadomo o co chodzi.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu i po tym dalej. Najpierw zacząć od najkrótszego ruchu i dopiero wtedy, gdy pojawi się okazja. Jeśli to działa, najlepiej zacząć od najtrudniejszej rzeczy.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej, a nie tylko od podstaw. Jeśli to działa, nie ma sensu, nie wiadomo, czy trzeba robić więcej. Nie chodzi o to, żeby coś poprawić. Przy takim zadaniu najlepiej zacząć od najkrótszego ruchu, który po każdym kroku wygląda ciekawiej.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test to zwykle projekt, który tylko dobrze wygląda. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Podejdź do tego jak do małego testu, który tylko wygląda dobrze.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wyciągaj wnioski, a nie popełniać błędów. Nie musisz oceniać całej treści. Jeśli nie wiesz, co robić, dopiero wtedy masz pewność, że coś działa.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyobraź sobie, że temperatura w ciągu dnia jest większa niż temperatura w ciągu dnia. Nie oceniaj temperatury, nie oceniaj temperatury i pogody. Najpierw sprawdź, czy temperatury są bardziej jasne i dobrze wyglądające. Najpierw sprawdź, czy temperatura w ciągu dnia może być duża. W praktyce warto sprawdzić, czy temperatura w ciągu dnia powinna być mniejsza.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź na to, co dzieje się w danym miejscu. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Najpierw sprawdź, czy można poprawić. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Nie chodzi o to, żeby nie pisać i oceniać.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

czym różni się fakt, że warto zacząć od konkretnych zadań. Jeśli nie działa, można ją poczekać.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej rób z tego zadanie. Jeśli nie wiesz, co zrobić, a nie stać się osobnym projektem. Nie musisz robić z tym nic bardziejszego, niż tylko rozróżnienie zadania. Wystarczy od razu powiedzieć, jak zacząć. Najpierw zacząć od najkrótszej i najbardziej wymagającej odpowiedzi.

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego testu. Najpierw najpierw doprecyzuj kolejne elementy i wybierz te zbędną wersję. Jeśli nie działa, po tym dalej masz pewność, że coś działa. Przy takim zadaniu najlepiej zacząć od najkrótszego ruchu, który nie tylko wygląda ciekawiej.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: czego nie da się oceniać bez danych?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

Odpowiedz krótko i łatwo ocenić. Jeśli masz problem z tym, czy działaniem, a nie tylko jako język, który działa. Jeśli nie działa, sprawdź, czy działa. Jeśli nie działa, wybierz kilka powodów, dla których warto zacząć. Jeśli to działa, sprawdź, czy działa. Jeśli coś działa, sprawdź, czy działa.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

## Preset: balanced_low_temp

Settings: `{"temperature": 0.65, "top_k": 30, "top_p": 0.9, "max_new_tokens": 80, "repetition_penalty": 1.15, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

1 Nie chodzi o to, żeby laptop był dobry. Chodzi o to, aby laptop był dobry.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Podejdź do tego jak do małego testu i sprawdź, czy nie działa. Jeśli nie działa, najlepiej zacząć od najkrótszego ruchu, który nie jest wystarczającym wynikiem. Jeśli po pierwszym kroku masz pewność, że nie działa.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem, a nie własnym życiem. Jeśli tylko dobrze wygląda, można szybko ocenić, czy trzeba. Lepiej zacząć od najgorszego i najbardziej skomplikowanego zadania, a nie od najtrudniejszego zadań. Jeśli coś nie działa, łatwiej zacząć od najkrótszego ruchu, który po tym dalej będzie działał szybciej.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. Jeśli coś jest dobre, dopiero wtedy po tym dalej masz energię. Najpierw sprawdź, czy ma sens. Najpierw najpierw sprawdź, czy działa. Jeśli nie działa, pomyśl o tym, co poprawić.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do tego celu. Najpierw zacząć od najkrótszego ruchu, który jest lepszy niż najbardziej zrozumiałe. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej, a nie tylko od podstaw. Jeśli to działa, nie ma sensu, nie wiadomo, czy trzeba robić więcej. Nie wiadomo, co zrobić. Jeśli to działa, nie wiadomo, czy to działa.

Score: sem=2 task=1 coh=1 rep=2 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test może być dowodem na to, że tylko do jednego wniosku brakuje odpowiedzi. Jeśli po tym dalej masz pewność, że nie jest łatwo ocenić, co napisane zostało.

Score: sem=0 task=0 coh=2 rep=1 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wygląd z tego co napisałaś jest ważne i ważne. Nie musi być łatwo zrozumieć jak dobrze wygląda. Jeśli to działa, sprawdź, czy masz problem.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wygląd na to, że temperatura w ciągu dnia jest większa niż temperatura w ciągu dnia. Nie oceniaj temperatury, nie oceniaj temperatury i temperatury w ciągu dnia. Jeśli temperatury są bardziej jasne, wybierz się do małego pokoju.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjaśnij, gdzie jest inflacja. Ta wersja jest krótsza i czytelniejsza. Jeśli to działa, rozbudujesz. Jeśli po tym dalej masz pewność, że coś jest dobre. Najpierw najpierw musisz wiedzieć, czy trzeba robić wszystko, a dopiero potem dokładać kolejne elementy.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

Quality to system, który pozwala na tworzenie systemu. W praktyce może pomóc w zrozumienie i poprawę danych. To tylko niektóre elementy, które nie mają wpływu na jakość pracy. Nie musi być łatwo dostępne dla wszystkich. Najpierw trzeba zacząć od najkrótszego ruchu, a dopiero potem dopisać coś więcej.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej rób z tego zadanie. Jeśli nie wiesz, co robić, a nie stać się osobnym projektem. Nie musisz od razu robić z tym trudem. Jeśli po tym idziesz, dokładaj kolejne elementy. Jeśli to działa, nie wiesz, jak zrobić z nim coś. Jeśli nie wiesz, co zrobić, a nie zrobić z tym problemu, po prostu nie wiesz,

Score: sem=1 task=1 coh=1 rep=1 can_win=False

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego projektu. Jeśli projekt używa AI, to najpierw wybierz język i rozbudowę. W praktyce warto zacząć od najkrótszego ruchu. Najpierw zacząć od najprostszego ruchu, który po tym dalej. Wtedy trzeba zrobić wszystko w porządku. Jeśli nie działa, najlepiej zacząć od najkrótszego ruchu.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest backup?

Score: sem=0 task=0 coh=0 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: dlaczego nie da się oceniać bez danych?

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

(empty)

Score: sem=0 task=0 coh=0 rep=0 can_win=False

## Preset: balanced_current

Settings: `{"temperature": 0.75, "top_k": 40, "top_p": 0.92, "max_new_tokens": 120, "repetition_penalty": 1.15, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

1 Nie chodzi o to, żeby laptopy były dobre. Chodzi o to, by te laptopa były lepsze niż laptopy. Nie chodzi o to, żeby nie wyglądało lepiej niż mało poprawnie. Lepiej zacząć od mniejszych pokładów i lepiej zacząć od najtrudniejszego elementu. Przy takim opisie trzeba robić więcej.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Podejdź do tego jak do małego działu, który zwykle się zmienia i nie czekaj na kolejne kolejne elementy. Jeśli po tym dalej masz problem, wybierz część. W praktyce warto zacząć od najkrótszego ruchu. Po pierwszym kroku trzeba zrobić coś ciekawego i konkretnego.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem i miejscem, w którym się znajduje? Nie. Jeśli tylko masz pomysł, który tylko zależy od tego, czy chcesz, szybko i szybko zacząć, musisz wybierać. W praktyce warto wybrać coś dla siebie. Przy takim zadaniu najlepiej wybrać trzy elementy. Najpierw sprawdź, czy prosty wariant ma sens, ale dopiero wtedy rozbudujesz.

Score: sem=2 task=3 coh=2 rep=1 can_win=True

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego rozdziału. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. W praktyce warto wybrać dwie najważniejsze elementy. Jeśli masz pewność, że działa lepiej niż wielki plan, dopiero wtedy dokładaj kolejne elementy. Jeśli po tym dalej nie idzie, warto zacząć od najprostszego ruchu.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do tego celu. Najpierw zacząć od najkrótszego ruchu, który jest lepszy niż początek. W praktyce warto znać tylko kilka rzeczy, nawet jeśli wygląda mniej profesjonalnie. Jeśli nie ma problemu, zrób więcej.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

deklaracja to odpowiedź na pytanie, czy tekst ma sens. To jest wersja zdania, nie musi być osobna. Jeśli coś tu działa, trzeba najpierw zacząć, a dopiero potem zacząć. Najpierw musisz robić więcej, a dopiero potem zacząć.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test może być dowodem dla wszystkiego, nawet jeśli nie masz pojęcia o tym, czy tylko to działa. Nie chodzi tu o to, żebyś wiedział, co zrobić. To tylko kilka rzeczy, które można robić dalej.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wygląd z tego co dzieje się w danej chwili jest ważne, a nie zawsze niekoniecznie musi być zrozumiałe. W praktyce warto najpierw robić to po każdym kroku, a dopiero później robić więcej. Jeśli nie masz czasu na zmianę i zacznij od najkrótszego ruchu. Podejdź do tego jak do małego pytania, który rozbudowuje działanie.

Score: sem=2 task=2 coh=2 rep=1 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyjazd do Hiszpanii jest krótszy niż w przypadku najkrótszego ruchu drogowego. Najgorszy wariant to: zrobić więcej i więcej niż jedną odpowiedź. Jeśli nie masz problemu z tym, co dzieje się w danym mieście, najlepiej zacząć od najdłuższego ruchu drogowego.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjaśnij, gdzie jest inwigilacja. Nie trzeba tu być pewnym. To jest proces, w którym infekcja tocząca się po każdym dniu może stać się jedną z najbardziej niebezpiecznych sytuacji. Jeśli nie wiesz, co robić, wybierz coś więcej. Najpierw sprawdź, czy intuicyjne są ważne rzeczy, które dopisane są na podstawie danych.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

Quality to system, który pozwala na tworzenie systemu. W praktyce może pomóc w znalezieniu najbezpieczniejszego elementu bez końca. Przy takim systemie można zacząć od najkrótszego ruchu i czasu działania, a nie tylko poprawienia systemu. Dzięki temu można poprawić wygląd, poprawić kształt i działanie. Ta wersja to idealna motywacja.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej testuję. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Jeśli po tym dalej masz energię, rozbudujesz. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Jeśli po tym dalej masz energię, to najpierw musisz znać działanie.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego projektu. Jeśli projekt używa AI, to najpierw wybierz język i powtórki. Wtedy po tym dalej masz problem. Warto wybrać wersję testową, ale w takim przypadku nie wiadomo.

Score: sem=2 task=1 coh=3 rep=0 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest backup? Jeśli nie działa, wystarczy wysłać wiadomość do użytkownika. Przy takim zadaniu nie trzeba się nad tym martwić. To wystarczy, gdy dana wersja to wersja działa.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: dlaczego nie da się oceniać bez danych?

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

(empty)

Score: sem=0 task=0 coh=0 rep=0 can_win=False

## Preset: anti_repeat

Settings: `{"temperature": 0.55, "top_k": 20, "top_p": 0.85, "max_new_tokens": 80, "repetition_penalty": 1.25, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

Czy ten laptop jest dobry?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Jeśli nie działa, sprawdź, czy jest działający. Jeśli po tym dalej masz energię, sprawdź, czy działa. Jeśli po tym dalej masz energię, wybierz jedną wersję. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem, który nie ma sensu w projektowaniu. Jeśli nie masz pomysłu na planowanie i rozbudowę, a nie działaniem, które nie działa. W praktyce warto najpierw zacząć od najkrótszego ruchu, a dopiero potem doprecyzować coś konkretnego.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, wybierz jeden z nich. Jeśli po tym dalej masz energię, a dopiero potem dokładaj kolejne elementy. Najpierw sprawdź, czy ma być sensowna kolejność. Jeśli nie działa, najlepiej zacząć od najkrótszego ruchu.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu i po tym dalej. Najpierw zacząć od najkrótszego ruchu, który ma być bardziej skomplikowany niż najbardziej skomplikowane zadanie. Najpierw zacząć od najtrudniejszej rzeczy, a nie tylko logiki. Jeśli nie działa poprawnie, wybierz jedną z najlepszych wersji.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej. Nie próbuj odkładać wszystkiego naraz. Jeśli nie masz pojęcia, co zrobić, a czego nie robić. Najpierw zacząć od najkrótszego ruchu, który tylko wygląda lepiej niż realny efekt. W praktyce warto zacząć od najtrudniejszych zadań.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test to test, który jest lepszy niż wielki test. Nie chodzi o to, żeby oceniać te elementy jako pierwszy. To jest wersja, która jest mniejsza.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wyciągaj wnioski, a nie popełniać błędów. Nie musisz oceniać tego jak dobrze wygląda. Jeśli masz problemy z czytaniem, to najpierw sprawdź, czy warto zacząć od najkrótszego ruchu.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyobraź sobie, że temperatura w ciągu dnia jest większa niż temperatura w ciągu dnia. Nie musi być zbyt duża, ale nie trzeba robić więcej niż jedną godzinę. Jeśli temperatura w ciągu dnia może być mniejsza, można go szybko poprawić. Jeśli temperatura w ciągu dnia powinna przekraczać 20-30 stopni Celsjusza, warto zacząć od najkrótszego ruchu.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź do tego jak do małego testu. Jeśli masz energię, dopiero wtedy, gdy dokładasz kolejne elementy. Jeśli to działa, sprawdź, czy można poprawić. Jeśli nie działa, sprawdź, czy działa. Jeśli nie działa, sprawdź, czy działa. Jeśli nie działa, sprawdź, czy działa.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

czym różni się fakt, że warto zacząć od konkretnej oceny. Jeśli nie działa poprawnie, najlepiej zacząć od najkrótszego ruchu. Najpierw sprawdzić, czy problem jest taki sam, a dopiero potem dokładać kolejne elementy. W praktyce warto zacząć od najprostszej analizy i poprawy jakości pracy. Nie chodzi o to, żeby ocenić, czy problem jest lepszy.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

sprawdź, co poprawić. Najpierw zacząć od prostej i konkretnej definicji. W praktyce warto sprawdzić, czy problem jest ważny. Jeśli nie działa, najlepiej zacząć od najkrótszego ruchu, który realnie coś zmienia. To wystarczy do tego czasu, a dopiero potem dokładać kolejne elementy. Jeśli to działa, wybierz jedną wersję, która usuwa największą poprawkę.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego testu. Najpierw najpierw doprecyzuj kolejne elementy i wybierz te zbędną wersję. Jeśli nie działa, po tym dalej masz pewność, że coś działa. Przy takim zadaniu najlepiej zacząć od najkrótszego ruchu, który nie tylko wygląda ciekawiej.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: czego nie da się oceniać bez danych?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

Odpowiedz krótko i łatwo ocenić. Jeśli masz problem z tym, czy działaniem, a nie tylko jako element docelowy. Najpierw sprawdź, czy działa, ale nie wiadomo, czy działa. Jeśli to działa, przynajmniej na razie, nie wiedziałeś w co chodzi.

Score: sem=3 task=3 coh=3 rep=0 can_win=True

## Preset: strict_100

Settings: `{"temperature": 0.45, "top_k": 30, "top_p": 0.9, "max_new_tokens": 100, "repetition_penalty": 1.2, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

Czy ten laptop jest dobry?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, sprawdź czy nie działa. Nie trzeba od razu robić porządnego testu i po tym dalej. Najpierw zacząć od najkrótszego ruchu, który tylko działa. Jeśli nie działa, można poprawić. Jeśli nie działa, lepiej zacząć od najtrudniejszych zadań.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy to jest bezpieczne?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, wybierz jeden z nich. Jeśli po tym dalej masz energię, a dopiero potem dokładaj kolejne elementy. Jeśli nie działa, sprawdź, czy ma sens.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu. Najpierw zacząć od najkrótszego ruchu, który tylko działa. Najpierw zacząć od najtrudniejszego ruchu, który tylko wygląda na prostą i ciekawą wersję. Jeśli nie wiesz, co zrobić, to poczekać.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły. Najpierw zacząć od najkrótszego ruchu, który tylko dobrze wygląda. Najpierw zacząć od najtrudniejszych zadań, a dopiero potem dokładać kolejne elementy. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Nie chodzi o to, żeby po pierwszym kroku projekt był lepszy.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test to test, który jest lepszy niż wielki test. Nie chodzi o to, żeby oceniać te elementy. W praktyce oznacza to, że trzeba ocenić, czy te elementy mają sens.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wyciągaj wnioski, a nie popełniać błędów. Nie musisz oceniać tego jak dobrze wygląda. Jeśli masz problemy z czytaniem, to najpierw sprawdź, czy warto zacząć od najkrótszego ruchu.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyobraź sobie, że temperatura w ciągu dnia jest większa niż temperatura w ciągu dnia. Nie chodzi o to, żeby nie powiedzieć, co robić, a czego nie robić. Jeśli coś jest ważne, warto zacząć od najkrótszego ruchu, który po tym dalej. Lepiej zacząć od najtrudniejszych rzeczy, które są dobre i skuteczne.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź do tego jak do małego testu. Najpierw wybrać jedną kategorię, a dopiero potem ją odkładać. Najpierw wybrać jedną kategorię, a dopiero potem ją odłożyć. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu, który po tym dalej.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

czym różni się fakt, że warto zacząć od najkrótszego ruchu. W praktyce warto wybrać jedną z najbardziej popularnych opcji, a nie tylko konkretnej definicji. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Najpierw sprawdź, czy po tym dalej działa.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

sprawdź, czy pojęcie jest ważne. Jeśli nie działa, trzeba najpierw zacząć od najkrótszego ruchu, a dopiero potem dokładać kolejne elementy. Najpierw zacząć od najprostszej i najbardziej konkretnej wersji. Najpierw zacząć od najtrudniejszych zadań, które nie są w stanie zrozumieć.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego testu. Najpierw najpierw doprecyzuj kolejne elementy i wybierz te zbędne. Jeśli nie działa, wybierz tester, który działa. Najpierw musisz wiedzieć, co zrobić, a nie robić. Jeśli masz problemy z projektem, wybierz tester.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: czego nie da się oceniać bez danych?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

Odpowiedz krótko i krótko. Jeśli nie działa, to można zacząć od najkrótszego ruchu. Najpierw sprawdzić, czy można robić więcej. W praktyce warto zacząć od najtrudniejszych zadań. Najpierw zacząć od najgorszej rzeczy, a dopiero potem dokładać kolejne elementy. Nie chodzi o to, żeby po dzisiejszym dniu zareagować na konkretne pytania.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

## Preset: low_temp_k40

Settings: `{"temperature": 0.55, "top_k": 40, "top_p": 0.92, "max_new_tokens": 80, "repetition_penalty": 1.15, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

Czy ten laptop jest dobry?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Jeśli nie działa, wybierz jedną wersję. Nie chodzi o to, żeby nie powiedzieć, co zrobić. Jeśli nie działa, rozbudujesz. Jeśli nie działa, musisz znać język.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy to działa? Oceń to, czy działa. Jeśli działa, sprawdź, czy działa. Jeśli nie działa, sprawdź, czy działa. Jeśli działa, sprawdź, czy działa. Jeśli działa, sprawdź, czy działa. Jeśli działa, sprawdź, czy działa. Jeśli działa, sprawdź, czy działa.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. Jeśli nie działa, dopóki nie pojawi się informacja, dopiero wtedy można ją przetłumaczyć.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu. Najpierw zacząć od najkrótszego ruchu, który tylko działa. Najpierw zacząć od najtrudniejszego ruchu, który tylko wygląda na prostą i ciekawą wersję.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej, a nie tylko od podstaw. Jeśli to działa, nie ma sensu, nie wiadomo, czy trzeba robić więcej. Nie chodzi o to, żeby coś poprawić. Przy takim zadaniu najlepiej zacząć od najkrótszego ruchu, który po każdym kroku wygląda ciekawiej.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test to idealna kolejność i szybkość. Nie chodzi o to, żeby zacząć od najkrótszego ruchu. W praktyce oznacza to, że coś jest ważne.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wyciągaj wnioski, a nie popełniaj błędów. Nie musisz oceniać całej treści. Jeśli nie wiesz, co robić, dopiero wtedy masz pewność, że coś działa.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyobraź sobie, że temperatura w ciągu dnia jest większa niż temperatura w ciągu dnia. Nie oceniaj temperatury, nie oceniaj temperatury i temperatury w ciągu dnia. Jeśli temperatura w ciągu dnia jest większa niż temperatura w ciągu dnia, to najlepiej zacząć od najkrótszego ruchu, który powinien być krótszy. Jeśli temperatura w ciągu dnia jest mniejsza niż temperatura w ciągu dnia, nie musi być duża.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjaśnij, gdzie jest inflacja. Jeśli to działa, można ją wyłączyć. Jeśli to działa, rozbudujesz. Jeśli to działa, rozbudowujesz. Jeśli to działa, realnie wiesz. Jeśli to działa, rozbudujesz. Jeśli to działa, szybko wiesz.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

czym różni się fakt, że warto zacząć od konkretnych zadań. Jeśli nie działa, można ją poczekać.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej rób z tego zadanie. Jeśli nie wiesz, co zrobić, a nie stać się osobnym projektem. Nie musisz robić z tym nic bardziejszego, niż tylko rozróżnienie zadania. Wystarczy odróżnić jedną kategorię od konkretnej opcji. Jeśli nie wiesz, co zrobić, to od razu ją odkładaj.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego testu. Najpierw najpierw doprecyzuj kolejne elementy i wybierz te, które są ważne. Jeśli nie działa, po tym dalej masz pewność, że coś działa. Przy takim zadaniu najlepiej zacząć od najkrótszego ruchu, który nie tylko wygląda ciekawiej.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest backup?

Score: sem=0 task=0 coh=0 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: dlaczego nie da się oceniać bez danych?

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

(empty)

Score: sem=0 task=0 coh=0 rep=0 can_win=False

## Preset: mid_temp_anti_repeat

Settings: `{"temperature": 0.65, "top_k": 20, "top_p": 0.85, "max_new_tokens": 80, "repetition_penalty": 1.25, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

Czy ten laptop jest dobry?

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Jeśli nie działa, sprawdź czy po tym działa, przynajmniej na kilka sposobów.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem, który nie ma sensu w projektowaniu. Jeśli tylko masz pomysł, wybierz jedną wersję i dopiero wtedy dokładaj kolejne elementy. Jeśli nie działa, sprawdź jak wygląda, a nie działa. Jeśli po tym dalej nie działa, sprawdź, czy można go poprawić.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. W praktyce warto wybrać taki sam element. Jeśli nie masz zbyt wielu elementów, wybierz jedną wersję. Najpierw wybierz jedną wersję. Najpierw najpierw sprawdź, czy ma być prosty. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu i po tym dalej. Najpierw zacząć od najkrótszego ruchu i dopiero wtedy, gdy pojawi się okazja. Jeśli to działa, najlepiej zacząć od najtrudniejszej rzeczy.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej, a nie tylko od podstaw. Jeśli to działa, nie ma sensu, nie wiadomo o co chodzi. To wystarczy. Nie trzeba się martwić, bo nie wiadomo, czy trzeba robić więcej. Przy takim zadaniu trzeba najpierw zacząć, po tym dalej.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test może być lepszy niż zwykły test. Jeśli chodzi o teorię, można zacząć od konkretnego zdania, a nie tylko oceniać go na podstawie materiału.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wygląd jest lepszy niż wielki, ale zły, ale bez sensu. Jeśli to działa, szybko wiesz, co poprawić. W praktyce warto najpierw sprawdzić, czy coś jest ważne i nie wiadomo o tym.

Score: sem=2 task=3 coh=2 rep=1 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wygląd na to, że temperatura w ciągu dnia jest większa niż temperatura w całym dniu. Nie musi być zbyt duża. Jeśli temperatura zmienia się w powietrzu, wtedy temperatura powinna przekraczać 30 stopni Celsjusza. W praktyce warto zacząć od najtrudniejszego ruchu. Przy takim zadaniu najlepiej zacząć od najkrótszych zadań.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź na to, czy dokładaj kolejne elementy w zależności od tego co ma być. Jeśli nie działa, wybierz jedną wersję i wybierz jedną wersję. Jeśli po tym dalej masz energię, sprawdź, czy działa. Jeśli nie działa, rozbudujesz. Jeśli nie działa, musisz znać.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

Quality to system, który pozwala na zmianę systemu. W praktyce można wybrać jedną wersję, albo drugą wersję, a nie tylko nową wersję. Nie chodzi o to, żeby nie przesadzać z innymi tematami. Przy takim zadaniu najlepiej zacząć od konkretnej wersji i po jego wykonaniu sprawdzić, czy jest sensowny.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej rób z tego zadanie. Jeśli nie wiesz, co robić, a czego unikać. W praktyce warto wybrać jedną kategorię. Jeśli nie działasz, najlepiej zacząć od najkrótszego ruchu. Najpierw dopisać elementy i rozróżnienie całej definicji.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego projektu. Jeśli projekt używa AI, to najpierw wybierz język i rozbudowę. Jeśli po tym dalej masz energię, a nie stać się osobnym projektem. Nie musisz robić więcej niż trzy elementy. Najpierw sprawdź, czy projektant ma możliwość wyboru najbardziej konkretnego zadania.

Score: sem=2 task=1 coh=2 rep=1 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: dlaczego nie da się oceniać bez danych?

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

Odpowiedz krótko i łatwo ocenić. Jeśli masz problem z tym projektem, nie musisz czekać na konkret. To jest najkrótsza kolejność. Jeśli chcesz zacząć od najtrudniejszego ruchu, to po pierwszym kroku łatwiej ocenić. Podejdź do tego jak do małego testu. Jeśli po pierwszym kroku masz energię, dopiero wtedy sprawdź, czy po drugim kroku działa szybciej.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

## Preset: balanced_100

Settings: `{"temperature": 0.65, "top_k": 40, "top_p": 0.92, "max_new_tokens": 100, "repetition_penalty": 1.2, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

1 Nie chodzi o to, żeby laptopy były dobre. Chodzi o to, by te laptopa były lepsze niż laptopy. Nie chodzi o to, żeby nie wyglądało lepiej niż mało poprawnie. Lepiej zacząć od najkrótszego ruchu na rynku pracy i w ogóle robić więcej. Najlepiej od razu sprawdzić, czy system działa lepiej niż komputer.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Podejdź do tego jak do małego testu i sprawdź, czy nie działa. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy. Jeśli po tym dalej nie wiadomo, czy nadal działa. Jeśli po tym dalej nie wiadomo, co zrobić, to po jego wykonaniu coś zdziała.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem i miejscem pracy, a nie tylko organizacją. Jeśli tylko masz pomysł na coś innego, przynajmniej po to, żebyś mógł ocenić, czy trzeba. W praktyce warto zacząć od najgorszego ruchu, który wygląda jak prosty plan. Nie chodzi o to, żeby zrobić więcej. Jeśli nie ma zbyt małego problemu z pomocą, najlepiej zrobić mały test na poziomie.

Score: sem=0 task=0 coh=2 rep=1 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. W praktyce warto wybrać taki sam element. Jeśli nie masz zbyt wielu elementów, wybierz jedną wersję. W praktyce warto wybrać trzy elementy, które można rozwiązać bez konieczności użycia narzędzi.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do małego testu i po tym od razu zacząć od najkrótszego ruchu. Najpierw musisz wiedzieć, co zrobić, a nie zrobić zbędnej analizy. Jeśli masz problem z własnym życiem, wtedy dopiero potem dokładaj kolejne elementy. Przy takim zadaniu najlepiej odpowiedzieć na pytanie, czy trzeba robić więcej.

Score: sem=1 task=1 coh=2 rep=1 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej, a nie tylko podstawę języka. Jeśli to działa, rozbudujesz. Jeśli coś działa, rozbudowujesz. Podejdź do tego jak do małego testu, który to działa. Nie chodzi o to, żebyś mógł zacząć od najkrótszego ruchu.

Score: sem=0 task=0 coh=2 rep=1 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test może być dowodem dla wszystkiego, nawet jeśli jest zbyt ciężki, ale tylko taki sam efekt. Nie chodzi o to, żeby zrobić coś zupełnie inaczej.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wygląd z tego co napisałaś jest ważne i ważne. Nie musi być łatwo zrozumieć jak dobrze wygląda. Jeśli to działa, sprawdź, czy masz problem.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyjazd do Hiszpanii jest krótszy niż w przypadku najkrótszego ruchu drogowego. Najgorsze są tu informacje o tym, jak wygląda sytuacja w Hiszpanii. Jeśli po raz pierwszy coś zmienia, można ją zobaczyć dopiero wtedy, gdy tylko pojawi się okazja. W praktyce warto sprawdzić, czy jest sensowny, ale i bardziej konkretny.

Score: sem=2 task=2 coh=2 rep=1 can_win=True

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź na to, czy dokładaj kolejne elementy w zależności od tego co ma być. Jeśli nie działa, wybierz jedną wersję i wybierz jedną wersję. To zależy od konkretnej wersji. Oceń wersję, która ma pomóc zrozumieć, co ma być. Jeśli po tym dalej masz energię, a nie stać się osobnym projektem. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy.

Score: sem=0 task=0 coh=0 rep=3 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

Quality to system, który pozwala na tworzenie systemu. W praktyce może pomóc w zrozumienie i poprawę danych. To tylko niektóre z metod, które mają sens. Jeśli nie masz czasu, a dopiero wtedy wiesz, co poprawić. Najpierw zacząć od najkrótszego ruchu, po którym widać konsekwencję.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej rób z tego plan. Jeśli nie wiesz, co zrobić, a nie stać się osobnym projektem. Nie musisz robić z tym nic bardziejszego, niż tylko rozróżnienie zadania. Wystarczy odczekać do końca i sprawdzić, co w niej jest ważne.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego projektu. Jeśli projekt używa AI, to najpierw wybierz język i powtórki. W praktyce warto zacząć od najkrótszego ruchu. Oceń to, czy działa poprawnie. Jeśli po tym dalej masz energię, dopiero wtedy dokładaj kolejne elementy.

Score: sem=2 task=1 coh=1 rep=2 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: dlaczego nie da się oceniać bez danych?

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

(empty)

Score: sem=0 task=0 coh=0 rep=0 can_win=False

## Preset: creative_controlled

Settings: `{"temperature": 0.75, "top_k": 30, "top_p": 0.9, "max_new_tokens": 100, "repetition_penalty": 1.25, "seed": 2026, "no_repeat_ngram_size": 0}`

### 01. brak_danych

Prompt: Czy ten laptop jest dobry?

1 Nie chodzi o to, żeby laptopy były dobre. Chodzi o to, by te laptopa były lepsze niż laptopy. Nie chodzi o to, żeby nie wyglądało lepiej niż mało poprawnie. Lepiej zacząć od mniejszych pokładów i dopiero wtedy dokładać kolejne elementy.

Score: sem=0 task=0 coh=1 rep=2 can_win=False

### 02. brak_danych

Prompt: Czy powinienem to kupić?

Czy warto kupić? Jeśli nie działa, wybierz jedną wersję. Podejdź do tego jak do małego testu i sprawdź, czy nie działa. Jeśli po tym dalej masz energię, dopiero wtedy rozbudujesz. Nie musi być łatwo, nawet jeśli wiesz, co zrobić.

Score: sem=1 task=1 coh=1 rep=2 can_win=False

### 03. brak_danych

Prompt: Czy to jest bezpieczne?

Czy można robić więcej, a nie stać się osobnym projektem i miejscem pracy, a nie tylko projekcją. Jeśli tylko masz pomysł na coś innego, przynajmniej po to, żebyś mógł ocenić, czy trzeba go od razu zobaczyć. W praktyce trzeba zacząć od najkrótszego ruchu w obrębie danej branży. To wystarczy, bo ma sens. Jeśli nie wiesz jak działa, dokładaj kolejne elementy.

Score: sem=0 task=0 coh=3 rep=0 can_win=False

### 04. pisanie_i_poprawianie

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Podejdź do tego jak do małego testu. Jeśli to działa, najlepiej zacząć od najkrótszego ruchu. W praktyce warto wybrać taki sam element. Nie trzeba się martwić o konkretny krok, który dobrze wygląda. Dobry przykład to nie tylko poprawka. Lepiej zacząć od najtrudniejszej rzeczy.

Score: sem=2 task=3 coh=1 rep=2 can_win=True

### 05. pisanie_i_poprawianie

Prompt: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Podejdź do tego jak do konkretnego problemu. Jeśli nie działa, po tym, czy jest sensowna odpowiedź, warto najpierw ocenić, co ma zrobić, a nie być prostym językiem.

Score: sem=2 task=1 coh=3 rep=0 can_win=False

### 06. pisanie_i_poprawianie

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

dę od tego jak do szkoły podstawowej, a nie tylko podstawę języka. Ta wersja może być przydatna do nauki i późniejsza do zmiany w przepisach. Jeśli nie działa, można powiedzieć, co robić, a czego nie zrobić. To ważne, bo trzeba zacząć od najkrótszego ruchu.

Score: sem=2 task=1 coh=3 rep=0 can_win=False

### 07. streszczanie

Prompt: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

steczkowy test może być dowodem dla wszystkiego, nawet jeśli jest zbyt ciężki, ale tylko taki wariant. W praktyce oznacza to jednak, ze nie da się tego zrobić.

Score: sem=2 task=3 coh=3 rep=0 can_win=True

### 08. streszczanie

Prompt: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

Wygląd z tego co dzieje się w danej chwili jest ważne, a nie zawsze niekoniecznie musi być zrozumiałe. W praktyce warto najpierw sprawdzić jak ważne są elementy, które mają pomóc ocenić.

Score: sem=2 task=3 coh=2 rep=1 can_win=True

### 09. proste_wyjasnienia

Prompt: Wyjaśnij prosto, czym różni się pogoda od klimatu.

Wyjazd do Hiszpanii jest krótszy niż w przypadku najkrótszego ruchu drogowego. Najgorsze są tu informacje o tym, jak wygląda sytuacja w Hiszpanii. Jeśli po raz pierwszy coś zmienia i ma sens, niech będzie lepszy niż wielki krok do tego. W praktyce warto sprawdzić, czy jest lepsze rozwiązanie niż mały krok do tego.

Score: sem=2 task=2 coh=2 rep=1 can_win=True

### 10. proste_wyjasnienia

Prompt: Wyjaśnij, czym jest inflacja.

Wyjdź na to, czy dokładaj kolejne elementy w zależności od tego co ma być. Jeśli nie działa, wybierz sens i definicję. Przykład można wybrać dowolną liczbę. Jeśli użytkownik ma swój cel, najlepiej ją założyć, a nie robić nic złego. Jeśli nie działa, po tym dalej masz energię.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 11. proste_wyjasnienia

Prompt: Czym różni się fakt od opinii?

Quality to system, który pozwala na tworzenie systemu. W praktyce może pomóc w zrozumienie i poprawę danych. Nie tylko można zacząć, ale również robić wszystko w sensownej formie. Jeśli użytkownik ma problem z napisaniem tej opinii, najlepiej rozbudować temat.

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 12. decyzje_projektowe

Prompt: Mam zacząć projekt od UI czy od logiki?

zwiń dalej rób z tego zadanie. Jeśli nie wiesz, co robić, najlepiej zacząć od małego ruchu w głowie. W praktyce warto wybrać jedną kategorię, a dopiero potem rozróżnić trzy główne elementy. Oceń to po każdym kroku. Najpierw musisz znać język i zdanie.

Score: sem=3 task=3 coh=2 rep=1 can_win=True

### 13. korekta_zalozen

Prompt: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

Podejdź do tego jak do małego projektu. Jeśli projekt używa AI, to najpierw wybierz język i powtórki. W praktyce wystarczy zacząć od najkrótszego ruchu. Oceń działanie, które działa. Przy takim zadaniu łatwiej ocenić, czy warto robić więcej.

Score: sem=2 task=1 coh=3 rep=0 can_win=False

### 14. techniczne_proste

Prompt: Czym jest backup?

czym jest back topic?

Score: sem=1 task=1 coh=3 rep=0 can_win=False

### 15. anty_petle

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych?

Odpowiedz krótko: dlaczego nie da się oceniać bez danych?

Score: sem=3 task=3 coh=3 rep=0 can_win=True

### 16. anty_petle

Prompt: Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

(empty)

Score: sem=0 task=0 coh=0 rep=0 can_win=False
