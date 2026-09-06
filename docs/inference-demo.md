# Glyph public inference demo

This is the public, locked-down inference demo used by `glyph.maksu.online`.

It is intentionally not a chatbot product. It exposes one controlled endpoint:

```text
POST /api/generate
```

The public site proxies this endpoint to the local inference backend. The private training dashboard, training controls, host paths, Docker socket and homelab services are not exposed.

## Demo checkpoint

The public demo must not use the actively written `checkpoints/latest.pt`.

Current demo checkpoint:

```text
checkpoints/public-demo.pt
```

It was copied from a stable numbered checkpoint:

```text
checkpoints/step_0115000.pt
```

To refresh it later, stop the inference service first or write to a new file and switch the env var after the copy finishes.

## Local backend

Run without Docker:

```bash
GLYPH_DEMO_ENABLED=true \
GLYPH_DEMO_CHECKPOINT=checkpoints/public-demo.pt \
GLYPH_DEMO_TOKENIZER=data/processed/tokenizer.model \
GLYPH_DEMO_HOST=127.0.0.1 \
GLYPH_DEMO_PORT=8195 \
.venv/bin/python inference/server.py
```

Health check:

```bash
curl http://127.0.0.1:8195/health
```

Generate:

```bash
curl -sS http://127.0.0.1:8195/api/generate \
  -H 'Content-Type: application/json' \
  --data '{"prompt":"Robotyka to dziedzina, która"}'
```

## Docker

Build and run the isolated backend:

```bash
docker compose -f docker-compose.inference.yml build
docker compose -f docker-compose.inference.yml up -d glyph-inference
```

The service binds only to localhost:

```text
127.0.0.1:8195
```

## Main env vars

```text
GLYPH_DEMO_ENABLED=true|false
GLYPH_DEMO_CHECKPOINT=/app/checkpoints/public-demo.pt
GLYPH_DEMO_TOKENIZER=/app/data/processed/tokenizer.model
GLYPH_DEMO_MAX_PROMPT_CHARS=500
GLYPH_DEMO_MAX_NEW_TOKENS=120
GLYPH_DEMO_TIMEOUT_SECONDS=45
GLYPH_DEMO_CONCURRENCY=1
GLYPH_DEMO_QUEUE_SIZE=4
GLYPH_DEMO_THREADS=4
GLYPH_DEMO_TEMPERATURE=0.75
GLYPH_DEMO_TOP_K=40
GLYPH_DEMO_TOP_P=0.92
GLYPH_DEMO_REPETITION_PENALTY=1.15
GLYPH_DEMO_NO_REPEAT_NGRAM=4
GLYPH_DEMO_RATE_PER_MINUTE=3
GLYPH_DEMO_RATE_PER_10_MINUTES=10
GLYPH_DEMO_RATE_PER_DAY=30
```

Kill switch:

```bash
GLYPH_DEMO_ENABLED=false
```

## Security notes

The Docker service:

- runs as non-root,
- mounts only `public-demo.pt` and `tokenizer.model`, both read-only,
- does not mount `/home/maksu`, `/mnt/data`, `.env` files or `/var/run/docker.sock`,
- uses `read_only: true`,
- drops all Linux capabilities,
- uses `no-new-privileges:true`,
- has memory and process limits,
- exposes only localhost.

The backend logs metadata only:

- timestamp,
- hashed IP key,
- prompt length,
- duration,
- status/error type.

Prompt contents and model outputs are not logged by default.

## Cloudflare hardening

Recommended edge settings for `https://glyph.maksu.online/api/generate`:

- allow `POST` and `OPTIONS`,
- body size limit around 4 KB,
- Cloudflare rate limiting in addition to backend limits,
- bot protection if spam appears,
- Turnstile only if abuse becomes real.
