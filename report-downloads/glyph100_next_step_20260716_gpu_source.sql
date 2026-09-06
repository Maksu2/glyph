-- SQLite JSON1. Bind the full contents of
-- reports/glyph100_next_step_20260716_gpu_pipeline_smoke.json as :gpu_smoke_json.

WITH payload AS (SELECT json(:gpu_smoke_json) AS doc)
SELECT
  json_extract(doc, '$.result.tokens_per_second') AS gpu_tokens_per_second,
  json_extract(doc, '$.result.loss') AS loss,
  json_extract(doc, '$.runtime.effective_tokens_per_step') AS effective_tokens_per_step,
  json_extract(doc, '$.result.nan_inf') AS nan_inf,
  json_extract(doc, '$.result.oom') AS oom,
  json_extract(doc, '$.result.crash') AS crash
FROM payload;
