# Glyph-27M SFT v0 samples

- checkpoint: `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`
- settings: `{"temperature": 0.75, "top_k": 40, "top_p": 0.92, "max_new_tokens": 120, "repetition_penalty": 1.15, "seed": 2026, "no_repeat_ngram_size": 0}`

## 01. brak_danych

**Prompt:** Czy ten laptop jest dobry?

**Output:**

1 Nie chodzi o to, żeby laptopy były dobre. Chodzi o to, by te laptopa były lepsze niż laptopy. Nie chodzi o to, żeby nie wyglądało lepiej niż mało poprawnie. Lepiej zacząć od mniejszych pokładów i lepiej zacząć od najtrudniejszego elementu. Przy takim opisie trzeba robić więcej.

**Score:** IF=1 coherence=1 repetition=2 usefulness=1 total=1

## 02. brak_danych

**Prompt:** Czy ten wynik jest poprawny?

**Output:**

Czy ten wynik jest poprawny?

**Score:** IF=1 coherence=3 repetition=0 usefulness=1 total=5

## 03. brak_danych

**Prompt:** Czy to jest bezpieczne?

**Output:**

Czy można robić więcej, a nie stać się osobnym projektem i miejscem, w którym się znajduje? Nie. Jeśli tylko masz pomysł, który tylko zależy od tego, czy chcesz, szybko i szybko zacząć, musisz wybierać. W praktyce warto wybrać coś dla siebie. Przy takim zadaniu najlepiej wybrać trzy elementy. Najpierw sprawdź, czy prosty wariant ma sens, ale dopiero wtedy rozbudujesz.

**Score:** IF=3 coherence=2 repetition=1 usefulness=3 total=7

## 04. brak_danych

**Prompt:** Czy powinienem to kupić?

**Output:**

Jeśli po tym dalej nie wiadomo, co zrobić, a co zrobić, a co zrobić. Jeśli po tym dalej nie wiadomo, co robić. W praktyce wystarczy kilka minut później nadać się tej funkcji, a dopiero potem dopisać kolejne elementy.

**Score:** IF=1 coherence=0 repetition=3 usefulness=0 total=-2

## 05. brak_danych

**Prompt:** Czy moja odpowiedź jest dobra?

**Output:**

Czy to jest taki krok do celu, który z łatwością może odróżnić działanie. Jeśli jest sensowny, to warto najpierw ocenić, czy da się ją odróżnić. Jeśli po tym nie ma problemu, wtedy nie wiadomo, co poprawić. W praktyce wystarczy zrobić kilka błędów. Najpierw trzeba wiedzieć, czy wszystko działa. To, że to działa nie tylko na człowieka, ale i na innych. Nie chodzi o to, żeby zrobić więcej.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 06. pisanie_i_poprawianie

**Prompt:** Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

**Output:**

Podejdź do tego jak do małego tekstu, a dopiero potem dopisać kolejne elementy. Jeśli ma być taki sam, a nie inny element, to po tym dalej działa. Przy pierwszym kroku, po każdym kroku, można ocenić, czy wystarczy.

**Score:** IF=1 coherence=3 repetition=0 usefulness=1 total=5

## 07. pisanie_i_poprawianie

**Prompt:** Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

**Output:**

po takim wykonaniu można ocenić, czy to działa. To jest tylko kwestia stylu, sposobu myślenia i logiki. Jeśli po tym nie wiadomo, co zrobić, od razu będzie wyglądało lepiej.

**Score:** IF=1 coherence=3 repetition=0 usefulness=1 total=5

## 08. pisanie_i_poprawianie

**Prompt:** Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.

**Output:**

dę wtedy od razu po tym, jak ją odkłada. Nie wiem, co dalej. Po tym, jak zmieni się rzeczywistość, pojawi się odpowiedź, a nie coś, co tylko wyglądałoby lepiej.

**Score:** IF=1 coherence=2 repetition=1 usefulness=1 total=3

## 09. pisanie_i_poprawianie

**Prompt:** Skróć tekst: Ten projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.

**Output:**

z tego trzeba zacząć. Wtedy po tym dalej można zacząć. W praktyce warto zacząć od najkrótszego ruchu, który ma sens, a nie więcej niż jednej myśli. Jeśli po tym dalej masz energię, dopiero wtedy dopiero potem dokładaj kolejne elementy.

**Score:** IF=1 coherence=1 repetition=2 usefulness=1 total=1

## 10. pisanie_i_poprawianie

**Prompt:** Napisz neutralną wiadomość, że nie mogę dziś przyjść.

**Output:**

dę do lekarza, który nie jest w stanie odpowiedzieć. Ta wersja byłaby wystarczająca. Nie jest to pierwszy wariant, ale mały problem. Chodzi o to, żeby ocenić, czy jest sens. Lepiej sprawdzić, czy istnieje możliwość zmiany zdania i odpowiedzi. Jeśli nie wiadomo, jak wygląda sytuacja, trzeba poczekać.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 11. streszczanie

**Prompt:** Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.

**Output:**

ż nie wiadomo, czy projekt ma sens, ale nie stać się osobnym projektem, który po tym dalej działa. Nie wiadomo, co to jest pomysł.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 12. streszczanie

**Prompt:** Streść w dwóch zdaniach: Nie każdy problem wymaga aplikacji, kont użytkowników i dashboardu. Czasem wystarczy prosty skrypt, plik tekstowy albo arkusz.

**Output:**

Streszczenie może być przydatne do użycia. Jeśli tylko działa, to musisz wiedzieć, co poprawić. Jeśli masz problemy z plikiem, nie znaczy, że trzeba szybko od razu zacząć.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 13. streszczanie

**Prompt:** Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.

**Output:**

Wygląd jest lepszy niż poprawka. Jeśli po tym dalej masz pewność, że coś do końca nie trafi, ale łatwo zacząć od najtrudniejszego zadania. Warto wiedzieć, jak ważne jest zrozumienie konkretnej myśli.

**Score:** IF=3 coherence=2 repetition=1 usefulness=3 total=7

## 14. streszczanie

**Prompt:** Streść tekst: Najpierw trzeba zbudować działający prototyp. Dopiero potem warto poprawiać wygląd i automatyzację.

**Output:**

dnia wersja to typ, w którym elementy są w stanie poprawić. Jeśli tekst jest lepszy, to można sprawdzić, czy coś jest ważne. W praktyce wystarczy zacząć od najgorszego elementu. Nie trzeba zmieniać nazwy, ale tylko powiedzieć, co zrobić.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 15. streszczanie

**Prompt:** Streść w jednym zdaniu: Dobry plan zaczyna się od małego testu, który pokazuje, czy warto rozwijać pomysł dalej.

**Output:**

Streszczenie to coś więcej niż tylko plan, który ma pomóc zrozumieć sens. Wtedy dopiero wtedy można ocenić sens. To ważne, bo nie trzeba być bez sensu.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 16. proste_wyjasnienia

**Prompt:** Wyjaśnij prosto, czym różni się pogoda od klimatu.

**Output:**

Wyjdź do tego jak do małego systemu. Ułatwia to zrozumienie i od razu je pocałkuje. Najpierw sprawdź czy deszcz działa, a później nie działa. Najważniejsze jest aby temperatura była mniejsza. Jeśli nie wygląda lepiej niż średnia temperatura to można go wyrobić za mało.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 17. proste_wyjasnienia

**Prompt:** Wyjaśnij, czym jest inflacja.

**Output:**

Wyobraź sobie, że to działa. Jeśli nie działa, po tym jak działa. Jeśli to działa, przynajmniej po pierwszym kroku, musisz zacząć od najkrótszego ruchu. Podejdź do tego jak do małego testu.

**Score:** IF=3 coherence=2 repetition=1 usefulness=3 total=7

## 18. proste_wyjasnienia

**Prompt:** Czym różni się fakt od opinii?

**Output:**

rodzaju dane są ważne dla konkretnego zdania. Nie trzeba go oceniać jako wartościową. Bez znaczenia jest też dokładność. Ta wersja jest większa niż ogólna, konkretna wersja. Jeśli użytkownik ma do wyboru konkretny sens, to powinien ocenić, czy można zrobić więcej.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 19. proste_wyjasnienia

**Prompt:** Wyjaśnij krótko, czym jest grawitacja.

**Output:**

Wyjaśnij krótko i krótko, aż do momentu, w którym się rozpada. Jeśli po tym dalej nie wiadomo, co to robić. Jeśli po tym dalej działa, łatwiej zrobić więcej niż jedną, którą chcesz zacząć.

**Score:** IF=3 coherence=1 repetition=2 usefulness=1 total=3

## 20. proste_wyjasnienia

**Prompt:** Czym różni się masa od wagi?

**Output:**

czym różni się masa w czasie trwania. Najlepiej zacząć od konkretnej masa, a nie od najkrótszego ruchu. Jeśli nie działa, wybierz część, która dotyka całej masy. W praktyce warto wybrać model zmysłowy, bo tylko wtedy można powiedzieć, że pojęcie nie jest ważne. Jeśli pojęcie nie leży w miejscu, ale ma sens, to dopiero potem można zrobić coś.

**Score:** IF=3 coherence=2 repetition=1 usefulness=3 total=7

## 21. decyzje_projektowe

**Prompt:** Mam zacząć projekt od UI czy od logiki?

**Output:**

ż to samo. W praktyce jest bardziej realny, niż zwykle większy niż zwykle. Jeśli po tym dalej masz pewność, że po tym dalej masz energię. To, co robisz, działa lepiej niż tylko uproszczenie. Nie próbuj od razu oceniać swojej decyzji. Nie oceniaj tego w praktyce jako głównego elementu systemu pracy.

**Score:** IF=1 coherence=2 repetition=1 usefulness=1 total=3

## 22. decyzje_projektowe

**Prompt:** Mam ambitny projekt i chcę od razu zrobić backend, frontend, dashboard, AI, logowanie i ładne UI. Dobry plan?

**Output:**

fermentuje to, co robi i czy działa. Oceń to, czy działa. Jeśli po tym dalej masz energię, a nie tylko energię.

**Score:** IF=1 coherence=2 repetition=1 usefulness=1 total=3

## 23. decyzje_projektowe

**Prompt:** Mam dwie opcje: zrobić projekt szybko i prosto albo długo dopracowywać wszystkie detale. Co wybrać?

**Output:**

rz. projekt szybko i łatwo. Plan ma pomóc w usunięciu wszystkich błędów. Jeśli to działa, wystarczy odróżnić kilka elementów od innych elementów. Najpierw wybrać jedną wersję, a dopiero potem wybrać jedną wersję. Najpierw wybrać typową wersję. Jeśli po tym dalej masz energię, trzeba najpierw zacząć od najkrótszego ruchu.

**Score:** IF=3 coherence=2 repetition=1 usefulness=3 total=7

## 24. decyzje_projektowe

**Prompt:** Czy warto robić projekt, jeśli nie wiem jeszcze, czy go skończę?

**Output:**

Czy można robić więcej w głowie, bo dopiero wtedy trzeba zacząć. Wtedy wszystko jest ważne, a nie do końca zrozumiałe. Najpierw najlepiej zacząć od najgorszego celu i po tym jak wygląda praca. Inaczej nie musi być duża, bo trzeba robić więcej.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 25. decyzje_projektowe

**Prompt:** Mam wybrać łatwiejszą czy ambitniejszą wersję projektu.

**Output:**

steczki są krótkie i krótkie. Przy takiej formie łatwo można zrobić bez problemu, a nie tylko szybko. Najpierw sprawdzić, czy trzeba robić więcej niż mały krok. To działa dobrze, a nie szybko. Jeśli coś działa, można najpierw odpowiedzieć na pytanie, co robić.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 26. korekta_zalozen

**Prompt:** Popraw błędne założenie: droższy sprzęt zawsze jest lepszy.

**Output:**

Podejdź do tego jak do małego testu. Jeśli nie masz czasu, rozbudujesz. Jeśli nie wiesz co zrobić, dopiero potem dopieszczaj najkrótszą wersję. Jeśli nie masz pomysłu na to, co poprawić, rozbudujesz. Nie oceniaj planu po tym, czy można go od razu poprawić. Jeśli coś nie działa, po pierwszym kroku łatwo zacząć od tego, co zostało.

**Score:** IF=1 coherence=2 repetition=1 usefulness=1 total=3

## 27. korekta_zalozen

**Prompt:** Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.

**Output:**

Ta wersja jest krótsza i czytelniejsza. Po tym czasie trzeba dokładnie ocenić, czy projekt nie działa. W praktyce warto rozróżnić zadania, które są ważne i bardziej szczegółowe.

**Score:** IF=1 coherence=2 repetition=1 usefulness=1 total=3

## 28. korekta_zalozen

**Prompt:** Popraw błędne założenie: jak projekt ma dużo funkcji, to jest lepszy.

**Output:**

W praktyce lepsze niż wersja, ale nie wiadomo, czy tekst ma sens. Nie ma sensu w ogóle robić z tego zadania. Przy takim zadaniu trzeba odpowiedzieć krótko i łatwo, bez powodu.

**Score:** IF=1 coherence=2 repetition=1 usefulness=1 total=3

## 29. korekta_zalozen

**Prompt:** Popraw błędne założenie: Docker to to samo co maszyna wirtualna.

**Output:**

Podejdź do tego, jak szybko i prosto. Najpierw najpierw najpierw zacząć od najkrótszego ruchu, a dopiero potem dopiero wtedy zrobić krok. W praktyce łatwiej zrozumieć, czy po tym dalej idzie. Najpierw zacząć od najgorszego zadania, który powinien pomóc poprawić działanie. Jeśli po tym dalej nie idzie, wybierz jedną z najbardziej podstawowych zadań.

**Score:** IF=1 coherence=1 repetition=2 usefulness=1 total=1

## 30. korekta_zalozen

**Prompt:** Popraw błędne założenie: im dłuższa odpowiedź, tym jest mądrzejsza.

**Output:**

Popraw błędny założenie: im dłuższy efekt nie będzie zbyt duży, tym łatwiejsze dopisanie. Wtedy warto zacząć od najkrótszego ruchu. Najpierw dodać kilka przykładów. Jeśli nadal działa, rozbudujesz.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 31. techniczne_proste

**Prompt:** Czym jest backup?

**Output:**

czym jest backup?

**Score:** IF=1 coherence=0 repetition=0 usefulness=0 total=1

## 32. techniczne_proste

**Prompt:** Czym różni się plik od folderu?

**Output:**

czym różni się pliki od wartości pliku?

**Score:** IF=1 coherence=3 repetition=0 usefulness=1 total=5

## 33. techniczne_proste

**Prompt:** Czy chmura jest zawsze lepsza niż lokalny serwer?

**Output:**

Czy to tylko działa, żeby zrobić krok po kroku?

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 34. techniczne_proste

**Prompt:** Czym różni się aplikacja od strony internetowej?

**Output:**

czym różni się aplikacja do tworzenia aplikacji? Ta wersja ma być mniejsza. Chodzi o to, żeby można było tworzyć w każdym miejscu własny projekt, który działa jak najkrótszy plan. Ta wersja jest krótsza i czytelniejsza.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 35. techniczne_proste

**Prompt:** Czym różni się CPU usage od load average?

**Output:**

kierowujesz dane i czas, nawet jeśli działa. Nie chodzi o to, żeby po tym jak go rozwiązać. W praktyce jest więcej możliwości. Jeśli to działa, najlepiej zacząć od konkretnych zadań, które są ważne. To działa tylko wtedy, gdy działa. Przy takim zadaniu lepiej zacząć od podstaw.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 36. anty_petle

**Prompt:** Napisz krótką odpowiedź i nie powtarzaj tej samej myśli.

**Output:**

dę do tego i po każdym kroku po jego wykonaniu warto odpowiedzieć na pytanie, czy te dane są poprawne. Jeśli chodzi o dane w formacie, warto sprawdzić, czy dane były poprawnie zapisane i w ogóle nie działało. Jeśli nie masz jeszcze takiej wiedzy, wybierz jedną z następujących definicji: Cierpliwość jest tu bardziej dokładna, ale łatwiejsza.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 37. anty_petle

**Prompt:** Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?

**Output:**

Odpowiedz Ja nie używam od razu jednej rzeczy, ale od razu ją odkłada. Nie jest to problem, bo jest zbyt ciężki, bo trzeba odróżnić elementy od pozostałych elementów, które są ważne. Problem polega na tym, że nie wiadomo. Otóż nie wiadomo, jak wygląda sprawa w przypadku. W praktyce wystarczy zrobić wszystko, ale nie wiadomo, co zrobić.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 38. anty_petle

**Prompt:** Ten tekst nie powinien się zapętlać. Wyjaśnij krótko dlaczego.

**Output:**

Ten tekst nie musi być zbyt wielki. Jeśli nie działa, trzeba szybko poprawić. Najpierw zacząć, a dopiero potem dokładać kolejne elementy. Najpierw zacząć, a dopiero później dokładać kolejne elementy. Nie chodzi o to, żeby zrobić więcej. Najpierw musisz czekać na konkretne szczegóły.

**Score:** IF=1 coherence=1 repetition=2 usefulness=1 total=1

## 39. anty_petle

**Prompt:** Odpowiedz krótko: czego nie da się ocenić bez danych?

**Output:**

Odpowiedz krótko: czego nie da się oceniać bez danych?

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9

## 40. anty_petle

**Prompt:** Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?

**Output:**

Odpowiedz krótko i łatwo.

**Score:** IF=3 coherence=3 repetition=0 usefulness=3 total=9
