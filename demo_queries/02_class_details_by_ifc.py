#!/usr/bin/env python3
"""Show richer details for classes mapped to a specific IFC class URI.

This is useful for demoing how a client can ask high-level questions from an IDE.
"""
from graphdb_query_utils import run_sparql, print_table

IFC_URI = 'https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcSpace'

QUERY = f'''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?class ?label_de ?label_en ?definition_en ?source ?derived_from
WHERE {{
  ?class a rdfs:Class ;
         skos:exactMatch <{IFC_URI}> .
  OPTIONAL {{ ?class rdfs:label ?label_de . FILTER(lang(?label_de) = 'de') }}
  OPTIONAL {{ ?class rdfs:label ?label_en . FILTER(lang(?label_en) = 'en') }}
  OPTIONAL {{ ?class skos:definition ?definition_en . FILTER(lang(?definition_en) = 'en') }}
  OPTIONAL {{ ?class dct:source ?source }}
  OPTIONAL {{ ?class prov:wasDerivedFrom ?derived_from }}
}}
ORDER BY ?label_en
'''

if __name__ == '__main__':
    result = run_sparql(QUERY)
    print_table(result)
