#!/usr/bin/env python3
"""Export validated data dictionary workbooks to an I14Y-oriented JSON bundle.

This exporter does two things:
1. Emits API-aligned payload fragments for the I14Y Partner API based on the
   published OpenAPI spec captured from I14Y-ch/apiconsole.
2. Preserves semantic anchors that are critical for the PoC but are not first-
   class fields in the partner API payloads yet (IFC/QUDT/SKOS cross-links).

The resulting bundle is intentionally richer than a direct API POST body. The
`partnerApi` section contains strict request payload wrappers. The `semantic`
section preserves anchors and cross-links so they are never lost between
pipeline stages.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT = BASE_DIR / 'out' / 'i14y_bundle.json'
PARTNER_SPEC = BASE_DIR / 'external' / 'apiconsole__partner__v1__Release.json'


def slug(text: str) -> str:
    text = (text or '').strip().lower()
    repl = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        ' ': '-', '/': '-', '_': '-', '(': '', ')': '', ',': '-', '.': '-',
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    text = re.sub(r'[^a-z0-9\-]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text or 'item'


def parse_date(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s + 'T00:00:00+00:00'
    return s


def ml(de=None, en=None, fr=None, it=None, rm=None):
    data = {'de': de, 'en': en, 'fr': fr, 'it': it, 'rm': rm}
    return {k: v for k, v in data.items() if v not in (None, '')}


def code_model(code: str | None):
    return {'code': code} if code else None


def identifier_model(identifier: str | None):
    return {'identifier': identifier} if identifier else None


def email_model(email: str | None):
    return {'email': email} if email else None


def resource_model(uri: str | None, de=None, en=None, fr=None, it=None):
    if not uri:
        return None
    obj = {'uri': uri}
    labels = ml(de=de, en=en, fr=fr, it=it)
    if labels:
        obj['label'] = labels
    return obj


def split_listish(value: Any) -> list[str]:
    if value in (None, ''):
        return []
    parts = re.split(r'[;,|]', str(value))
    return [p.strip() for p in parts if p and p.strip()]


def first_nonempty(*vals):
    for v in vals:
        if v not in (None, ''):
            return v
    return None


@dataclass
class WorkbookContext:
    path: Path
    wb: Any
    title: str
    publisher: str
    contact_email: str | None
    version: str
    release_date: str | None
    modified_date: str | None
    metadata: dict[str, Any]
    lindas_base: str
    dataset_identifier: str
    dataset_uri: str


def read_dictionary_public(wb) -> dict[str, Any]:
    if 'Dictionary_public' not in wb.sheetnames:
        return {}
    ws = wb['Dictionary_public']
    meta = {}
    for row in range(4, ws.max_row + 1):
        field = ws.cell(row, 1).value
        value = ws.cell(row, 2).value
        if field and isinstance(field, str) and not field.startswith('──'):
            meta[field.strip()] = value
    return meta


def infer_context(path: Path) -> WorkbookContext:
    wb = load_workbook(path, data_only=True)
    meta = read_dictionary_public(wb)
    name = path.stem
    if 'kbob' in name.lower():
        title = 'KBOB FM Data Dictionary'
        publisher = 'kbob'
    elif 'area' in name.lower() or 'areamgmt' in name.lower():
        title = 'bDCH Area Management Data Dictionary'
        publisher = 'bdch'
    else:
        title = name
        publisher = slug(name)
    title = first_nonempty(meta.get('Title'), meta.get('Name'), title)
    publisher = first_nonempty(meta.get('Owner / Publisher'), publisher)
    contact_email = meta.get('ContactEmail')
    version = first_nonempty(meta.get('Version'), '0.1.0')
    release_date = parse_date(meta.get('ReleaseDate'))
    modified_date = parse_date(meta.get('ModifiedDate')) or release_date
    lindas_base = 'https://lindas.admin.ch/fobl/kbob/dd-fm'
    dataset_identifier = slug(name)
    dataset_uri = f'https://i14y.admin.ch/catalog/{dataset_identifier}'
    return WorkbookContext(path, wb, title, publisher, contact_email, version, release_date, modified_date, meta, lindas_base, dataset_identifier, dataset_uri)


def rowdict(ws, header_row=1, data_start=8):
    headers = {c: str(ws.cell(header_row, c).value).strip() for c in range(1, ws.max_column + 1) if ws.cell(header_row, c).value}
    rows = []

    def is_guidance_row(row_index: int) -> bool:
        vals = [ws.cell(row_index, c).value for c in range(1, ws.max_column + 1)]
        joined = ' | '.join(str(v).strip() for v in vals if v not in (None, '')).lower()
        markers = [
            'erforderlich für excel', 'erforderlich für merkmalkatalog', 'erforderlich für data dictionary',
            'sprachen', 'referenziert / system generiert', 'dropdown liste', 'validierung',
            'hinweise zur handhabung'
        ]
        return any(m in joined for m in markers)

    start = data_start
    for candidate in range(2, data_start + 1):
        vals = [ws.cell(candidate, c).value for c in range(1, ws.max_column + 1)]
        has_any = any(v not in (None, '') for v in vals)
        if has_any and not is_guidance_row(candidate):
            start = candidate
            break
    while start <= ws.max_row and is_guidance_row(start):
        start += 1

    for r in range(start, ws.max_row + 1):
        rec = {}
        anyv = False
        for c, h in headers.items():
            v = ws.cell(r, c).value
            if v not in (None, ''):
                anyv = True
            rec[h] = v
        if anyv:
            rec['_row'] = r
            rows.append(rec)
    return rows


def infer_concept_type(prop: dict, values_by_prop: dict[str, list[dict]]) -> tuple[str, dict[str, Any]]:
    code = str(prop.get('Property-Code') or '').strip()
    datatype = str(prop.get('DataType\n(Base Type)') or prop.get('DataType') or '').strip().upper()
    if values_by_prop.get(code):
        maxlen = max((len(str(v.get('Enumeration (EN)') or v.get('Bezeichnung (DE)') or '')) for v in values_by_prop[code]), default=0)
        return 'CodeList', {
            'codeListEntryDefaultSortProperty': 'Code',
            'codeListEntryValueType': 'String',
            'codeListEntryValueMaxLength': max(maxlen, 1),
        }
    if datatype in {'INTEGER', 'REAL', 'DECIMAL', 'NUMBER'} or 'MEASURE' in datatype:
        return 'Numeric', {}
    if datatype in {'BOOLEAN'}:
        return 'String', {'minLength': 1, 'maxLength': 5, 'pattern': '^(true|false|TRUE|FALSE|0|1)$'}
    maxlen = max(len(str(first_nonempty(prop.get('Designation (EN)'), prop.get('Bezeichnung (DE)'), code, 'x'))), 1)
    return 'String', {'minLength': 0, 'maxLength': maxlen * 4}


def build_dataset_payload(ctx: WorkbookContext) -> dict[str, Any]:
    meta = ctx.metadata
    descriptions = ml(
        de=first_nonempty(meta.get('Description (DE)'), f'{ctx.title} published from validated schemaforge workbook.'),
        en=first_nonempty(meta.get('Description (EN)'), f'{ctx.title} published from validated schemaforge workbook.'),
        fr=meta.get('Description (FR)'),
        it=meta.get('Description (IT)'),
    )
    title_ml = ml(
        de=first_nonempty(meta.get('Title (DE)'), ctx.title),
        en=first_nonempty(meta.get('Title (EN)'), ctx.title),
        fr=meta.get('Title (FR)'),
        it=meta.get('Title (IT)'),
    )
    doc_urls = split_listish(meta.get('DocumentationURLs'))
    related_urls = split_listish(meta.get('RelatedResourceURLs'))
    data = {
        'accessRights': code_model(first_nonempty(meta.get('AccessRights'), 'public')),
        'description': descriptions,
        'publisher': identifier_model(ctx.publisher),
        'title': title_ml,
        'identifiers': [ctx.dataset_identifier, str(ctx.path)],
        'issued': ctx.release_date,
        'modified': ctx.modified_date,
        'version': ctx.version,
        'versionNotes': ml(de=meta.get('VersionNotes (DE)'), en=meta.get('VersionNotes (EN)'), fr=meta.get('VersionNotes (FR)')),
        'landingPages': [resource_model(first_nonempty(meta.get('MoreInfoUrl'), ctx.dataset_uri), en='I14Y dataset landing page')],
        'documentation': [resource_model(u) for u in doc_urls if u],
        'relations': [resource_model(u) for u in related_urls if u],
        'conformsTo': [x for x in [
            resource_model(first_nonempty(meta.get('ConformsTo_ISO23386'), 'https://www.iso.org/standard/75401.html'), en='ISO 23386'),
            resource_model(meta.get('ConformsTo_DCAT_AP_CH'), en='DCAT-AP CH') if meta.get('ConformsTo_DCAT_AP_CH') else None,
        ] if x],
        'responsiblePerson': email_model(first_nonempty(ctx.contact_email, 'placeholder@example.org')),
        'responsibleDeputy': email_model(ctx.contact_email) if ctx.contact_email else None,
        'keywords': [
            {'label': ml(en='data dictionary')},
            {'label': ml(en='schemaforge')},
            {'label': ml(en='lindas', de='LINDAS')},
        ],
        'languages': [code_model(code) for code in ['de', 'en']],
    }
    data = {k: v for k, v in data.items() if v not in (None, [], {})}
    return {'data': data}


def build_concepts(ctx: WorkbookContext, classes: list[dict], props: list[dict], gops: list[dict], values: list[dict], concept_relations: list[dict]):
    by_prop_code: dict[str, list[dict]] = {str(p.get('Property-Code') or '').strip(): [] for p in props}
    for v in values:
        enum_bucket = str(v.get('Werteliste\n(DE)') or v.get('Liste de valeurs\n(FR)') or v.get('Lista valori\n(IT)') or v.get('Enumeration (EN)') or '').strip()
        for p in props:
            if str(p.get('EnumerationDesignation (EN)') or '').strip() == enum_bucket:
                by_prop_code[str(p.get('Property-Code') or '').strip()].append(v)
    concepts = []
    semantic_index = []
    for c in classes:
        owned = first_nonempty(c.get('GUID/URI'), f"{ctx.lindas_base}/class/class/{slug(c.get('Designation (EN)') or c.get('Bezeichnung (DE)') or c.get('Class-Code'))}")
        payload = {
            'data': {
                'conceptType': 'String',
                'minLength': 0,
                'maxLength': 512,
                'name': ml(de=c.get('Bezeichnung (DE)'), en=c.get('Designation (EN)'), fr=c.get('Désignation (FR)'), it=c.get('Designazione (IT)')),
                'description': ml(de=c.get('Beschreibung (DE)'), en=c.get('Description (EN)'), fr=c.get('Description (FR)'), it=c.get('Descrizione (IT)')),
                'publisher': identifier_model(ctx.publisher),
                'responsiblePerson': email_model(first_nonempty(ctx.contact_email, 'placeholder@example.org')),
                'version': str(c.get('Version date') or ctx.version),
                'identifiers': [str(c.get('Class-Code') or ''), str(owned)],
                'conformsTo': [x for x in [
                    resource_model(c.get('IFC_URI'), en='IFC 4.3 SSOT class pointer'),
                    resource_model(owned, en='LINDAS authoritative class IRI'),
                    resource_model(ctx.dataset_uri, en='I14Y dataset record')
                ] if x],
            }
        }
        concepts.append(payload)
        semantic_index.append({
            'kind': 'class',
            'code': c.get('Class-Code'),
            'ownedUri': owned,
            'ifcUri': c.get('IFC_URI'),
            'ifcEntity': c.get('IfcObject Entity'),
            'ifcTypeObjectEntity': c.get('IfcTypeObject Entity'),
            'predefinedType': c.get('PredefinedType'),
            'sourceWorkbook': str(ctx.path),
            'i14yDatasetUri': ctx.dataset_uri,
        })
    for g in gops:
        code = str(g.get('GoP-Code') or g.get('GoP-ID') or '').strip()
        owned = f"{ctx.lindas_base}/group-of-properties/{slug(g.get('Designation (EN)') or code or g.get('Beschreibung (DE)') or 'gop')}"
        payload = {
            'data': {
                'conceptType': 'String',
                'minLength': 0,
                'maxLength': 512,
                'name': ml(de=g.get('Beschreibung (DE)'), en=g.get('Designation (EN)'), fr=g.get('Description (FR)'), it=g.get('Descrizione (IT)')),
                'description': ml(de=g.get('Beschreibung (DE)'), en=g.get('Description (EN)'), fr=g.get('Description (FR)'), it=g.get('Descrizione (IT)')),
                'publisher': identifier_model(ctx.publisher),
                'responsiblePerson': email_model(first_nonempty(ctx.contact_email, 'placeholder@example.org')),
                'version': str(g.get('Version date') or ctx.version),
                'identifiers': [code, owned],
                'conformsTo': [x for x in [resource_model(owned, en='LINDAS authoritative GoP IRI'), resource_model(ctx.dataset_uri, en='I14Y dataset record')] if x],
            }
        }
        concepts.append(payload)
        semantic_index.append({
            'kind': 'groupOfProperties',
            'code': code,
            'ownedUri': owned,
            'sourceWorkbook': str(ctx.path),
            'i14yDatasetUri': ctx.dataset_uri,
        })
    for p in props:
        code = str(p.get('Property-Code') or '').strip()
        owned = first_nonempty(p.get('GUID/URI'), f"{ctx.lindas_base}/property/property/{slug(p.get('Designation (EN)') or p.get('Bezeichnung (DE)') or code)}")
        ctype, extra = infer_concept_type(p, by_prop_code)
        payload_data = {
            'conceptType': ctype,
            'name': ml(de=p.get('Bezeichnung (DE)'), en=p.get('Designation (EN)'), fr=p.get('Désignation (FR)'), it=p.get('Designazione (IT)')),
            'description': ml(de=p.get('Beschreibung (DE)'), en=p.get('Description (EN)'), fr=p.get('Description (FR)'), it=p.get('Descrizione (IT)')),
            'publisher': identifier_model(ctx.publisher),
            'responsiblePerson': email_model(first_nonempty(ctx.contact_email, 'placeholder@example.org')),
            'version': str(p.get('Version date') or ctx.version),
            'identifiers': [code, str(owned)],
            'conformsTo': [x for x in [
                resource_model(p.get('IFC_URI'), en='IFC 4.3 SSOT property pointer'),
                resource_model(p.get('QUDT URI'), en='QUDT unit SSOT pointer'),
                resource_model(owned, en='LINDAS authoritative property IRI'),
                resource_model(ctx.dataset_uri, en='I14Y dataset record')
            ] if x],
        }
        payload_data.update(extra)
        concepts.append({'data': payload_data})
        semantic_index.append({
            'kind': 'property',
            'code': code,
            'ownedUri': owned,
            'ifcUri': p.get('IFC_URI'),
            'ifcPropertySet': p.get('IfcPropertySet (Pset)\nIfcQuantitySet (Qto)'),
            'qudtUri': p.get('QUDT URI'),
            'unitNameEn': p.get('Unit Name (EN)'),
            'dataType': p.get('DataType\n(Base Type)'),
            'dataTypeIfc': p.get('DataType\n(IFC)'),
            'sourceWorkbook': str(ctx.path),
            'i14yDatasetUri': ctx.dataset_uri,
            'enumerationDesignation': p.get('EnumerationDesignation (EN)'),
        })
    semantic_relations = []
    for r in concept_relations:
        semantic_relations.append({
            'sourcePropertyCode': r.get('PropertyCode'),
            'relationType': r.get('RelationType'),
            'relatedPropertyUri': r.get('RelatedPropertyUri'),
            'notes': r.get('Notes'),
            'sourceWorkbook': str(ctx.path),
        })
    codelist_entries = []
    for pcode, vals in by_prop_code.items():
        if not vals:
            continue
        entries = []
        for v in vals:
            entries.append({
                'code': first_nonempty(v.get('Enumeration-Code'), slug(first_nonempty(v.get('Enumeration (EN)'), v.get('Bezeichnung (DE)'), 'value'))),
                'label': ml(de=v.get('Bezeichnung (DE)'), en=v.get('Enumeration (EN)'), fr=v.get('Désignation (FR)'), it=v.get('Designazione (IT)')),
                'ownedUri': v.get('GUID/URI'),
                'unit': v.get('Units/Einheit/Unité/Unità'),
            })
        codelist_entries.append({'propertyCode': pcode, 'entries': entries})
    return concepts, semantic_index, semantic_relations, codelist_entries


def extract_rows(ctx: WorkbookContext):
    wb = ctx.wb
    classes = rowdict(wb['Classes']) if 'Classes' in wb.sheetnames else []
    props = rowdict(wb['Properties']) if 'Properties' in wb.sheetnames else []
    gops = rowdict(wb['GroupOfProperties']) if 'GroupOfProperties' in wb.sheetnames else []
    values = rowdict(wb['Values']) if 'Values' in wb.sheetnames else []
    concept_relations = rowdict(wb['ConceptRelation'], header_row=2, data_start=5) if 'ConceptRelation' in wb.sheetnames else []
    return classes, props, gops, values, concept_relations


def build_bundle(workbooks: list[Path]):
    partner_spec = json.loads(PARTNER_SPEC.read_text()) if PARTNER_SPEC.exists() else None
    bundle = {
        'bundleVersion': '0.1.0',
        'generator': 'schemaforge/export_i14y_json.py',
        'partnerApiSpec': {
            'title': partner_spec['info']['title'],
            'version': partner_spec['info']['version'],
            'serverAbn': partner_spec['servers'][1]['url'] if partner_spec and len(partner_spec['servers']) > 1 else None,
            'serverProd': partner_spec['servers'][0]['url'] if partner_spec else None,
        } if partner_spec else None,
        'datasets': [],
        'concepts': [],
        'codeListEntries': [],
        'semantic': {'anchors': [], 'skosRelations': [], 'crossLinks': []}
    }
    for wb_path in workbooks:
        ctx = infer_context(wb_path)
        classes, props, gops, values, concept_relations = extract_rows(ctx)
        dataset_payload = build_dataset_payload(ctx)
        concepts, anchors, skos_relations, code_entries = build_concepts(ctx, classes, props, gops, values, concept_relations)
        bundle['datasets'].append({
            'sourceWorkbook': str(wb_path),
            'i14yRecordUri': ctx.dataset_uri,
            'lindasGraphUri': ctx.lindas_base,
            'partnerApi': dataset_payload,
            'counts': {
                'classes': len(classes),
                'properties': len(props),
                'groupOfProperties': len(gops),
                'values': len(values),
                'conceptRelations': len(concept_relations),
            },
        })
        bundle['concepts'].extend(concepts)
        bundle['codeListEntries'].extend(code_entries)
        bundle['semantic']['anchors'].extend(anchors)
        bundle['semantic']['skosRelations'].extend(skos_relations)
        bundle['semantic']['crossLinks'].append({
            'datasetUri': ctx.dataset_uri,
            'lindasGraphUri': ctx.lindas_base,
            'sourceWorkbook': str(wb_path),
            'note': 'I14Y record should reference LINDAS authoritative IRIs; LINDAS RDF should reference this I14Y dataset URI as provenance.'
        })
    return bundle


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    errs = []
    for ds in bundle.get('datasets', []):
        data = ds['partnerApi']['data']
        for req in ['accessRights', 'description', 'publisher', 'title']:
            if req not in data:
                errs.append(f'dataset missing required field: {req}')
    for concept in bundle.get('concepts', []):
        data = concept['data']
        for req in ['description', 'name', 'publisher', 'responsiblePerson', 'version']:
            if req not in data:
                errs.append(f'concept missing required field: {req}')
        for ct in data.get('conformsTo', []):
            if 'uri' in ct and ct['uri'] and not str(ct['uri']).startswith(('http://', 'https://')):
                errs.append(f'non-absolute URI in conformsTo: {ct["uri"]}')
    for a in bundle.get('semantic', {}).get('anchors', []):
        for k in ('ifcUri', 'qudtUri', 'ownedUri'):
            v = a.get(k)
            if v and not str(v).startswith(('http://', 'https://')):
                errs.append(f'anchor {k} is not absolute: {v}')
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('workbooks', nargs='*', default=[
        str(BASE_DIR / 'templates' / 'Strukturvorlage_DataDictionary_KBOB_FM.xlsx'),
        str(BASE_DIR / 'templates' / 'Strukturvorlage_DataDictionary_AreaMgmt.xlsx'),
    ])
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)
    bundle = build_bundle([Path(p) for p in args.workbooks])
    errs = validate_bundle(bundle)
    if errs:
        bundle['validationErrors'] = errs
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding='utf8')
    print(out)
    print('validation_ok' if not errs else f'validation_errors {len(errs)}')
    if errs:
        for e in errs[:20]:
            print('-', e)


if __name__ == '__main__':
    raise SystemExit(main())
