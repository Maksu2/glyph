-- SQLite JSON1. Bind the full contents of
-- data/processed/glyph100_v2_4_1_metadata.json as :metadata_json.

WITH metadata AS (SELECT json(:metadata_json) AS doc)
SELECT
  json_extract(doc, '$.total_tokens') / 1000000.0 AS total_tokens_m,
  json_extract(doc, '$.wikipedia_share') AS wikipedia_share
FROM metadata;

WITH metadata AS (SELECT json(:metadata_json) AS doc)
SELECT
  source.key AS source,
  json_extract(source.value, '$.tokens') / 1000000.0 AS tokens_m,
  json_extract(source.value, '$.tokens') * 1.0 / json_extract(doc, '$.total_tokens') AS share,
  json_extract(source.value, '$.selected_docs') AS documents,
  CASE source.key WHEN 'wikisource' THEN 'train only' ELSE 'train + val' END AS validation_policy
FROM metadata, json_each(doc, '$.sources') AS source
ORDER BY json_extract(source.value, '$.tokens') DESC;

WITH metadata AS (SELECT json(:metadata_json) AS doc),
stages(stage, steps) AS (VALUES ('1k', 1000), ('5k', 5000), ('20k', 20000), ('50k', 50000))
SELECT
  stage,
  steps,
  steps * 16384 / 1000000.0 AS tokens_m,
  steps * 16384.0 / json_extract(doc, '$.train_tokens') AS train_passes
FROM metadata, stages;
