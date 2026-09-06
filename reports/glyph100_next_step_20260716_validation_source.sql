-- SQLite JSON1. Bind the full contents of
-- reports/glyph100_next_step_20260716_v2_4_1_validation.json as :validation_json.

WITH payload AS (SELECT json(:validation_json) AS doc)
SELECT
  checks.key AS check_name,
  CASE checks.value WHEN 1 THEN 'PASS' ELSE 'FAIL' END AS status
FROM payload, json_each(doc, '$.checks') AS checks;

WITH payload AS (SELECT json(:validation_json) AS doc)
SELECT
  json_extract(doc, '$.observed_total_tokens') AS total_tokens,
  json_extract(doc, '$.observed_docs') AS documents,
  json_extract(doc, '$.observed_parents') AS parent_documents,
  json_extract(doc, '$.parent_leakage_count') AS parent_leakage,
  json_extract(doc, '$.duplicate_ids') AS duplicate_ids
FROM payload;
