"""Deterministic field-level Foundry -> scraper -> bundled fallback.

Zero and False are real values. Lists are atomic to avoid duplicating effects.
Conflicting populated values are reported, never silently blended.
"""
from copy import deepcopy
import re
from models.entity import DiyargezenEntity

VERSION = 'pf1e-field-merge-v2'
RANK = {'foundry': 0, 'scraper': 1, 'bundled': 2}
PLACEHOLDERS = {'', 'benefit', 'benefit(s)', 'prerequisites', 'special', 'normal', 'description'}


def missing(value):
    return value is None or value == [] or value == {} or (isinstance(value, str) and value.strip().lower() in PLACEHOLDERS)


def merge_entities(entities):
    groups = {}
    for entity in entities:
        name = re.sub(r'\s*\((combat|teamwork|metamagic|grit|racial|performance|item creation)\)$', '', entity.isim.strip(), flags=re.I).casefold()
        groups.setdefault((entity.sistem, entity.kategori, name), []).append(entity)
    output = []
    for group in groups.values():
        group.sort(key=lambda e: RANK.get(e.sistem_verisi.get('data_source'), 3))
        primary = group[0]
        fields, conflicts, sources = {}, [], []
        merged = {}
        description = None
        for entity in group:
            source = entity.sistem_verisi.get('data_source', 'bundled')
            reference = entity.sistem_verisi.get('_source_ref', source)
            if reference not in sources:
                sources.append(reference)

            def merge(target, incoming, prefix=''):
                for key, value in incoming.items():
                    if key in {'data_source', '_source_ref', '_provenance'}:
                        continue
                    path = prefix + key
                    if isinstance(value, dict) and isinstance(target.get(key, {}), dict):
                        target.setdefault(key, {})
                        merge(target[key], value, path + '.')
                    elif missing(target.get(key)) and not missing(value):
                        target[key] = deepcopy(value)
                        fields[path] = source
                    elif not missing(value) and not missing(target.get(key)) and target[key] != value:
                        conflicts.append({'field': path, 'chosen_source': fields.get(path, 'foundry'), 'other_source': source})
            merge(merged, entity.sistem_verisi)
            if missing(description) and not missing(entity.aciklama):
                description = entity.aciklama
                fields['aciklama'] = source
            elif not missing(entity.aciklama) and entity.aciklama != description:
                conflicts.append({'field': 'aciklama', 'chosen_source': fields.get('aciklama'), 'other_source': source})
        fallback = sorted(path for path, source in fields.items() if source == 'scraper')
        merged['data_source'] = primary.sistem_verisi.get('data_source', 'bundled')
        merged['_provenance'] = {'version': VERSION, 'sources': sources,
                                 'field_sources': fields, 'fallback_fields': fallback, 'conflicts': conflicts}
        output.append(DiyargezenEntity(isim=primary.isim, sistem=primary.sistem, kategori=primary.kategori,
                                      aciklama=description or '', sistem_verisi=merged))
    return output
