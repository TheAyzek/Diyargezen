from models.entity import DiyargezenEntity
from parsers.pf1e_unified import merge_entities
from db.entity_store import init_game_schema, bulk_upsert_entities, list_entities, _source_fingerprint


def entity(source, data, description='', name='Power Attack'):
    return DiyargezenEntity(isim=name, sistem='pathfinder1e', kategori='feat', aciklama=description,
                            sistem_verisi={**data, 'data_source': source})


def test_field_fallback_keeps_primary_values_and_reports_sources():
    primary = entity('foundry', {'weight': 0, 'active': False, 'system': {'bab': '', 'prerequisites': 'Str 13'}})
    scraped = entity('scraper', {'weight': 2, 'active': True, 'system': {'bab': 1, 'prerequisites': 'Str 15'}}, 'Useful rule text')
    merged = merge_entities([scraped, primary])[0]
    assert merged.sistem_verisi['weight'] == 0
    assert merged.sistem_verisi['active'] is False
    assert merged.sistem_verisi['system'] == {'bab': 1, 'prerequisites': 'Str 13'}
    assert merged.aciklama == 'Useful rule text'
    provenance = merged.sistem_verisi['_provenance']
    assert set(provenance['fallback_fields']) == {'system.bab', 'aciklama'}
    assert {item['field'] for item in provenance['conflicts']} == {'weight', 'active', 'system.prerequisites'}
    assert primary.sistem_verisi['system']['bab'] == ''


def test_fallback_lists_are_atomic_and_categories_never_merge():
    primary = entity('foundry', {'changes': []}, name='Power Attack (Combat)')
    scraped = entity('scraper', {'changes': [{'value': 2}]})
    assert len(merge_entities([primary, scraped])) == 1
    assert merge_entities([primary, scraped])[0].sistem_verisi['changes'] == [{'value': 2}]
    scraped.kategori = 'spell'
    assert len(merge_entities([primary, scraped])) == 2


def test_catalog_upsert_keeps_unrelated_rows_and_provenance(tmp_path):
    db = tmp_path / 'catalog.db'
    init_game_schema(db)
    bulk_upsert_entities(db, [entity('foundry', {}, name='Custom feat')], 'pathfinder1e')
    merged = merge_entities([entity('foundry', {}), entity('scraper', {'bonus': 2})])
    bulk_upsert_entities(db, merged, 'pathfinder1e')
    records = list_entities(db, 'pathfinder1e')
    assert len(records) == 2
    assert next(r for r in records if r.isim == 'Power Attack').sistem_verisi['_provenance']['field_sources']['bonus'] == 'scraper'


def test_foundry_and_scraper_changes_invalidate_catalog_fingerprint(tmp_path):
    source = tmp_path / 'pf1e-content-main'
    source.mkdir()
    before = _source_fingerprint(tmp_path, ['pf1e_scraped_items.json'])
    (source / 'feat.json').write_text('{}')
    foundry = _source_fingerprint(tmp_path, ['pf1e_scraped_items.json'])
    (tmp_path / 'pf1e_scraped_items.json').write_text('[]')
    assert len({before, foundry, _source_fingerprint(tmp_path, ['pf1e_scraped_items.json'])}) == 3


def test_etl_aliases_parse_and_write_once(tmp_path, monkeypatch):
    from etl import pipeline
    calls = []
    monkeypatch.setattr(pipeline, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(pipeline, 'PARSERS', {
        'pathfinder1e': lambda **kwargs: calls.append('parse') or [entity('foundry', {})],
        'pf1e': lambda **kwargs: calls.append('duplicate') or [],
    })
    result = pipeline.run_etl(db_path=tmp_path / 'etl.db', systems=['pf1e', 'pathfinder1e'], force=True)
    assert result == {'pathfinder1e': 1}
    assert calls == ['parse']
