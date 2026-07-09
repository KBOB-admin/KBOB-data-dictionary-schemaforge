#!/usr/bin/env python3
import requests

DEFAULT_BASE = 'http://127.0.0.1:7200'
DEFAULT_REPO = 'LINDAS_PoC_2'


def run_sparql(query: str, base: str = DEFAULT_BASE, repo: str = DEFAULT_REPO) -> dict:
    endpoint = f"{base.rstrip('/')}/repositories/{repo}"
    response = requests.post(
        endpoint,
        data={'query': query},
        headers={'Accept': 'application/sparql-results+json'},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def print_table(result: dict):
    vars_ = result.get('head', {}).get('vars', [])
    rows = result.get('results', {}).get('bindings', [])
    if not vars_:
        print(result)
        return
    print(' | '.join(vars_))
    print('-' * (sum(len(v) for v in vars_) + 3 * max(len(vars_) - 1, 0)))
    for row in rows:
        values = []
        for v in vars_:
            cell = row.get(v, {})
            values.append(cell.get('value', ''))
        print(' | '.join(values))


def print_boolean(result: dict):
    print(result.get('boolean'))
