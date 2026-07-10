# LINDAS-INT-Zugriffsbeispiele für den PoC

Vom PoC verwendeter Graph-Namespace:

- `<https://lindas.admin.ch/fobl/kbob/dd-fm>`

## 1. pyLINDAS- / Python-Zugriff

Nach der Publikation ausführen:

```bash
python examples/pylindas_query_example.py
```

## 2. SPARQL-Abfrage (direkt)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dd: <https://lindas.admin.ch/fobl/kbob/dd-fm/vocab/>

SELECT ?prop ?label ?gop
WHERE {
  GRAPH <https://lindas.admin.ch/fobl/kbob/dd-fm> {
    ?prop a rdf:Property ;
          rdfs:label ?label ;
          dd:inGroupOfProperties ?gop .
    FILTER(lang(?label) = "en")
  }
}
LIMIT 50
```

## 3. Dritter Zugriffskanal: HTTP-Content-Negotiation / Dereferenzierung

Beispiel mit `curl` gegen eine konkrete Ressourcen-IRI nach der Publikation:

```bash
curl -L \
  -H 'Accept: text/turtle' \
  'https://lindas.admin.ch/fobl/kbob/dd-fm/class/class/room-(ai)'
```

Alternative Graph-Level-Abfrage über SPARQL-over-HTTP:

```bash
curl -G 'https://int.lindas.admin.ch/query' \
  --data-urlencode 'query=PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?s ?label WHERE { GRAPH <https://lindas.admin.ch/fobl/kbob/dd-fm> { ?s rdfs:label ?label FILTER(lang(?label)="en") } } LIMIT 10' \
  -H 'Accept: application/sparql-results+json'
```

## Empfohlene Demo-Abfragen

### Klassen im Dictionary

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class ?label
WHERE {
  GRAPH <https://lindas.admin.ch/fobl/kbob/dd-fm> {
    ?class a rdfs:Class ; rdfs:label ?label .
    FILTER(lang(?label) = "en")
  }
}
LIMIT 50
```

### Properties mit QUDT-Einheiten

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX qudt: <http://qudt.org/schema/qudt/>
SELECT ?prop ?label ?unit
WHERE {
  GRAPH <https://lindas.admin.ch/fobl/kbob/dd-fm> {
    ?prop a rdf:Property ; rdfs:label ?label ; qudt:hasUnit ?unit .
    FILTER(lang(?label) = "en")
  }
}
LIMIT 50
```

### Dictionary-übergreifende SKOS-Links

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?source ?rel ?target
WHERE {
  GRAPH <https://lindas.admin.ch/fobl/kbob/dd-fm> {
    ?source ?rel ?target .
    FILTER(?rel IN (skos:exactMatch, skos:closeMatch, skos:broadMatch, skos:narrowMatch, skos:relatedMatch))
  }
}
LIMIT 100
```
