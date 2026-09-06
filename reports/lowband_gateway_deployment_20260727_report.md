# Lowband Gateway — raport wdrożenia produkcyjnego

Data zakończenia: 2026-07-27 19:39 UTC  
Adres: `https://lowband.maksu.online`  
Stan: uruchomiony i dostępny publicznie wyłącznie przez Cloudflare Tunnel.

## Wynik

Lowband Gateway działa produkcyjnie. Sześć usług pozostaje uruchomionych:
`web`, `worker`, `runner-gateway`, `runner`, `egress-proxy` i `cloudflared`.
Usługi z healthcheckami są zdrowe, a publiczny `/health` zwraca wyłącznie
`{"status":"ok"}`.

Nie opublikowano żadnego portu hosta. Dedykowany tunel `lowband-gateway`
łączy się z Cloudflare czterema połączeniami i przekazuje ruch bezpośrednio do
`http://web:8080` w prywatnej sieci Compose. Istniejący systemowy tunel
Minecraft nie został zmodyfikowany ani zatrzymany.

## Konfiguracja

- `PUBLIC_BASE_URL=https://lowband.maksu.online`.
- Model: `gpt-5.6-terra`.
- Reasoning: `medium`.
- Runner: izolowany wariant HTTP/Docker.
- ntfy: wyłączone, ponieważ nie podano topicu ani tokenu.
- Cloudflare Access: opcjonalne i obecnie niewłączone.
- `.env`: prawa `0600`; tokenowy tryb tunelu wyłączony.
- Lokalny config Cloudflare: prawa `0600`.
- Hostowy credential tunelu: prawa `0400`.
- Kopie configu i credentialu w prywatnym wolumenie są własnością UID 65532,
  mają tryb `0400` i są montowane do produkcyjnego cloudflared read-only.
- `COMPOSE_FILE=compose.yaml:compose.local-tunnel.yaml` chroni przed
  przypadkowym uruchomieniem niewłaściwego wariantu tunelu.

## Codex

Host był zalogowany przez ChatGPT. Credential został jednorazowo skopiowany
do osobnego wolumenu `runner-codex-home`; katalog hostowego Codexa nie jest
montowany do usługi. Produkcyjny runner potwierdził `Logged in using ChatGPT`.

Runner działa jako UID 10001, z read-only root filesystem, bez capabilities i
bez sekretów aplikacji. Po rzeczywistym zadaniu katalog `/runner/jobs`
pozostał pusty.

## Publiczny E2E

Pełny przebieg przez `https://lowband.maksu.online`:

1. logowanie właściwym hasłem;
2. trwały `POST /api/v1/jobs`;
3. odpowiedź `queued` po 0,276 s;
4. zamknięcie pierwszego klienta;
5. wykonanie w izolowanym runnerze przez Terra `medium`;
6. końcowy status `done`;
7. ponowne logowanie niezależnego klienta;
8. pobranie wyniku;
9. warunkowy GET zwrócił `304`.

Pierwszy celowo ogólny prompt kontrolny poprawnie zakończył się
`needs_user`. Doprecyzowany test `2 + 2` zakończył się `done`. Oba zadania
usunięto później przez autoryzowane API. Wszystkie testowe sesje zostały
unieważnione. Pozostały dwa beztreściowe rekordy `job_usage`, zgodnie z
polityką limitów i idempotencji.

## Walidacja bezpieczeństwa

- HTTP przekierowuje kodem `308` do HTTPS.
- HTTPS `/health`: `200`.
- API zadań bez sesji: `401`.
- Manifest PWA i service worker: `200`.
- CSP, HSTS, nosniff, DENY, Referrer-Policy i Permissions-Policy obecne.
- Runner: UID 10001, read-only, `cap_drop=ALL`, zero zabronionych sekretów.
- Cloudflared: UID 65532, read-only, `cap_drop=ALL`.
- Porty usług są wyłącznie wewnętrzne.
- SQLite: `integrity_check=ok`, WAL, migracja `0003_system_job_events`.
- Baza po testach: zero zadań i zero aktywnych sesji.
- Worker heartbeat: zdrowy.
- Backup online utworzony w
  `/data/backups/lowband-deployed-20260727.sqlite`; integralność `ok`.

Podczas wdrożenia pierwsza wersja tunelu została natychmiast usunięta i
utworzona ponownie, ponieważ diagnostyczny format JSON CLI wypisał credential.
Ujawniony credential został w ten sposób unieważniony przed utworzeniem trasy
DNS. Rekord DNS został następnie jawnie przypisany do nowego, dedykowanego
tunelu. Nie doszło do dostępu do aplikacji przez niewłaściwy tunel.

## Testy repozytorium

- `ruff check`: zaliczone.
- `ruff format --check`: zaliczone.
- `compileall`: zaliczone.
- `pip check`: zaliczone.
- składnia JavaScriptu: zaliczona.
- konfiguracja Compose z lokalnym tunelem: zaliczona.
- pytest: **66 passed, 1 opt-in skipped, 0 failed**.
- Jedno ostrzeżenie: deprecjacja testowego adaptera Starlette/httpx.
- Rzeczywisty publiczny E2E Codexa: zaliczony niezależnie od testów unit.

## Dostęp użytkownika

Hasło startowe nie znajduje się w repozytorium ani `.env`. Jest tymczasowo
zapisane tylko w prywatnym tmpfs użytkownika:

```bash
cat /run/user/1000/lowband-gateway-initial-password
```

Po zapisaniu go w menedżerze haseł usuń plik:

```bash
rm /run/user/1000/lowband-gateway-initial-password
```

Następnie otwórz `https://lowband.maksu.online` w Safari i opcjonalnie dodaj
PWA do ekranu głównego.

## Obsługa

`.env` ustawia oba pliki Compose, dlatego standardowe komendy na tym hoście to:

```bash
cd /home/maksu/lowband-gateway
docker compose --profile codex --profile tunnel ps
docker compose --profile codex --profile tunnel logs --tail=100
docker compose --profile codex --profile tunnel up -d
docker compose --profile codex --profile tunnel stop
```

Nie używaj `docker compose down -v`, chyba że świadomie chcesz usunąć bazę,
credential Codexa oraz konfigurację tunelu z wolumenów.
