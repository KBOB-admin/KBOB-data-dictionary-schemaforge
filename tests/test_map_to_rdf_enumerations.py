import tempfile
import unittest
from pathlib import Path
import sys

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import map_to_rdf  # noqa: E402


DD = Namespace('https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/')
BASE = 'https://lindas.admin.ch/fobl/kbob/dd-fm/bdch'


class EnumerationMappingTests(unittest.TestCase):
    def test_actual_workbooks_publish_schemes_and_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            map_to_rdf.main([
                str(ROOT / 'templates' / 'Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx'),
                str(ROOT / 'templates' / 'Strukturvorlage_AreaMgmt_v0.5.0.xlsx'),
                '--out',
                str(out),
            ])
            graph = Graph()
            graph.parse(out / 'combined.ttl')

        scheme = URIRef(f'{BASE}/enumerations/area-type-sia-416-code-enum')
        value = URIRef(f'{BASE}/enumerations/area-type-sia-416-code-enum/values/0001-1-2')
        prop = URIRef(f'{BASE}/properties/sia-416-2003')

        self.assertIn((scheme, RDF.type, SKOS.ConceptScheme), graph)
        self.assertIn((scheme, RDF.type, DD.EnumerationScheme), graph)
        self.assertIn((value, RDF.type, DD.EnumerationValue), graph)
        self.assertIn((value, SKOS.inScheme, scheme), graph)
        self.assertIn((prop, DD.usesEnumerationScheme, scheme), graph)
        self.assertIn((prop, DD.hasAllowedValue, value), graph)
        self.assertEqual(len(list(graph.triples((None, SKOS.member, None)))), 0)

    def test_duplicate_lexical_values_are_distinguished_by_position(self):
        rows = [{
            'Enumeration-ID': 'room_designation_enum',
            'Enumeration-Code': 'ROOM',
            'Designation (EN)': 'Room designation',
            'Bezeichnung (DE)': 'Raumbezeichnung',
            'Enumeration (EN)': '["1", "2", "1"]',
            'Werteliste\n(DE)': '["HNF1", "HNF2", "NNF7"]',
            '_row': 7,
        }]
        schemes, by_designation, diagnostics = map_to_rdf.build_enumerations(rows)
        self.assertEqual(len(schemes[0]['values']), 3)
        self.assertIn('Room designation', by_designation)
        self.assertEqual(len(diagnostics), 1)

        uris = [
            map_to_rdf.mint_value_uri(BASE, schemes[0]['id'], value['position'], value['canonical'])
            for value in schemes[0]['values']
        ]
        self.assertEqual(len(set(uris)), 3)
        self.assertTrue(str(uris[0]).endswith('/values/0001-1'))
        self.assertTrue(str(uris[2]).endswith('/values/0003-1'))

    def test_misaligned_multilingual_value_lists_fail_fast(self):
        rows = [{
            'Enumeration-ID': 'bad_enum',
            'Designation (EN)': 'Bad enum',
            'Enumeration (EN)': '["A", "B"]',
            'Werteliste\n(DE)': '["A"]',
            '_row': 12,
        }]
        with self.assertRaisesRegex(ValueError, 'misaligned value-list lengths'):
            map_to_rdf.build_enumerations(rows)


if __name__ == '__main__':
    unittest.main()
