from scripts.glyph100_dataset_v2_4_2_build import rejection_reasons


def test_rejects_wikipedia_locality_template():
    text = (
        "Według danych z 31 grudnia 2019 r. gminę zamieszkiwało 317 osób. "
        "Struktura powierzchni obejmuje 148 km2."
    )
    reasons = rejection_reasons("wikipedia_pl", text)
    assert "wiki_population_template" in reasons
    assert "wiki_surface_template" in reasons


def test_keeps_normal_wikipedia_prose():
    text = (
        "Energia jest wielkością fizyczną opisującą zdolność układu do wykonania pracy. "
        "Może występować w wielu postaciach, między innymi jako energia kinetyczna."
    )
    assert rejection_reasons("wikipedia_pl", text) == []


def test_rejects_heavy_legal_citations():
    text = (
        "Zgodnie z art. 1, art. 2, art. 3, art. 4 i art. 5 oraz ust. 1, ust. 2, "
        "ust. 3, ust. 4, ust. 5 i ust. 6 przywołano Dz. U., Dz. U. oraz Dz. U."
    )
    assert "parliamentary_legal_citation_heavy" in rejection_reasons("parliamentary", text)


def test_rejects_wikisource_page_header():
    text = "376WYBÓR PISM J. I. KRASZEWSKIEGO. Dalej rozpoczyna się tekst utworu."
    assert "wikisource_page_header_ocr" in rejection_reasons("wikisource", text)


def test_rejects_source_metadata_preamble():
    text = "Z cmentarzy <<< Dane tekstu Autor Maria Konopnicka Skany na Commons Inne Cały tekst Indeks stron."
    assert "source_metadata_preamble" in rejection_reasons("1000_novels", text)


def test_rejects_wiki_media_residue():
    text = "left|150px Demokraci przygotowali reklamówkę wyborczą."
    assert "wiki_media_residue" in rejection_reasons("wikinews", text)


def test_rejects_administrative_locality_lead():
    text = (
        "Gnaszyn-Kawodrza to dzielnica Częstochowy. Dzielnica obejmuje miejscowość "
        "położoną administracyjnie w granicach gminy."
    )
    assert "wiki_locality_administrative_lead" in rejection_reasons("wikipedia_pl", text)
