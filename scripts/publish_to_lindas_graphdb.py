#!/usr/bin/env python3
"""Publish a Turtle file to LINDASNext / GraphDB.

Default mode is a dry-run. Real upload requires --publish and local credentials
from external/lindas.ini or environment variables.
"""
from __future__ import annotations

import argparse
import configparser
import os
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE = Path(__file__).resolve().parents[1]
DEFAULT_TTL = BASE / 'out' / 'combined.ttl'
DEFAULT_CONFIG = BASE / 'external' / 'lindas.ini'
DEFAULT_GRAPH = 'https://lindas.admin.ch/fobl/kbob/dd-fm'
DEFAULT_INT_GSP_ENDPOINT = 'https://int.graphdb.lindas.admin.ch/repositories/lindas/rdf-graphs/service'


def config_value(config: Path, environment: str, key: str) -> str | None:
    if not config.exists():
        return None
    cp = configparser.RawConfigParser()
    cp.read(config)
    section = environment.upper()
    if not cp.has_section(section) or not cp.has_option(section, key):
        return None
    value = cp.get(section, key).strip()
    return value or None


def resolve_setting(
    explicit: str | None,
    env_key: str,
    config: Path,
    environment: str,
    config_key: str,
    fallback: str | None = None,
) -> str | None:
    return explicit or os.environ.get(env_key) or config_value(config, environment, config_key) or fallback


def require_absolute_url(label: str, value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        raise SystemExit(f'{label} must be an absolute HTTP(S) URL: {value}')


def publish_graph(
    ttl: Path,
    endpoint: str,
    graph: str,
    username: str,
    password: str,
    operation: str,
    timeout: int,
) -> requests.Response:
    auth = (username, password)
    params = {'graph': graph}
    headers = {'Content-Type': 'text/turtle'}
    if operation == 'delete':
        return requests.delete(endpoint, params=params, auth=auth, timeout=timeout)
    with ttl.open('rb') as fh:
        if operation == 'replace':
            return requests.put(endpoint, params=params, data=fh, headers=headers, auth=auth, timeout=timeout)
        return requests.post(endpoint, params=params, data=fh, headers=headers, auth=auth, timeout=timeout)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--ttl', default=str(DEFAULT_TTL))
    ap.add_argument('--config', default=str(DEFAULT_CONFIG))
    ap.add_argument('--environment', default=os.environ.get('LINDAS_ENVIRONMENT', 'INT'))
    ap.add_argument('--gsp-endpoint')
    ap.add_argument('--graph')
    ap.add_argument('--username')
    ap.add_argument('--password')
    ap.add_argument('--operation', choices=('append', 'replace', 'delete'), default='append')
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--publish', action='store_true')
    args = ap.parse_args(argv)

    ttl = Path(args.ttl)
    config = Path(args.config)
    environment = args.environment.upper()
    endpoint_fallback = DEFAULT_INT_GSP_ENDPOINT if environment == 'INT' else None
    endpoint = resolve_setting(args.gsp_endpoint, 'LINDAS_GSP_ENDPOINT', config, environment, 'gsp_endpoint', endpoint_fallback)
    graph = resolve_setting(args.graph, 'LINDAS_GRAPH', config, environment, 'graph', DEFAULT_GRAPH)
    username = resolve_setting(args.username, 'LINDAS_USERNAME', config, environment, 'username')
    password = resolve_setting(args.password, 'LINDAS_PASSWORD', config, environment, 'password')

    if args.operation != 'delete' and not ttl.exists():
        raise SystemExit(f'TTL file not found: {ttl}')
    if not endpoint:
        raise SystemExit('Graph Store Protocol endpoint missing. Set gsp_endpoint in lindas.ini or LINDAS_GSP_ENDPOINT.')
    if not graph:
        raise SystemExit('Named graph missing. Set graph in lindas.ini or LINDAS_GRAPH.')
    require_absolute_url('Graph Store Protocol endpoint', endpoint)
    require_absolute_url('Named graph', graph)
    if args.publish and (not username or not password):
        raise SystemExit('Username/password missing for publish. Set them in lindas.ini or environment variables.')

    print('TTL:', ttl)
    print('Environment:', environment)
    print('Graph Store Protocol endpoint:', endpoint)
    print('Graph:', graph)
    print('Operation:', args.operation)
    print('Config:', config)
    print('Auth configured:', bool(username and password))
    if args.operation != 'delete':
        print('TTL bytes:', ttl.stat().st_size)

    if not args.publish:
        print('\nDRY RUN only. Real publication requires --publish.')
        if args.operation == 'append':
            print('Would POST Turtle to the named graph.')
        elif args.operation == 'replace':
            print('Would PUT Turtle and replace the named graph.')
        else:
            print('Would DELETE the named graph.')
        return 0

    response = publish_graph(ttl, endpoint, graph, username, password, args.operation, args.timeout)
    if response.status_code not in {200, 201, 202, 204}:
        print('Publish failed.')
        print('HTTP status:', response.status_code)
        print('Response:', response.text[:1000])
        response.raise_for_status()

    print('Publish complete.')
    print('HTTP status:', response.status_code)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
