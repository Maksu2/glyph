-- SQLite JSON1. Bind the full contents of
-- reports/glyph100_next_step_20260716_eos_recheck.json as :eos_json.

WITH payload AS (SELECT json(:eos_json) AS doc)
SELECT
  summary.key AS checkpoint_and_preset,
  json_extract(summary.value, '$.avg_quality_score') AS avg_quality,
  json_extract(summary.value, '$.eos_endings') AS eos_endings,
  json_extract(summary.value, '$.repetition_samples') AS repetitions,
  json_extract(summary.value, '$.max_token_cutoffs') AS cutoffs
FROM payload, json_each(doc, '$.summary') AS summary;

WITH payload AS (SELECT json(:eos_json) AS doc)
SELECT
  json_extract(doc, '$.pairwise."44k"') AS wins_44k,
  json_extract(doc, '$.pairwise."50k"') AS wins_50k,
  json_extract(doc, '$.pairwise.tie') AS ties
FROM payload;
