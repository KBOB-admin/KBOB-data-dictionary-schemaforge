#!/usr/bin/env python3
"""Prepare or publish the PoC RDF bundle to LINDAS INT.

Default mode is dry-run. Real publish requires a Stardog-compatible pylindas
config file and explicit --publish.
"""
from __future__ import annotations

import argparse
import configparser
import getpass
import os
from pathlib import Path

try:
    from pylindas import upload_ttl
except ModuleNotFoundError:
    upload_ttl = None

BASE = Path(__file__).resolve().parents[1]
DEFAULT_TTL = BASE / 'out' / 'combined.ttl'
DEFAULT_CONFIG = BASE / 'external' / 'lindas.ini'
DEFAULT_GRAPH = 'https://lindas.admin.ch/fobl/kbob/dd-fm'


def ensure_local_config(config: Path, environment: str, graph: str) -> Path:
    if config.exists():
        return config
    config.parent.mkdir(parents=True, exist_ok=True)
    username = os.environ.get('LINDAS_USERNAME') or input('LINDAS username/token: ').strip()
    password = os.environ.get('LINDAS_PASSWORD') or getpass.getpass('LINDAS password/token: ')
    endpoint = os.environ.get('LINDAS_ENDPOINT') or ('https://int.lindas.admin.ch' if environment.upper() == 'INT' else 'https://lindas.admin.ch')
    cp = configparser.RawConfigParser()
    cp[environment.upper()] = {
        'endpoint': endpoint,
        'username': username,
        'password': password,
        'graph': graph,
    }
    with config.open('w') as fh:
        cp.write(fh)
    print(f'Wrote local config to {config} (keep uncommitted).')
    return config


def read_config_graph(config: Path, environment: str) -> str | None:
    if not config.exists():
        return None
    cp = configparser.RawConfigParser()
    cp.read(config)
    section = environment.upper()
    if not cp.has_section(section) or not cp.has_option(section, 'graph'):
        return None
    value = cp.get(section, 'graph').strip()
    return value or None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--ttl', default=str(DEFAULT_TTL))
    ap.add_argument('--config', default=str(DEFAULT_CONFIG))
    ap.add_argument('--environment', default=os.environ.get('LINDAS_ENVIRONMENT', 'INT'))
    ap.add_argument('--graph')
    ap.add_argument('--clear-graph', action='store_true')
    ap.add_argument('--publish', action='store_true')
    args = ap.parse_args(argv)

    ttl = Path(args.ttl)
    config = Path(args.config)
    graph = args.graph or os.environ.get('LINDAS_GRAPH') or read_config_graph(config, args.environment) or DEFAULT_GRAPH
    if not ttl.exists():
        raise SystemExit(f'TTL file not found: {ttl}')

    print('TTL:', ttl)
    print('Environment:', args.environment)
    print('Graph:', graph)
    print('Config:', config)
    print('Clear graph:', args.clear_graph)

    if not args.publish:
        print('\nDRY RUN only. Real publication uses local-only credentials via env vars or a local lindas.ini.')
        print('Expected config sections: [INT] and/or [PROD] with Stardog connection details.')
        return 0

    if upload_ttl is None:
        raise SystemExit('pylindas is not installed. Install it locally before running --publish.')

    config = ensure_local_config(config, args.environment, graph)
    upload_ttl(str(ttl), str(config), args.environment, graph, clear_graph=args.clear_graph)
    print('Publish complete.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
