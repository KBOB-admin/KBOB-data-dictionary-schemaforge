#!/usr/bin/env python3
"""Prepare or publish the PoC RDF bundle to LINDAS INT.

Default mode is dry-run. Real publish requires a Stardog-compatible pylindas
config file and explicit --publish.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from pylindas import upload_ttl

BASE = Path(__file__).resolve().parents[1]
DEFAULT_TTL = BASE / 'out' / 'combined.ttl'
DEFAULT_CONFIG = BASE / 'external' / 'lindas.ini'
DEFAULT_GRAPH = 'https://lindas.admin.ch/fobl/kbob/dd-fm'


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--ttl', default=str(DEFAULT_TTL))
    ap.add_argument('--config', default=str(DEFAULT_CONFIG))
    ap.add_argument('--environment', default=os.environ.get('LINDAS_ENVIRONMENT', 'INT'))
    ap.add_argument('--graph', default=os.environ.get('LINDAS_GRAPH', DEFAULT_GRAPH))
    ap.add_argument('--clear-graph', action='store_true')
    ap.add_argument('--publish', action='store_true')
    args = ap.parse_args(argv)

    ttl = Path(args.ttl)
    config = Path(args.config)
    if not ttl.exists():
        raise SystemExit(f'TTL file not found: {ttl}')

    print('TTL:', ttl)
    print('Environment:', args.environment)
    print('Graph:', args.graph)
    print('Config:', config)
    print('Clear graph:', args.clear_graph)

    if not args.publish:
        print('\nDRY RUN only. To publish tomorrow, provide a valid lindas.ini and run with --publish.')
        print('Expected config sections: [INT] and/or [PROD] with Stardog connection details.')
        return 0

    if not config.exists():
        raise SystemExit(f'Config file not found: {config}')

    upload_ttl(str(ttl), str(config), args.environment, args.graph, clear_graph=args.clear_graph)
    print('Publish complete.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
