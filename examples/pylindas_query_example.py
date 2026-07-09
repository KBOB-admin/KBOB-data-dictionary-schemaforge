#!/usr/bin/env python3
"""Example pyLINDAS query for the published PoC graph on INT.

This uses a raw SPARQLWrapper query because pylindas.query_lindas() only returns
ASK booleans in the installed version.
"""
from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT = 'https://int.lindas.admin.ch/query'
GRAPH = 'https://lindas.admin.ch/fobl/kbob/dd-fm'

QUERY = f'''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?s ?label
WHERE {{
  GRAPH <{GRAPH}> {{
    ?s rdfs:label ?label .
    FILTER(lang(?label) = "en")
  }}
}}
LIMIT 25
'''

sparql = SPARQLWrapper(ENDPOINT)
sparql.setQuery(QUERY)
sparql.setReturnFormat(JSON)
res = sparql.query().convert()
for b in res['results']['bindings']:
    print(b['s']['value'], '->', b['label']['value'])
