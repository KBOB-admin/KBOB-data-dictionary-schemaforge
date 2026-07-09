#!/usr/bin/env python3
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, OWL
from openpyxl import load_workbook
from pathlib import Path
import argparse, re

LINDAS_BASE = 'https://lindas.admin.ch/fobl/kbob/dd-fm'
BDCH = 'bdch'
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


def mint_or_owned(base, subpath, owned_uri, label_or_code):
    if owned_uri:
        return URIRef(str(owned_uri))
    return URIRef(f"{base}/{subpath}/{slug(label_or_code)}")


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

    # process both workbooks
    for wb, path, prefix in [(kbob, args.kbob, ''), (area, args.areamgmt, BDCH)]:
        classes, props, gops, vals, concept_rel, dataset_uri, base = workbook_resources(wb, path, prefix)
        # dataset provenance node
        g.add((dataset_uri, RDF.type, URIRef('http://www.w3.org/ns/dcat#Dataset')))
        g.add((dataset_uri, RDF.type, DD.DataDictionary))
        g.add((dataset_uri, RDFS.label, Literal(Path(path).stem, lang='en')))

        property_uri_by_code = {}
        class_uri_by_code = {}
        gop_uri_by_code = {}

        for c in classes:
            code = c.get('Class-Code') or c.get('Designation (EN)') or c.get('Bezeichnung (DE)')
            uri = mint_or_owned(base, 'class', c.get('GUID/URI'), code)
            class_uri_by_code[str(c.get('Class-Code') or code)] = uri
            g.add((uri, RDF.type, RDFS.Class))
            g.add((dataset_uri, DD.hasClass, uri))
            add_labels(g, uri, c.get('Bezeichnung (DE)'), c.get('Designation (EN)'), c.get('Désignation (FR)'), c.get('Designazione (IT)'))
            if c.get('Beschreibung (DE)'):
                g.add((uri, SKOS.definition, Literal(str(c.get('Beschreibung (DE)')), lang='de')))
            if c.get('Description (EN)'):
                g.add((uri, SKOS.definition, Literal(str(c.get('Description (EN)')), lang='en')))
            add_resource_links(g, uri, dataset_uri, ifc_uri=c.get('IFC_URI'))
            # preserve IFC entity details as labels/comments
            if c.get('IfcObject Entity'):
                g.add((uri, RDFS.comment, Literal(f"IFC entity: {c.get('IfcObject Entity')}")))
            if c.get('PredefinedType'):
                g.add((uri, RDFS.comment, Literal(f"IFC predefined type: {c.get('PredefinedType')}")))

        for gop in gops:
            gcode = str(gop.get('GoP-Code') or gop.get('GoP-ID') or '').strip()
            gop_uri = mint_or_owned(base, 'group-of-properties', None, gop.get('Designation (EN)') or gcode or gop.get('Beschreibung (DE)'))
            gop_uri_by_code[gcode] = gop_uri
            g.add((gop_uri, RDF.type, DD.GroupOfProperties))
            g.add((dataset_uri, DD.hasGroupOfProperties, gop_uri))
            add_labels(g, gop_uri, gop.get('Beschreibung (DE)'), gop.get('Designation (EN)'), gop.get('Description (FR)'), gop.get('Descrizione (IT)'))
            add_resource_links(g, gop_uri, dataset_uri)

        # map enum designation to values
        values_by_designation = {}
        for v in vals:
            designation = str(v.get('Werteliste\n(DE)') or v.get('Enumeration (EN)') or '').strip()
            values_by_designation.setdefault(designation, []).append(v)

        for prop in props:
            code = str(prop.get('Property-Code') or '').strip()
            uri = mint_or_owned(base, 'property', prop.get('GUID/URI'), prop.get('Designation (EN)') or prop.get('Bezeichnung (DE)') or code)
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
                    g.add((pset_uri, RDF.type, DD.GroupOfProperties))
                    g.add((dataset_uri, DD.hasGroupOfProperties, pset_uri))
                    g.add((uri, DD.alignedWithIfcPset, pset_uri))
                    g.add((uri, DD.inGroupOfProperties, pset_uri))
                    g.add((pset_uri, DD.groupContainsProperty, uri))
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
            if enum_designation and enum_designation in values_by_designation:
                for vv in values_by_designation[enum_designation]:
                    val_uri = mint_or_owned(base, 'value', vv.get('GUID/URI'), vv.get('Enumeration-Code') or vv.get('Enumeration (EN)') or vv.get('Bezeichnung (DE)'))
                    g.add((val_uri, RDF.type, SKOS.Concept))
                    g.add((val_uri, RDF.type, DD.AllowedValue))
                    add_labels(g, val_uri, vv.get('Bezeichnung (DE)'), vv.get('Enumeration (EN)'), vv.get('Désignation (FR)'), vv.get('Designazione (IT)'))
                    g.add((uri, DD.hasAllowedValue, val_uri))
                    g.add((val_uri, DD.valueOfProperty, uri))
                    g.add((uri, SKOS.related, val_uri))
                    g.add((val_uri, DCTERMS.source, dataset_uri))
                    if vv.get('GUID/URI') and 'ifc' in str(vv.get('GUID/URI')).lower():
                        g.add((val_uri, DD.alignedWithIfcPredefinedType, URIRef(str(vv.get('GUID/URI')))))

        # preserve concept relations exactly as declared
        for row in concept_rel:
            s_code = str(row.get('PropertyCode') or '').strip()
            rel = str(row.get('RelationType') or '').strip()
            target = str(row.get('RelatedPropertyUri') or '').strip()
            if not s_code or not rel or not target:
                continue
            s_uri = property_uri_by_code.get(s_code) or class_uri_by_code.get(s_code) or mint_or_owned(base, 'property', None, s_code)
            pred_local = rel.split(':')[-1]
            if hasattr(SKOS, pred_local):
                pred = getattr(SKOS, pred_local)
            else:
                pred = URIRef(rel)
            t_uri = URIRef(target) if target.startswith('http') else mint_or_owned(base, 'property', None, target)
            g.add((s_uri, pred, t_uri))
            if row.get('Notes'):
                g.add((s_uri, RDFS.comment, Literal(str(row.get('Notes')))))

    out_ttl=outdir/'combined.ttl'
    g.serialize(destination=str(out_ttl), format='turtle')
    print('wrote', out_ttl)

if __name__=='__main__':
    import sys
    main(sys.argv[1:])
