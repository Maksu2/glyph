# Glyph public site

Static public showcase page for `glyph.maksu.online`.

It is intentionally separate from the private training dashboard. The site exposes only public, sanitized project information: model card style metadata, a training snapshot, evaluation summary, samples, limitations and roadmap.

## Run locally

From the repository root:

```bash
python3 site/serve.py
```

Then open:

```text
http://127.0.0.1:8194/
```

For a throwaway static preview, this also works:

```bash
python3 -m http.server 8193 --directory site
```

## Content

- Polish copy: `content/pl.json`
- English copy: `content/en.json`
- Model metadata: `data/model.json`
- Public training snapshot: `data/training.json`
- Public evaluation snapshot: `data/evaluation.json`
- Public samples: `data/samples.json`

The language is selected from `navigator.language` on first visit. If it starts with `pl`, the Polish version is shown; otherwise English is shown. Manual selection through the PL/EN switch is stored in `localStorage`.

## Data refresh

Public JSON snapshots are generated from local logs and reports by:

```bash
python3 scripts/export_public_site_data.py --sample-limit 6
```

The user timer `glyph-public-snapshot.timer` refreshes training progress every 5 minutes. The nightly Gemma evaluation cycle also runs the exporter after writing new judge reports, so `data/evaluation.json` and `data/samples.json` follow the newest nightly run.

## Assets

The active logo files are:

- `assets/glyph_mark.png`
- `assets/glyph_logotext.png`

Replace those files to update the branding. Keep filenames stable unless `index.html`, `styles.css` and `src/app.js` are updated too.

## Deployment note

The static root can be the `site/` directory. Do not expose the private training dashboard, host paths, service ports, checkpoint paths or admin endpoints through this page.

The public inference demo is proxied through `POST /api/generate` to a separate local backend. See `docs/inference-demo.md` for the backend, Docker isolation, rate limits and kill switch.

Current deployment target:

- public URL: `https://glyph.maksu.online/`
- origin service: `glyph-public-site.service`
- tunnel service: `cloudflared-glyph-public.service`
- tunnel config: `~/.cloudflared/glyph-public.yml`
