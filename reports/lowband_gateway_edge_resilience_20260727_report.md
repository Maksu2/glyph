# Lowband Gateway 0.1.1 — odporność na fatalne EDGE

Data walidacji: 2026-07-27 (UTC)  
Wdrożenie: `https://lowband.maksu.online`

## Wynik

Zmiana została wdrożona bez przebudowy kolejki ani runnera. Klient renderuje
się offline-first, utracone odpowiedzi logowania i tworzenia zadania są
rozstrzygane bezpiecznymi requestami kontrolnymi, a minimalny lokalny model
zadań znajduje się w IndexedDB. Wszystkie testy Python, testy kontraktowe PWA
i 17 scenariuszy Chromium przeszły.

Przed wdrożeniem wykonano online backup:
`/data/backups/lowband-pre-edge-20260727.sqlite`. Po wdrożeniu
`PRAGMA integrity_check` zwróciło `ok`; istniejący rekord `done` pozostał w
bazie.

## 1. Konkretne przyczyny problemów

- `login-view` i `app-view` były początkowo ukryte, a `init()` czekał na
  `/session`. Timeout podczas pełnego reloadu dawał pusty interfejs.
- Utrata odpowiedzi `POST /login` była traktowana jak nieudane logowanie.
  Frontend nie sprawdzał, czy cookie i sesja powstały.
- Backend już miał unikalny indeks `client_request_id` i poprawnie
  deduplikował POST, lecz nie istniał endpoint odszukania zadania po tym ID.
- Frontend przechowywał szkic i kilka ID w `localStorage`, ale nie zachowywał
  lokalnych statusów, czasu synchronizacji ani stanu `uncertain`.
- Ręczne odświeżenie, polling, powrót z tła i zdarzenie `online` mogły
  uruchamiać równoległe list/detail requesty.
- Lista nie obsługiwała ETag; szczegół zadania już go obsługiwał.
- Service worker miał podstawowy cache shellu, ale bez strony offline i bez
  stale-while-revalidate dla navigation. Błąd sesji nadal ukrywał aplikację,
  więc sam cache nie wystarczał.
- Polling zaczynał od natychmiastowego requestu i używał wspólnego timeoutu
  20 s bez rozróżnienia soft/hard timeout.

## 2. Zmienione pliki

- Backend: `app/main.py`, `app/jobs.py`, `app/config.py`,
  `app/__init__.py`.
- Frontend: `frontend/app.js`, `frontend/index.html`,
  `frontend/styles.css`, `frontend/sw.js`, nowy
  `frontend/offline.html`.
- Testy: `tests/test_jobs.py`, `tests/test_pwa.py`,
  `tests/test_import_cloudflare_credentials.py`, nowy
  `scripts/test_edge_browser.py`.
- Operacyjne i dokumentacja: `README.md`, `compose.yaml`, `pyproject.toml`,
  `.env.example`, produkcyjne `APP_VERSION=0.1.1`,
  `scripts/import_cloudflare_credentials.py`.

Nie zmieniono schematu kolejki, algorytmu lease, workera, runnera Codexa ani
izolacji sieciowej.

## 3. Logowanie po utraconej odpowiedzi

Frontend wykonuje pojedynczy `POST /login`. Po 15 s pokazuje informację o
wolnym połączeniu. POST ma twardy limit 20 s. Przy timeoutcie lub błędzie
transportu klient informuje o niepewnym wyniku i wykonuje `GET /session` w
pozostałym budżecie, tak aby najpóźniej po około 30 s zakończyć oczekiwanie.

Aktywna sesja oznacza sukces i przejście do aplikacji. Brak sesji albo drugi
błąd daje możliwość ręcznego ponowienia. Nie ma automatycznej pętli, a hasło
pozostaje wyłącznie w polu DOM do chwili sukcesu lub opuszczenia widoku.

## 4. Idempotencja zadań

Przed pierwszą próbą frontend generuje UUID, zapisuje rekord lokalny i dopiero
potem wysyła POST. Ten sam UUID jest używany przez każde jawne ponowienie.

Nowy endpoint:

`GET /api/v1/jobs/by-client-request-id/{client_request_id}`

wymaga sesji, zwraca krótki rekord albo 404. Powtórzony `POST /jobs` nadal
zwraca ten sam rekord (200 z `duplicate=true`), nie konflikt i nie duplikat.
Test z utraconą odpowiedzią potwierdził jeden POST w bazie, a test trzech
równoczesnych submit events potwierdził jeden pierwszy request.

## 5. Lokalny cache i IndexedDB

Store `lowband-gateway/jobs` zapisuje:

- stabilny `client_request_id` i opcjonalny `public_id`;
- skrót promptu, a pełny prompt tylko dla `draft`, `sending` i `uncertain`;
- status, `created_at`, `updated_at`, stan synchronizacji;
- ostatni bezpieczny błąd i czas ostatniej udanej synchronizacji;
- jakość i flagę powiadomienia potrzebne do bezpiecznego retry.

Obsługiwane lokalnie stany to `draft`, `sending`, `uncertain`, `queued`,
`running`, `done`, `failed`, `needs_user` oraz terminalne statusy serwera.
Pojedynczy błąd synchronizacji dopisuje komunikat do rekordu, ale nie zmienia
ostatniego statusu. Gdy IndexedDB jest niedostępne, istnieje ograniczony
fallback do `localStorage`. Cookie, hasło i pełne wyniki nie trafiają do tych
magazynów.

## 6. Service worker

Cache `lowband-shell-v3` zawiera `/`, CSS, JS, manifest, lokalną ikonę i
`/offline.html`. Instalacja kończy `cache.addAll(SHELL)` przed
`skipWaiting()`. Aktywacja i usuwanie starego cache’u występują dopiero po
kompletnej instalacji nowego.

Navigation request otrzymuje najpierw zapisany `/`, a aktualizacja sieciowa
odbywa się w tle. Przy braku shellu używana jest strona offline. Zasoby shellu
mają cache-first z aktualizacją w tle. `/api/`, `/ready` i `/health` są
network-only i prywatne odpowiedzi nie są zapisywane.

## 7. Brak nakładających się requestów

- `syncInProgress` serializuje sprawdzenie sesji, resolving `uncertain`, listę
  i szczegół.
- `listInFlight` blokuje kolejną listę; przycisk pokazuje
  „Odświeżanie…”.
- `detailInFlight` blokuje kolejny szczegół i jest anulowany przy zmianie
  widoku lub przejściu w tło.
- `submitInFlight` i `pendingSends` blokują wielokrotny submit.
- Jawne retry pokazane przed zwolnieniem poprzedniej próby czeka na jej wynik
  i wysyła ponownie tylko wtedy, gdy rekord nadal jest `draft/uncertain`.
- Polling: 5, 10, 20, 40, 60, 60 s; soft timeout 15 s, hard timeout 30 s.
- `offline` zatrzymuje polling i anuluje status requesty; `online` uruchamia
  jedną synchronizację bez automatycznego wysyłania draftów.

## 8. Uruchomione testy

- `pytest`: **70 passed**, 1 płatny test prawdziwego Codexa pominięty jawnie.
- `ruff check .`: bez błędów.
- `node --check frontend/app.js frontend/sw.js`: bez błędów.
- `docker compose config --quiet`: poprawna konfiguracja.
- Chromium/Playwright: **17/17** scenariuszy.
- Produkcja: sześć usług healthy/running, publiczny health 200, shell i SW
  0.1.1 dostępne, niezalogowane API i lookup zwracają 401.
- Prawdziwy Chrome przez `agent-browser`: ekran logowania i shell widoczne na
  publicznej domenie.

Testy Chromium objęły utraconą odpowiedź loginu i POST zadania, deduplikację,
trzy submit events, jawne bezpieczne retry, cztery kliknięcia odświeżenia,
timeout listy, zachowanie statusu, reload offline, reconnect, wygasłą sesję i
kompletność cache’u. Osobny scenariusz przerwał aktualizację service workera
na brakującym pliku, potwierdził pozostawienie starego aktywnego shellu, a
następnie dokończył aktualizację i wykonał reload offline.

Rozmiar shellu:

- 62 719 B bez kompresji;
- 16 991 B gzip;
- 6 requestów przy pierwszym wejściu;
- 1 navigation request przy odświeżeniu z kontrolującym service workerem.

## 9. Weak EDGE i Brutal EDGE

Automatyczna emulacja CDP używała:

| Profil | Down | Up | Łączne latency (z DNS) | Packet loss | Shell z cache |
|---|---:|---:|---:|---:|---:|
| Weak EDGE | 100 kb/s | 40 kb/s | 850 ms | 1% | 46 ms |
| Brutal EDGE | 50 kb/s | 15 kb/s | 1950 ms | 3% | 24 ms |
| Całkowicie offline | 0 | 0 | — | — | 33 ms |

Po przerwanej, a następnie kompletnej aktualizacji service workera reload
offline trwał 35 ms.

We wszystkich przypadkach formularz był widoczny i zachował szkic/statusy.
Wyniki mierzą lokalny cache service workera; dlatego przepustowość i latency
nie opóźniają samego renderu. CDP potwierdził obsługę pola packet loss.

## 10. Ograniczenia

- Pierwsza wizyta na urządzeniu nadal wymaga jednego kompletnego pobrania
  shellu; offline-first działa po udanej instalacji service workera.
- iOS może usunąć Cache Storage/IndexedDB pod presją miejsca. Aplikacja nie ma
  wpływu na politykę systemową Safari.
- Pełne prywatne wyniki celowo nie są cache’owane. Offline widoczny jest
  ostatni status i skrót, nie pełna odpowiedź, jeśli nie ma sieci.
- Emulacja CDP sumuje opóźnienia wejścia, wyjścia i DNS. Nie zastępuje
  końcowego ręcznego testu na fizycznym iPhonie z Network Link Conditioner.
- `navigator.onLine` jest tylko wskazówką; dlatego wszystkie błędy transportu
  są również obsługiwane niezależnie od jego wartości.
- System ma jedno konto. Lookup jest chroniony sesją tego konta; ewentualne
  przyszłe dodanie wielu kont wymaga kolumny właściciela zadania.

## Stan produkcji

- Wersja aplikacji: `0.1.1`.
- Model pozostaje bez zmian: `gpt-5.6-terra`, reasoning `medium`.
- Cloudflare Tunnel pozostał działający; router nadal nie publikuje portu.
- Backup przed zmianą istnieje w wolumenie danych.
