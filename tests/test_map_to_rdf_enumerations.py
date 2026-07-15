import tempfile
import unittest
from pathlib import Path
import shutil
import sys

from openpyxl import load_workbook
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, OWL

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import map_to_rdf  # noqa: E402


DD = Namespace('https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/')
BASE = 'https://lindas.admin.ch/fobl/kbob/dd-fm/bdch'


class EnumerationMappingTests(unittest.TestCase):
    def export_actual_workbooks(self):
        tmp = tempfile.TemporaryDirectory()
        out = Path(tmp.name)
        map_to_rdf.main([
            str(ROOT / 'templates' / 'Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx'),
            str(ROOT / 'templates' / 'Strukturvorlage_AreaMgmt_v0.5.0.xlsx'),
            '--out',
            str(out),
        ])
        graph = Graph()
        graph.parse(out / 'combined.ttl')
        return tmp, graph

    def test_actual_workbooks_publish_schemes_and_values(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        scheme = URIRef(f'{BASE}/enumerations/area-type-sia-416-code-enum')
        value = URIRef(f'{BASE}/enumerations/area-type-sia-416-code-enum/values/0001-1-2')
        prop = URIRef(f'{BASE}/properties/sia-416-2003')

        self.assertIn((scheme, RDF.type, SKOS.ConceptScheme), graph)
        self.assertIn((scheme, RDF.type, DD.EnumerationScheme), graph)
        self.assertIn((value, RDF.type, DD.EnumerationValue), graph)
        self.assertIn((value, SKOS.inScheme, scheme), graph)
        self.assertIn((prop, DD.usesEnumerationScheme, scheme), graph)
        self.assertIn((prop, DD.hasAllowedValue, value), graph)
        self.assertIn((scheme, DD.status, Literal('Preview')), graph)
        self.assertNotIn((value, DD.status, Literal('Preview')), graph)
        self.assertEqual(len(list(graph.triples((None, SKOS.member, None)))), 0)

    def test_actual_workbooks_publish_data_templates_requirements_groups_and_documents(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        template = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/data-templates/0005-site-kbob-grundstuck-architekt')
        class_uri = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/classes/site')
        group_uri = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/group-of-properties/kbob-grundstuck-architekt')
        document_uri = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/documents/kbob-dk-fm-i14y-csv')
        req_guid = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/property-requirements/0005-site-kbob-grundstuck-architekt/guid')
        req_site_id = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/property-requirements/0005-site-kbob-grundstuck-architekt/site-id')

        self.assertIn((template, RDF.type, DD.DataTemplate), graph)
        self.assertIn((template, DD.appliesToClass, class_uri), graph)
        self.assertIn((template, DD.includesGroupOfProperties, group_uri), graph)
        self.assertIn((template, DD.referencesDocument, document_uri), graph)
        self.assertIn((document_uri, RDF.type, DD.Document), graph)
        self.assertIn((template, DD.hasPropertyRequirement, req_guid), graph)
        self.assertIn((req_guid, RDF.type, DD.PropertyRequirement), graph)
        self.assertNotIn((template, DD.hasPropertyRequirement, req_site_id), graph)

    def test_dataset_uses_header_dictionary_name_and_source_workbook(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        dataset = URIRef('https://i14y.admin.ch/catalog/strukturvorlage-datadictionary-kbob-fm-v0-9-5')
        self.assertIn((dataset, RDFS.label, None), graph)
        self.assertIn((dataset, RDFS.label, Literal('KBOB FM Data Dictionary', lang='en')), graph)
        self.assertIn((dataset, DCTERMS.identifier, Literal('kbob_fm_data_dictionary')), graph)
        self.assertIn((dataset, OWL.versionInfo, Literal('0.3.0')), graph)
        self.assertIn((dataset, DD.sourceWorkbook, Literal('Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx')), graph)

    def test_property_datatype_ifc_datatype_and_status_are_published(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        prop = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/properties/airconditioning')
        self.assertIn((prop, DD.datatype, Literal('BOOLEAN')), graph)
        self.assertIn((prop, DD.ifcDatatype, None), graph)
        self.assertIn((prop, DD.status, None), graph)

    def test_x_requirement_retains_property_level_enumeration(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        requirement = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/property-requirements/0009-room-ifma-areamgmt/sia-2024-2021')
        scheme = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/room-usage-sia-2024-code-enum')
        self.assertIn((requirement, RDF.type, DD.PropertyRequirement), graph)
        self.assertIn((requirement, DD.usesEnumerationScheme, scheme), graph)
        self.assertIn((requirement, DD.usesCompleteValueScheme, None), graph)
        self.assertEqual(len(list(graph.objects(requirement, DD.allowedValue))), 0)

    def test_override_requirement_links_selected_existing_values(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        requirement = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/property-requirements/0007-surrounding-area-ifma-areamgmt/sia-416-2003')
        scheme = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/area-type-sia-416-code-enum')
        value = URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/enumerations/area-type-sia-416-code-enum/values/0001-1-2')
        self.assertIn((requirement, DD.usesEnumerationScheme, scheme), graph)
        self.assertIn((requirement, DD.allowedValue, value), graph)
        self.assertIn((value, RDF.type, DD.EnumerationValue), graph)

    def test_invalid_override_outside_linked_enumeration_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bad_area = tmp / 'bad-area.xlsx'
            shutil.copyfile(ROOT / 'templates' / 'Strukturvorlage_AreaMgmt_v0.5.0.xlsx', bad_area)
            wb = load_workbook(bad_area)
            ws = wb['Data_Template']
            ws.cell(7, 8).value = '["NOT_A_VALUE"]'
            wb.save(bad_area)
            with self.assertRaisesRegex(ValueError, 'unresolved override value: NOT_A_VALUE'):
                map_to_rdf.main([
                    str(ROOT / 'templates' / 'Strukturvorlage_DataDictionary_KBOB_FM_v0.9.5.xlsx'),
                    str(bad_area),
                    '--out',
                    str(tmp / 'out'),
                ])

    def test_requirement_uris_are_deterministic_and_unique(self):
        tmp, graph = self.export_actual_workbooks()
        self.addCleanup(tmp.cleanup)

        requirements = list(graph.subjects(RDF.type, DD.PropertyRequirement))
        self.assertEqual(len(requirements), len(set(requirements)))
        self.assertIn(
            URIRef('https://lindas.admin.ch/fobl/kbob/dd-fm/bdch/property-requirements/0009-room-ifma-areamgmt/sia-416-2003'),
            set(requirements),
        )

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
