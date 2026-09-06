# Glyph SFT v0 dataset validation

## glyph100_sft_smoke_v0.jsonl

- examples: 1500
- invalid JSON lines: 0
- records with missing fields: 0
- total words: 29109
- avg instruction words: 8.7
- avg response words: 10.7
- duplicate instructions, extra copies: 0
- duplicate instruction+response pairs, extra copies: 0
- real tokenizer template tokens: 57865
- template tokens avg/p50/p90/p95/max: 38.6 / 39.0 / 47.0 / 50.0 / 65
- fits context 256: 1500
- over context 256: 0

### Categories

- anty_petle: 150
- brak_danych: 150
- codzienne_proste_pytania: 150
- krotkie_definicje: 150
- krotkie_poprawki_tekstu: 150
- mini_streszczenia: 150
- mvp_first_project_advice: 150
- naturalne_zakonczenia: 150
- ostrozne_odpowiedzi_przy_niepewnosci: 150
- proste_techniczne_wyjasnienia: 150

### Bad-pattern checks

- empty_instruction: 0
- empty_response: 0
- very_short_response_lt_8_words: 300
- very_long_response_gt_120_words: 0
- control_chars: 0
- as_language_model_phrase: 0
- english_pattern: 0

### Similar instruction pairs sample

- lines 46 / 1487 score=0.889: 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Zwięźle.' <> 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss?'
- lines 203 / 1487 score=0.889: 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Bez metafor.' <> 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss?'
- lines 687 / 1487 score=0.889: 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Bez listy.' <> 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss?'
- lines 1331 / 1487 score=0.889: 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Nie powtarzaj.' <> 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss?'
- lines 1379 / 1487 score=0.889: 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Bez dygresji.' <> 'Nie rozwijaj bez końca: dlaczego warto mierzyć loss?'
- lines 4 / 166 score=0.917: 'Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?' <> 'Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej? Odpowiedz wprost.'
- lines 4 / 1268 score=0.917: 'Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?' <> 'Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej? Zwięźle.'
- lines 4 / 1295 score=0.917: 'Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?' <> 'Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej? Jednym zdaniem.'
- lines 162 / 689 score=0.889: 'Czy można porównać modele bez tych samych promptów?' <> 'Czy można porównać modele bez tych samych promptów? Krótko.'
- lines 466 / 990 score=0.9: 'Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.' <> 'Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj. Naturalnie.'
