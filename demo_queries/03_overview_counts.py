#!/usr/bin/env python3
"""Small overview query for a quick IDE demo."""
from graphdb_query_utils import run_sparql, print_table

QUERY = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?type (COUNT(?s) AS ?count)
WHERE {
  ?s a ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
LIMIT 20
'''

if __name__ == '__main__':
    result = run_sparql(QUERY)
    print_table(result)
