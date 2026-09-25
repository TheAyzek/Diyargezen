def test_parsing_spells_never_opens_or_writes_a_database(monkeypatch):
    import sqlite3
    from parsers.base import make_entity
    def forbidden(*args, **kwargs):
        raise AssertionError('Parser must not open any database')
    monkeypatch.setattr(sqlite3, 'connect', forbidden)
    spell = make_entity('Light', 'pathfinder1e', 'spell', {'name': 'Light', 'type': 'spell', 'system': {'level': 0}})
    assert spell is not None
    assert spell.isim == 'Light'


def test_batch_spell_projection_uses_only_explicit_database(tmp_path):
    import sqlite3
    from parsers.base import make_entity
    from db.entity_store import init_game_schema, bulk_upsert_entities
    path = tmp_path / 'catalog.db'
    init_game_schema(path)
    spell = make_entity('Light', 'pathfinder1e', 'spell', {'name': 'Light', 'type': 'spell', 'system': {'level': 0}})
    bulk_upsert_entities(path, [spell], 'pathfinder1e')
    with sqlite3.connect(path) as db:
        assert db.execute('SELECT isim FROM spells').fetchall() == [('Light',)]
