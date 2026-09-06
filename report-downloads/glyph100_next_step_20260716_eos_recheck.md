# Glyph-100M EOS-aware checkpoint recheck

This is an inference-only base-LM continuation check. Generation now stops at the SentencePiece EOS token and reports the actual generated length.

## Result

- prompts: `60`
- generations: `360`
- pairwise: `{'44k': 52, 'tie': 84, '50k': 44}`
- provisional winner: **44k**

| Checkpoint / preset | avg quality | EOS | natural | max-token cutoff | repetitions | avg tokens | tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| 44k / current_normal_80 | 7.833 | 16/60 | 19/60 | 44/60 | 18/60 | 70.73 | 72.41 |
| 44k / repetition_guard_80 | 8.617 | 21/60 | 22/60 | 39/60 | 0/60 | 63.38 | 73.26 |
| 50k / current_normal_80 | 7.95 | 8/60 | 8/60 | 52/60 | 18/60 | 74.08 | 72.17 |
| 50k / repetition_guard_80 | 9.167 | 18/60 | 19/60 | 42/60 | 0/60 | 68.5 | 72.62 |
| 44k / greedy_80 | 2.7 | 14/60 | 15/60 | 46/60 | 51/60 | 72.18 | 74.18 |
| 50k / greedy_80 | 1.567 | 8/60 | 11/60 | 52/60 | 55/60 | 75.03 | 73.99 |

## Interpretation

The old eval path treated every generation as if it consumed the full token budget. This recheck separates true EOS endings from max-token cutoffs. It is intentionally smaller than the historical broad eval and does not by itself authorize training or change the selected best checkpoint.

## Largest Pairwise Differences

### broad-043 · greedy_80 · delta 50k-44k=-15

Prompt: `Według najnowszych danych`

44k (14): , w tym: gęstość zaludnienia wynosiła 79,1 osób/km2 (wśród 2290 gmin Akwitanii Saint-Martin-de-Villages plasuje się na 712. miejscu pod względem liczby ludności, natomiast pod względem powierzchni na miejscu 1332.).

50k (-1): z roku 2002 liczba ludności wynosiła 312, co stanowiło 10,8% ludności kraju. W roku 2002 liczba ludności wynosiła 312, co stanowiło 10,8% ludności kraju. W roku 2002 liczba ludności wynosiła 312, co stanowiło 10,8% ludności kraju. W roku 2002 liczba ludności wynosiła 312, co stanowiło 10,8% ludności kraju. W roku 2002 liczba ludności wynosiła 312

### broad-011 · current_normal_80 · delta 50k-44k=14

Prompt: `Uczenie maszynowe polega na`

44k (0): tym, że maszyna może być używana do odpylania, np. do odpylania, a nawet do tego celu. Z drugiej strony maszyna może być używana przez osoby pracujące przy użyciu techniki odpylania. Z drugiej strony maszyna może być używana do odpylania i wtrysku do odpylania. Maszyna może być używana do odpylania i

50k (14): tym, że maszyny z napędem mają taki samo układ napędowy, żeby nie mogły się poruszać, a nie na nich. Uczenie maszynowe jest niezbędne, ponieważ nie można ich poruszać i używać do pracy w terenie, w którym się znajduje. W tych warunkach konieczne jest sprawdzenie poprawności i w praktyce nie ma możliwości, aby wykonać skomplikowane prace i zwiększyć bezpieczeństwo maszyny. W tym przypadku

### broad-053 · greedy_80 · delta 50k-44k=-14

Prompt: `Morze Bałtyckie znajduje się`

44k (9): w odległości ok. 5 km od Morza Bałtyckiego. W latach 1975–1998 miejscowość administracyjnie należała do województwa bydgoskiego. Według Narodowego Spisu Powszechnego (III 2011 r.) liczyła 311 mieszkańców. Jest drugą co do wielkości miejscowością gminy Morze Bałtyckie.

50k (-5): w granicach administracyjnych miasta Gdańska. W latach 1975–1998 miejscowość administracyjnie należała do województwa gdańskiego. Zabytki Według rejestru zabytków NID na listę zabytków wpisany jest zespół dworski, nr rej.: A/157 z 27.12.1957: dwór, nr rej.: A/157 z 27.12.1957: dwór, nr rej.: A/157 z 27

### broad-053 · current_normal_80 · delta 50k-44k=-14

Prompt: `Morze Bałtyckie znajduje się`

44k (16): dwa jeziora w: Gotlandii, Szwecji, Szwecji i Szwecji. Na jeziorze znajdują się dwa jeziora: Jezioro Wicko-Krzyżackie, Jezioro Morza Bałtyckie i jezioro Morza Bałtyckiego.

50k (2): dwa razy w roku w gminie i w gminie: Chojnice, Grądy (wieś na terenie gminy Chojnice), Chojnice, Chojnice, Chojnice, Chojnice, Drzewieś, Drzewieś, Drzewieś, Drzewieś, Drzewieś oraz wiele innych. Na terenie gminy, w pobliżu znajduje się cmenta

### broad-012 · current_normal_80 · delta 50k-44k=-13

Prompt: `Model językowy przewiduje`

44k (12): , że w ciągu jednego stulecia na świecie powstał język wysokiego poziomu, a na świecie powstał ponad 1300 języków, w tym kilkaset języków obcych. Język ten, używany obecnie również przez część osób związanych z językami niemieckimi, jest językiem standardowym.

50k (-1): w nim: *Lament – w języku potocznym *Lament – w języku polskim *Lament – w języku polskim *Lament – w języku polskim *Lament – w języku polskim *Lament – w języku angielskim *Lament – w języku angielskim *Lament – w języku angielskim *Lament – w języku polskim *Lament

### broad-013 · current_normal_80 · delta 50k-44k=12

Prompt: `Dobry plan zaczyna się od`

44k (4): nowa, a jego wykonanie trwa od 20 minut do 30 minut w zależności od gatunku. Z drugiej strony, w zależności od gatunku, są one mniej kosztowne, niż w przypadku innych taksometrycznych elementów (np. w przypadku chmur). Wszystkie ściany są jednak bardziej przyjazne i bardziej przyjazne dla środowiska i narażone na zanieczyszczenie powietrza. Na przykład, jeśli masz już dość wysokie

50k (16): nowa, a jego plan trwa jeszcze dłużej. Stąd też w Polsce jest coraz mniej, a jego plan się nie odbędzie. Niezwykle ważny jest plan, ale na dodatek w Polsce tak naprawdę można dojechać do takich miast, jak Kraków.

### broad-014 · greedy_80 · delta 50k-44k=-12

Prompt: `Kiedy brakuje danych, najlepiej`

44k (12): jest wybrać odpowiednie oprogramowanie, które może pomóc w rozwiązaniu problemów. W tym artykule przyjrzymy się bliżej temu, jak kluczowe jest zrozumienie problemów z zarządzaniem projektami.

50k (0): jest mieć na uwadze, że nie ma w nich miejsca na dyskusję. W tym przypadku warto mieć na uwadze, że nie ma w niej miejsca na dyskusję. W tym przypadku warto mieć na uwadze, że nie ma miejsca na dyskusję. W takim przypadku warto mieć na uwadze, że nie ma miejsca na dyskusję. W takim przypadku warto mieć na uwa

### broad-023 · current_normal_80 · delta 50k-44k=12

Prompt: `Błąd w konfiguracji może powodować`

44k (1): załamanie pola elektrycznego i zmiany stanu pola, które mogłyby przeżyć zarówno w czasie rzeczywistym, jak i fizycznym. W przypadku fal elektromagnetycznych lub planet lub planet, sygnały, które muszą być zapisane w układzie współrzędnych, mogą być zapisane w postaci dwóch różnych współrzędnych, które muszą być zapisane w taki sposób, aby od tej

50k (13): załamania, pęknięcia i pęknięcia. W przypadku przeciążeń w konfiguracji dochodzi do ich przeciążenia. W przypadku przeciążeń do kresów lub pęknięć, zazwyczaj, a nawet pęknięć, układy są przeciążone, jednak z uwagi na brak mechanizmu przeciążenia, w warunkach normalnych, stosuje się przeciążenia odwz

### broad-051 · greedy_80 · delta 50k-44k=-12

Prompt: `Wisła przepływa przez`

44k (7): Wisłę, a następnie przez Wisłę. W latach 1975–1998 miejscowość administracyjnie należała do województwa bielskiego. W miejscowości znajduje się kościół parafialny pw. św. Stanisława Biskupa i Męczennika, który został poświęcony w 1830 r. przez ks. proboszcza Józefa Gąsiorowskiego.

50k (-5): miasto, a następnie przez miasto. W latach 1975–1998 miejscowość administracyjnie należała do województwa siedleckiego. W miejscowości znajduje się szkoła podstawowa, szkoła podstawowa, przedszkole, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła podstawowa, szkoła

### broad-033 · greedy_80 · delta 50k-44k=10

Prompt: `Krótki tekst jest lepszy, gdy`

44k (0): nie ma miejsca na jego wykonanie. W tym przypadku, jeśli nie ma miejsca na wykonanie tego zadania, to może być to niemożliwe. Jeśli nie ma miejsca na wykonanie tego zadania, to może być to niemożliwe. Jeśli nie ma miejsca na wykonanie zadania, to może być to niemożliwe. Jeśli nie ma miejsca na wykonanie zadania, to może być to niemożliwe. Jeśli nie ma miejsca na wykonanie zadania

50k (10): jest on bardziej złożony. W tym artykule przyjrzymy się bliżej temu, co jest ważne dla Ciebie.

### broad-039 · current_normal_80 · delta 50k-44k=-10

Prompt: `Komentarze: anonimowy napisał`

44k (12): : A jeśli jest tam, niech będzie taka wojna. [] Czy to ty, jak się okazuje o wojnie? [] Czy to jest wojna? [] Na pewno się tyczy wojny? []

50k (2): : A jeśli jest, to niech będzie, a będzie, to niech to niech będzie. A w tym przypadku nie będzie, a jeśli masz, to niech będzie. A jeśli tak, to niech to zrobi (jeśli to zrobi). A jeśli tak (wszystko) niech będzie, to niech będzie, a niech będzie, to niech będzie, to niech będzie, to niech będzie. A jeśli

### broad-057 · current_normal_80 · delta 50k-44k=10

Prompt: `W praktyce oznacza to, że`

44k (1): ludzie, którzy nie mają styczności z tymi, którzy są w stanie być spokojni i naśladowani. To samo dotyczy zarówno tych, którzy chcą być w niej postrzegani jako ludzie, ludzie, osoby, osoby i osoby, które chcą być świadomi tego, którzy nie mają styczności z tymi, którzy nie mają styczności z tymi, którzy nie są świadomi tych,

50k (11): ludzie, którzy nie mają styczności z człowiekiem, nie są w stanie być samodzielnymi ludźmi, ale są w stanie tworzyć nowe, niekoniecznie jednolity obraz życia, a także pomagają znaleźć własne życie. W niektórych wypadkach na przykład, jak i z różnymi czynnościami fizycznymi i psychicznymi, mogą spotkać się ze sobą i prowadzić do sytuacji, w której ktoś nie chce żyć. W

