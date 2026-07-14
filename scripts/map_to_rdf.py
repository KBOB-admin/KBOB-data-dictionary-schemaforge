#!/usr/bin/env python3
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, OWL, XSD
from openpyxl import load_workbook
from pathlib import Path
import argparse, ast, json, re

LINDAS_BASE = 'https://lindas.admin.ch/fobl/kbob/dd-fm'
BDCH = 'bdch'
IFC_CLASS_BASE = 'https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class'
QUDT = Namespace('http://qudt.org/schema/qudt/')
PROV = Namespace('http://www.w3.org/ns/prov#')
DD = Namespace('https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/')


def slug(s):
    s = str(s or '').strip().lower()
    repl = {' ':'-','ä':'ae','ö':'oe','ü':'ue','ß':'ss','/':'-','_':'-','(':'',')':''}
    for a,b in repl.items():
        s = s.replace(a,b)
    s = re.sub(r'[^a-z0-9\-]+','-',s)
    s = re.sub(r'-+','-',s).strip('-')
    return s or 'item'


def rowdict(ws, header_row=1, data_start=8):
    headers={str(ws.cell(header_row,c).value).strip():c for c in range(1,ws.max_column+1) if ws.cell(header_row,c).value}
    rows=[]

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

    for r in range(start, ws.max_row+1):
        rec={}
        anyv=False
        for h,c in headers.items():
            v=ws.cell(r,c).value
            if v not in (None,''):
                anyv=True
            rec[h]=v
        if anyv:
            rec['_row']=r
            rows.append(rec)
    return rows


def require_id(row, column, sheet_name):
    value = str(row.get(column) or '').strip()
    if not value:
        row_no = row.get('_row', '?')
        raise ValueError(f'{sheet_name} row {row_no} is missing required system identifier {column}')
    return value


def mint_from_id(base, subpath, identifier):
    identifier = str(identifier or '').strip()
    if not identifier:
        raise ValueError(f'Cannot mint {subpath} URI without an identifier')
    return URIRef(f"{base}/{subpath}/{slug(identifier)}")


def mint_value_uri(base, enum_id, position, lexical):
    return URIRef(f"{base}/enumerations/{slug(enum_id)}/values/{position:04d}-{slug(lexical)}")


def parse_value_list(value, sheet_name, row_no, column):
    if value in (None, ''):
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(f'{sheet_name} row {row_no} column {column} must contain a JSON-style list') from exc
    if not isinstance(parsed, list):
        raise ValueError(f'{sheet_name} row {row_no} column {column} must contain a list')
    return parsed


def lexical(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value).strip()


def typed_literal(value):
    if isinstance(value, bool):
        return Literal(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return Literal(value, datatype=XSD.integer)
    if isinstance(value, float):
        return Literal(value, datatype=XSD.decimal)
    return None


def add_pref_labels(g, uri, de=None, en=None, fr=None, it=None):
    labels = [('en', en), ('de', de), ('fr', fr), ('it', it)]
    for lang, value in labels:
        if value not in (None, ''):
            lit = Literal(lexical(value), lang=lang)
            g.add((uri, SKOS.prefLabel, lit))
            g.add((uri, RDFS.label, lit))


def build_enumerations(values_rows, sheet_name='Values'):
    schemes = []
    by_designation = {}
    by_id = {}
    diagnostics = []
    for row in values_rows:
        enum_id = require_id(row, 'Enumeration-ID', sheet_name)
        row_no = row.get('_row', '?')
        designation_en = str(row.get('Designation (EN)') or '').strip()
        if not designation_en:
            raise ValueError(f'{sheet_name} row {row_no} is missing required Designation (EN)')
        if enum_id in by_id:
            raise ValueError(f'{sheet_name} row {row_no} duplicates Enumeration-ID: {enum_id}')
        lists = {
            'en': parse_value_list(row.get('Enumeration (EN)'), sheet_name, row_no, 'Enumeration (EN)'),
            'de': parse_value_list(row.get('Werteliste\n(DE)'), sheet_name, row_no, 'Werteliste (DE)'),
            'fr': parse_value_list(row.get('Liste de valeurs\n(FR)'), sheet_name, row_no, 'Liste de valeurs (FR)'),
            'it': parse_value_list(row.get('Lista valori\n(IT)'), sheet_name, row_no, 'Lista valori (IT)'),
        }
        populated_lengths = {lang: len(items) for lang, items in lists.items() if items}
        if not populated_lengths:
            raise ValueError(f'{sheet_name} row {row_no} has no enumeration values')
        canonical_len = populated_lengths.get('en') or next(iter(populated_lengths.values()))
        for lang, length in populated_lengths.items():
            if length != canonical_len:
                raise ValueError(
                    f'{sheet_name} row {row_no} has misaligned value-list lengths: '
                    f'{", ".join(f"{k}={v}" for k, v in sorted(populated_lengths.items()))}'
                )
        values = []
        seen_value_uris = set()
        for index in range(canonical_len):
            labels = {lang: (items[index] if items else None) for lang, items in lists.items()}
            canonical = lexical(labels.get('en') or labels.get('de') or labels.get('fr') or labels.get('it') or index + 1)
            value_uri_key = f'{index + 1:04d}-{slug(canonical)}'
            if value_uri_key in seen_value_uris:
                raise ValueError(f'{sheet_name} row {row_no} produces a duplicate value URI token: {value_uri_key}')
            seen_value_uris.add(value_uri_key)
            values.append({'position': index + 1, 'canonical': canonical, 'labels': labels, 'raw': labels.get('en')})
        scheme = {
            'id': enum_id,
            'code': str(row.get('Enumeration-Code') or '').strip(),
            'designation_en': designation_en,
            'labels': {
                'en': row.get('Designation (EN)'),
                'de': row.get('Bezeichnung (DE)'),
                'fr': row.get('Désignation (FR)'),
                'it': row.get('Designazione (IT)'),
            },
            'values': values,
            'row': row,
        }
        by_id[enum_id] = scheme
        if designation_en in by_designation:
            raise ValueError(f'{sheet_name} row {row_no} duplicates Designation (EN): {designation_en}')
        by_designation[designation_en] = scheme
        diagnostics.append(f'{designation_en}: {len(values)} value(s), URI basis Enumeration-ID={enum_id}')
        schemes.append(scheme)
    return schemes, by_designation, diagnostics


def normalize_predefined_type(value):
    if value in (None, ''):
        return ''
    return str(value).strip().replace(' ', '').replace('-', '_').upper()


def ifc_base_class_uri(ifc_entity):
    entity = str(ifc_entity or '').strip()
    if not entity:
        return None
    if not entity.startswith('Ifc'):
        raise ValueError(f'IfcObject Entity must start with Ifc: {entity}')
    return URIRef(f'{IFC_CLASS_BASE}/{entity}')


def ifc_predefined_class_uri(ifc_entity, predefined_type):
    entity = str(ifc_entity or '').strip()
    predefined = normalize_predefined_type(predefined_type)
    if not entity or not predefined or predefined == 'USERDEFINED':
        return None
    if predefined.startswith('Ifc'):
        return URIRef(f'{IFC_CLASS_BASE}/{predefined}')
    return URIRef(f'{IFC_CLASS_BASE}/{entity}{predefined}')


def dataset_uri_for_workbook(path):
    return URIRef(f"https://i14y.admin.ch/catalog/{slug(Path(path).stem)}")


def workbook_resources(wb, wb_path, dict_prefix=''):
    classes = rowdict(wb['Classes']) if 'Classes' in wb.sheetnames else []
    props = rowdict(wb['Properties']) if 'Properties' in wb.sheetnames else []
    gops = rowdict(wb['GroupOfProperties']) if 'GroupOfProperties' in wb.sheetnames else []
    vals = rowdict(wb['Values']) if 'Values' in wb.sheetnames else []
    concept_rel = rowdict(wb['ConceptRelation'], header_row=2, data_start=5) if 'ConceptRelation' in wb.sheetnames else []
    dataset_uri = dataset_uri_for_workbook(wb_path)
    base = LINDAS_BASE if not dict_prefix else f"{LINDAS_BASE}/{dict_prefix}"
    return classes, props, gops, vals, concept_rel, dataset_uri, base


def add_labels(g, uri, de=None, en=None, fr=None, it=None):
    if en: g.add((uri, RDFS.label, Literal(str(en), lang='en')))
    if de: g.add((uri, RDFS.label, Literal(str(de), lang='de')))
    if fr: g.add((uri, RDFS.label, Literal(str(fr), lang='fr')))
    if it: g.add((uri, RDFS.label, Literal(str(it), lang='it')))


def add_resource_links(g, uri, dataset_uri, ifc_uri=None, qudt_uri=None, doc_uri=None):
    g.add((uri, DCTERMS.source, dataset_uri))
    g.add((uri, PROV.wasDerivedFrom, dataset_uri))
    if ifc_uri:
        g.add((uri, SKOS.exactMatch, URIRef(str(ifc_uri))))
    if qudt_uri:
        g.add((uri, QUDT.hasUnit, URIRef(str(qudt_uri))))
    if doc_uri:
        g.add((uri, RDFS.seeAlso, URIRef(str(doc_uri))))


def add_ifc_class_alignment(g, uri, row):
    base_ifc_uri = ifc_base_class_uri(row.get('IfcObject Entity'))
    predefined_ifc_uri = ifc_predefined_class_uri(row.get('IfcObject Entity'), row.get('PredefinedType'))
    if base_ifc_uri is None:
        if row.get('IFC_URI'):
            g.add((uri, SKOS.exactMatch, URIRef(str(row.get('IFC_URI')))))
        return
    g.add((uri, DD.ifcObjectEntity, base_ifc_uri))
    if predefined_ifc_uri is None:
        g.add((uri, SKOS.exactMatch, base_ifc_uri))
        return
    g.add((uri, SKOS.exactMatch, predefined_ifc_uri))
    g.add((uri, SKOS.broadMatch, base_ifc_uri))
    g.add((uri, DD.ifcPredefinedType, predefined_ifc_uri))


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('kbob')
    p.add_argument('areamgmt')
    p.add_argument('--out', default='out')
    args=p.parse_args(argv)

    kbob=load_workbook(args.kbob,data_only=True)
    area=load_workbook(args.areamgmt,data_only=True)
    outdir=Path(args.out)
    outdir.mkdir(parents=True,exist_ok=True)

    g=Graph()
    g.bind('rdfs', RDFS)
    g.bind('skos', SKOS)
    g.bind('dct', DCTERMS)
    g.bind('prov', PROV)
    g.bind('qudt', QUDT)
    g.bind('owl', OWL)
    g.bind('dd', DD)
    g.bind('lindas', Namespace(LINDAS_BASE+'/'))

    diagnostics = []
    # process both workbooks
    for wb, path, prefix in [(kbob, args.kbob, ''), (area, args.areamgmt, BDCH)]:
        classes, props, gops, vals, concept_rel, dataset_uri, base = workbook_resources(wb, path, prefix)
        enum_schemes, enum_by_designation, enum_diagnostics = build_enumerations(vals)
        diagnostics.extend([f'{Path(path).name}: {line}' for line in enum_diagnostics])
        # dataset provenance node
        g.add((dataset_uri, RDF.type, URIRef('http://www.w3.org/ns/dcat#Dataset')))
        g.add((dataset_uri, RDF.type, DD.DataDictionary))
        g.add((dataset_uri, RDFS.label, Literal(Path(path).stem, lang='en')))

        property_uri_by_code = {}
        class_uri_by_code = {}
        gop_uri_by_code = {}

        for c in classes:
            class_id = require_id(c, 'Class-ID', 'Classes')
            code = str(c.get('Class-Code') or '').strip()
            uri = mint_from_id(base, 'classes', class_id)
            class_uri_by_code[class_id] = uri
            if code:
                class_uri_by_code[code] = uri
            g.add((uri, RDF.type, RDFS.Class))
            g.add((dataset_uri, DD.hasClass, uri))
            add_labels(g, uri, c.get('Bezeichnung (DE)'), c.get('Designation (EN)'), c.get('Désignation (FR)'), c.get('Designazione (IT)'))
            if c.get('Beschreibung (DE)'):
                g.add((uri, SKOS.definition, Literal(str(c.get('Beschreibung (DE)')), lang='de')))
            if c.get('Description (EN)'):
                g.add((uri, SKOS.definition, Literal(str(c.get('Description (EN)')), lang='en')))
            add_resource_links(g, uri, dataset_uri)
            add_ifc_class_alignment(g, uri, c)
            # preserve IFC entity details as labels/comments
            if c.get('IfcObject Entity'):
                g.add((uri, RDFS.comment, Literal(f"IFC entity: {c.get('IfcObject Entity')}")))
            if c.get('PredefinedType'):
                g.add((uri, RDFS.comment, Literal(f"IFC predefined type: {c.get('PredefinedType')}")))

        for gop in gops:
            gop_id = require_id(gop, 'GoP-ID', 'GroupOfProperties')
            gcode = str(gop.get('GoP-Code') or '').strip()
            gop_uri = mint_from_id(base, 'group-of-properties', gop_id)
            gop_uri_by_code[gop_id] = gop_uri
            if gcode:
                gop_uri_by_code[gcode] = gop_uri
            g.add((gop_uri, RDF.type, DD.GroupOfProperties))
            g.add((dataset_uri, DD.hasGroupOfProperties, gop_uri))
            add_labels(g, gop_uri, gop.get('Beschreibung (DE)'), gop.get('Designation (EN)'), gop.get('Description (FR)'), gop.get('Descrizione (IT)'))
            add_resource_links(g, gop_uri, dataset_uri)

        value_uris_by_scheme_id = {}
        for scheme in enum_schemes:
            scheme_uri = mint_from_id(base, 'enumerations', scheme['id'])
            value_uris = []
            g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
            g.add((scheme_uri, RDF.type, DD.EnumerationScheme))
            g.add((dataset_uri, DD.hasEnumerationScheme, scheme_uri))
            add_pref_labels(
                g,
                scheme_uri,
                de=scheme['labels']['de'],
                en=scheme['labels']['en'],
                fr=scheme['labels']['fr'],
                it=scheme['labels']['it'],
            )
            if scheme['code']:
                g.add((scheme_uri, SKOS.notation, Literal(scheme['code'])))
            add_resource_links(g, scheme_uri, dataset_uri)
            for value in scheme['values']:
                val_uri = mint_value_uri(base, scheme['id'], value['position'], value['canonical'])
                value_uris.append(val_uri)
                g.add((val_uri, RDF.type, SKOS.Concept))
                g.add((val_uri, RDF.type, DD.EnumerationValue))
                g.add((val_uri, RDF.type, DD.AllowedValue))
                g.add((val_uri, SKOS.inScheme, scheme_uri))
                g.add((scheme_uri, DD.hasEnumerationValue, val_uri))
                g.add((val_uri, DD.enumerationPosition, Literal(value['position'], datatype=XSD.integer)))
                add_pref_labels(
                    g,
                    val_uri,
                    de=value['labels'].get('de'),
                    en=value['labels'].get('en'),
                    fr=value['labels'].get('fr'),
                    it=value['labels'].get('it'),
                )
                if value['canonical']:
                    g.add((val_uri, SKOS.notation, Literal(value['canonical'])))
                literal_value = typed_literal(value['raw'])
                if literal_value is not None:
                    g.add((val_uri, RDF.value, literal_value))
                add_resource_links(g, val_uri, dataset_uri)
            value_uris_by_scheme_id[scheme['id']] = value_uris

        for prop in props:
            prop_id = require_id(prop, 'Property-ID', 'Properties')
            code = str(prop.get('Property-Code') or '').strip()
            uri = mint_from_id(base, 'properties', prop_id)
            property_uri_by_code[prop_id] = uri
            if code:
                property_uri_by_code[code] = uri
            g.add((uri, RDF.type, RDF.Property))
            g.add((dataset_uri, DD.hasProperty, uri))
            add_labels(g, uri, prop.get('Bezeichnung (DE)'), prop.get('Designation (EN)'), prop.get('Désignation (FR)'), prop.get('Designazione (IT)'))
            if prop.get('Beschreibung (DE)'):
                g.add((uri, SKOS.definition, Literal(str(prop.get('Beschreibung (DE)')), lang='de')))
            if prop.get('Description (EN)'):
                g.add((uri, SKOS.definition, Literal(str(prop.get('Description (EN)')), lang='en')))
            add_resource_links(g, uri, dataset_uri, ifc_uri=prop.get('IFC_URI'), qudt_uri=prop.get('QUDT URI'))
            if prop.get('IfcPropertySet (Pset)\nIfcQuantitySet (Qto)'):
                pset_name = str(prop.get('IfcPropertySet (Pset)\nIfcQuantitySet (Qto)'))
                g.add((uri, RDFS.comment, Literal(f"IFC property set: {pset_name}")))
                if pset_name.startswith('http'):
                    pset_uri = URIRef(pset_name)
                    g.add((uri, DD.alignedWithIfcPset, pset_uri))
                else:
                    g.add((uri, DD.alignedWithIfcPset, Literal(pset_name)))
                for gcode, guri in gop_uri_by_code.items():
                    if gcode and (gcode == pset_name or slug(gcode) == slug(pset_name)):
                        g.add((uri, DD.inGroupOfProperties, guri))
                        g.add((guri, DD.groupContainsProperty, uri))
            if prop.get('DataType\n(Base Type)'):
                g.add((uri, RDFS.comment, Literal(f"Data type: {prop.get('DataType\n(Base Type)')}")))
            # preserve enumeration relation
            enum_designation = str(prop.get('EnumerationDesignation (EN)') or '').strip()
            if enum_designation:
                if enum_designation not in enum_by_designation:
                    diagnostics.append(
                        f'{Path(path).name}: WARNING Properties row {prop.get("_row", "?")} references unknown '
                        f'EnumerationDesignation (EN): {enum_designation}'
                    )
                    continue
                scheme = enum_by_designation[enum_designation]
                scheme_uri = mint_from_id(base, 'enumerations', scheme['id'])
                g.add((uri, DD.usesEnumerationScheme, scheme_uri))
                g.add((scheme_uri, DD.enumerationSchemeForProperty, uri))
                for val_uri in value_uris_by_scheme_id.get(scheme['id'], []):
                    g.add((uri, DD.hasAllowedValue, val_uri))
                    g.add((val_uri, DD.valueOfProperty, uri))
                    g.add((uri, SKOS.related, val_uri))

        # preserve concept relations exactly as declared
        for row in concept_rel:
            s_code = str(row.get('PropertyCode') or '').strip()
            rel = str(row.get('RelationType') or '').strip()
            target = str(row.get('RelatedPropertyUri') or '').strip()
            if not s_code or not rel or not target:
                continue
            if s_code not in property_uri_by_code and s_code not in class_uri_by_code:
                raise ValueError(f'ConceptRelation row {row.get("_row", "?")} references unknown source code/id: {s_code}')
            s_uri = property_uri_by_code.get(s_code) or class_uri_by_code.get(s_code)
            pred_local = rel.split(':')[-1]
            if hasattr(SKOS, pred_local):
                pred = getattr(SKOS, pred_local)
            else:
                pred = URIRef(rel)
            t_uri = URIRef(target) if target.startswith('http') else mint_from_id(base, 'properties', target)
            g.add((s_uri, pred, t_uri))
            if row.get('Notes'):
                g.add((s_uri, RDFS.comment, Literal(str(row.get('Notes')))))

    out_ttl=outdir/'combined.ttl'
    g.serialize(destination=str(out_ttl), format='turtle')
    diagnostics_file = outdir/'mapper-diagnostics.md'
    diagnostics_file.write_text(
        '# Mapper Diagnostics\n\n'
        '## Enumeration publication\n\n'
        + ('\n'.join(f'- {line}' for line in diagnostics) if diagnostics else '- No enumeration schemes found.')
        + '\n',
        encoding='utf-8',
    )
    print('wrote', out_ttl)
    print('wrote', diagnostics_file)

if __name__=='__main__':
    import sys
    main(sys.argv[1:])
