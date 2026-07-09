#!/usr/bin/env python3
"""Simple editable template for ad hoc demo questions in an IDE."""
from graphdb_query_utils import run_sparql, print_table, print_boolean

QUERY = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?class ?label
WHERE {
  ?class a rdfs:Class ;
         skos:exactMatch <https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcSpace> ;
         rdfs:label ?label .
  FILTER(lang(?label) = 'en')
}
ORDER BY ?label
LIMIT 25
'''

if __name__ == '__main__':
    result = run_sparql(QUERY)
    if 'boolean' in result:
        print_boolean(result)
    else:
        print_table(result)
