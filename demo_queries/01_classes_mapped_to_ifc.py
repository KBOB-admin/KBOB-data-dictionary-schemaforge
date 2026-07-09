#!/usr/bin/env python3
"""Show local classes that map to a given IFC class URI via skos:exactMatch.

Demo example:
    python3 01_classes_mapped_to_ifc.py
"""
from graphdb_query_utils import run_sparql, print_table

IFC_URI = 'https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcSpace'

QUERY = f'''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?class ?label ?comment
WHERE {{
  ?class a rdfs:Class ;
         skos:exactMatch <{IFC_URI}> ;
         rdfs:label ?label .
  OPTIONAL {{ ?class rdfs:comment ?comment }}
  FILTER(lang(?label) = 'en')
}}
ORDER BY ?label
'''

if __name__ == '__main__':
    result = run_sparql(QUERY)
    print_table(result)
