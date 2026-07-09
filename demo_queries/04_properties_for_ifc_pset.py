#!/usr/bin/env python3
"""Show properties aligned with a specific IFC property set."""
from graphdb_query_utils import run_sparql, print_table

IFC_PSET_URI = 'https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/Pset_SpaceCommon'

QUERY = f'''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dd:   <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?property ?label ?ifc_property
WHERE {{
  ?property dd:alignedWithIfcPset <{IFC_PSET_URI}> ;
            rdfs:label ?label .
  OPTIONAL {{ ?property skos:exactMatch ?ifc_property }}
  FILTER(lang(?label) = 'en')
}}
ORDER BY ?label
'''

if __name__ == '__main__':
    result = run_sparql(QUERY)
    print_table(result)
