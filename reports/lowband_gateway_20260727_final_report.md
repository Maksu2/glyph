# Lowband Gateway — raport końcowy

Data walidacji: 2026-07-27 13:57 UTC  
Repozytorium: `/home/maksu/lowband-gateway`  
Wersja aplikacji: `0.1.0`  
Stan: kompletne, uruchamialne repozytorium; publiczne wdrożenie wymaga
uzupełnienia prywatnych danych operatora.

## Zrealizowane

- FastAPI i wersjonowane `/api/v1`, z minimalnym publicznym `/health` oraz
  chronionym `/ready`.
- SQLite z WAL, foreign keys na połączeniach aplikacji, busy timeout,
  transakcjami, indeksami i trzema kontrolowanymi migracjami Alembic.
- Trwała kolejka i osobny worker: atomowy claim, lease/renewal, heartbeat,
  recovery po awarii, limit prób, anulowanie, retry i `needs_user`.
- Idempotentne utworzenie zadania przez `client_request_id`; reply i retry
  również mają klucze idempotencji. Minimalne rekordy użycia pozostają po
  usunięciu zadania, aby nie omijać limitów i nie tworzyć duplikatu.
- Jednohasłowe logowanie Argon2id, zahashowane tokeny sesji, 30-dniowe cookie
  `HttpOnly`, `Secure`, `SameSite=Strict`, rotacja, revocation i sprzątanie.
- Rate limit logowania 5 błędów/IP/15 min, limit globalny oraz bezpieczne
  ustalanie IP za jawnie zaufanym adresem Cloudflare Tunnel.
- CSRF powiązany z sesją i kontrola `Origin` dla wszystkich mutacji.
- Limity kosztowe i rozmiarowe po stronie backendu: godzinowe, dzienne,
  kolejki, współbieżności, promptu, wyniku, timeoutu i retry.
- Adapter Codex CLI 0.145.0 bez `shell=True`, z walidowanymi argumentami,
  `--json`, schematem wyniku, timeoutem grupy procesów, anulowaniem i jedną
  próbą naprawy formatu.
- Produkcyjny model pozostawiony jako `gpt-5.6-terra` z reasoning `medium`;
  `high` jest używane tylko jawnie lub po kwalifikującym błędzie.
- Fake runner do bezpłatnych testów całego przepływu.
- Izolowany runner Docker: nie-root, read-only root, bez capabilities,
  `no-new-privileges`, limity CPU/RAM/PID, efemeryczny workspace, brak bazy,
  sekretów aplikacji, kluczy hosta i Docker socketa.
- Rozdzielony runner-gateway. Bearer znajduje się w workerze i gatewayu, ale
  nie w procesie właściwego Codexa; połączenie runnera jest dodatkowo
  ograniczone adresem źródłowym.
- Oddzielny Squid egress z blokadą prywatnego LAN, link-local i metadata
  endpoints po rozwiązaniu DNS. Bezpośredni ruch runnera poza proxy jest
  blokowany topologią sieci Compose.
- Warstwa researchu: zwykły HTTP jako pierwsza próba, Chromium Headless tylko
  gdy potrzebny; blokada obrazów, fontów, multimediów i trackerów, timeout,
  limit stron i bajtów, brak trwałego profilu i brak obchodzenia CAPTCHA.
- Opcjonalne ntfy, którego awaria nie zmienia poprawnego `done` na `failed`.
- Lekki frontend bez frameworka: logowanie, formularz, lista, szczegół,
  `needs_user`, retry, cancel/delete, ręczne odświeżanie i mały widok admina.
- PWA z lokalnym shellem, network-only dla API, zapisem szkicu i stałego UUID
  niedostarczonego requestu oraz pollingiem 0/5/10/20/40/60 s.
- CSP i pozostałe nagłówki ochronne, brak CDN, fontów i skryptów inline.
- Retencja automatyczna i ręczna, bezpieczny SQLite Online Backup, restore z
  kontrolą integralności, skrypty revocation i generowania sekretów.
- Docker Compose dla `web`, `worker`, migracji, runnera, egress i opcjonalnego
  `cloudflared`; backend produkcyjny nie publikuje portu hosta.
- Dziesięciozadaniowy benchmark Terra/Luna z raportem JSON/Markdown, który nie
  uruchamia się automatycznie.
- Pełne polskie `README.md`, `AGENTS.md`, threat model, instrukcje aktualizacji,
  rollbacku, backupu, Cloudflare, ntfy i diagnostyki.

## Nieukończone

- Nie skonfigurowano publicznej domeny, Cloudflare Tunnel ani opcjonalnego
  Cloudflare Access: wymagają konta, domeny i prywatnego tokenu użytkownika.
- Nie wysłano prawdziwego powiadomienia ntfy: nie podano topicu ani tokenu.
- Dedykowany wolumen produkcyjnego runnera nie został zalogowany do Codex.
  Rzeczywisty adapter został natomiast sprawdzony z hostowym, zalogowanym
  Codex CLI na modelu Terra.
- Nie uruchomiono pełnego benchmarku Terra kontra Luna, ponieważ wykonałby
  20 płatnych zadań researchowych. Bez benchmarku Luna pozostaje wyłączona.
- Nie wykonano fizycznego testu na iPhonie i prawdziwym EDGE/GPRS. Zachowanie
  po zerwaniu klienta, backoff, rozmiary zasobów i trwałość zostały sprawdzone
  lokalnie.
- Nie wykonano publicznego wdrożenia produkcyjnego, ponieważ brak wymienionych
  wyżej sekretów i domeny.

## Testy

- `ruff check`, `ruff format --check`, `compileall`, `pip check`,
  `node --check` dla obu skryptów PWA i `git diff --check`: zaliczone.
- `pytest -q`: **60 passed, 1 skipped**. Pominięto wyłącznie jawnie opt-in
  test płatnego Codexa.
- `pytest --cov=app --cov=worker`: **60 passed**, łączna coverage **78%**.
- Jawny `RUN_REAL_CODEX=1` na `gpt-5.6-terra`, reasoning `medium`:
  **1 passed**; zwrócił poprawny JSON zgodny ze schematem.
- Fake Docker E2E: POST został trwale przyjęty w około 0,289 s, pierwszy
  klient zamknięto, worker ukończył zadanie, drugi klient odczytał wynik, a
  ETag zwrócił `304`.
- Restart `web` w trakcie `running`: sesja i zadanie zachowane, wynik `done`.
- Restart workera w trakcie `running`: po wygaśnięciu lease to samo zadanie
  odzyskano jako drugą próbę i zakończono bez trwałego `running`.
- Pełne `compose down/up` przy zadaniu `queued`: wolumen, sesja i zadanie
  zachowane, końcowy stan `done`.
- Dwa workery próbujące claimu: tylko jeden przejmuje rekord.
- Migracja istniejącej bazy do `0003_system_job_events`: zaliczona;
  `PRAGMA integrity_check=ok`, tryb `wal`, Alembic na head.
- Chromium: `example.com` zwrócił 559 B; duży dokument Gutenberg został
  przerwany z błędem limitu przy konfiguracji 10 KB.
- Izolacja: runner UID 10001, wszystkie capability masks równe zero,
  prywatny LAN i bezpośredni internet z pominięciem proxy niedostępne,
  sekret gatewayu nieobecny w env i `/proc`, workspace po testach pusty.
- Konfiguracja Compose dla profili `codex` i `tunnel`: poprawna.
- Shell PWA: **31 452 B** surowo, **10 466 B** po gzip; 6 lokalnych requestów
  przy zimnym shellu i 1 przy ponownym wejściu przed requestami API.
- Jedno ostrzeżenie testowe: `StarletteDeprecationWarning` dotyczące
  przejściowej integracji TestClient/httpx. Nie jest błędem runtime.

## Konfiguracja ręczna

1. Utwórz `.env` i lokalne środowisko narzędzi:

   ```bash
   cd /home/maksu/lowband-gateway
   cp .env.example .env
   python3 -m venv .venv
   .venv/bin/python -m pip install -c constraints.txt -e '.[dev]'
   .venv/bin/python scripts/generate_password_hash.py
   .venv/bin/python scripts/generate_session_secret.py
   ```

2. W `.env` ustaw co najmniej:

   ```dotenv
   PUBLIC_BASE_URL=https://lowband.twoja-domena.pl
   APP_PASSWORD_HASH='$argon2id$...'
   SESSION_SECRET=<pierwszy-losowy-sekret>
   CODEX_RUNNER=http
   RUNNER_SHARED_SECRET=<drugi-niezależny-losowy-sekret>
   TUNNEL_TOKEN=<token-z-Cloudflare-Zero-Trust>
   ```

   Pozostaw `SECURE_COOKIES=true`, `REQUIRE_HTTPS=true`,
   `TRUST_PROXY_HEADERS=true` i
   `TRUSTED_PROXY_CIDRS=10.254.249.4/32`.

3. W Cloudflare Zero Trust utwórz Tunnel, przypisz public hostname dokładnie
   do `http://web:8080`, a token wklej wyłącznie do `TUNNEL_TOKEN` w `.env`.
   Nie otwieraj portu routera.

4. Zaloguj osobny wolumen Codexa:

   ```bash
   docker compose --profile codex up -d egress-proxy
   docker compose --profile codex run --rm --no-deps runner codex --version
   docker compose --profile codex run --rm --no-deps runner codex login --device-auth
   docker compose --profile codex run --rm --no-deps runner codex login status
   ```

5. Opcjonalnie ustaw ntfy:

   ```dotenv
   NTFY_ENABLED=true
   NTFY_BASE_URL=https://ntfy.sh
   NTFY_TOPIC=<długi-losowy-topic>
   NTFY_TOKEN=<token-jeżeli-wymagany>
   ```

## Bezpieczeństwo

Zabezpieczono uwierzytelnienie, sesję, CSRF, rate limiting, limity kosztowe,
idempotencję, prywatność wyników, nagłówki przeglądarki, logi, trwałość bazy,
recovery kolejki, izolację procesową i ograniczenie egressu. Publiczne ID jest
losowe, ale samo nigdy nie daje dostępu bez sesji.

Pozostałe ryzyka:

- root hosta i operator Docker daemon mają dostęp do wolumenów;
- Codex musi odczytywać własny credential modelu, więc prompt injection może
  próbować go wykraść; nie dostaje jednak sekretów aplikacji/infrastruktury;
- wewnętrzny bwrap nie działa przy `cap_drop: ALL`, więc granicą runnera jest
  zewnętrzny sandbox Docker/kernel;
- awaria po uzyskaniu wyniku modelu, lecz przed commitem SQLite, może
  powtórzyć płatne wykonanie (semantyka co najmniej raz);
- backup poza hostem i szyfrowanie nośnika pozostają obowiązkiem operatora;
- Cloudflare Access/WAF jest wskazany przy rozproszonych próbach logowania.

## Uruchomienie

Po wykonaniu konfiguracji ręcznej:

```bash
cd /home/maksu/lowband-gateway
docker compose --profile codex --profile tunnel build
docker compose run --rm migrate
docker compose --profile codex --profile tunnel up -d
docker compose --profile codex --profile tunnel ps
docker compose --profile codex logs --tail=100 web worker runner-gateway runner
```

Sprawdź lokalnie wewnątrz kontenera:

```bash
docker compose exec web python -c \
  "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"
```

Otwórz `PUBLIC_BASE_URL` w Safari, zaloguj się, wyślij kontrolowane zadanie i
sprawdź status w PWA. Szczegółowe procedury fake startu, Cloudflare, backupu,
restore, aktualizacji, rollbacku i troubleshooting znajdują się w
`README.md`.
