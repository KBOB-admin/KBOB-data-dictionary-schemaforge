#!/usr/bin/env python3
"""Upload TTL to GraphDB repository (dry-run by default).

Usage:
  python3 scripts/upload_to_graphdb.py --ttl out/combined.ttl --repo termit --endpoint http://localhost:7200 --user YOUR --pass YOUR --publish

If --publish is omitted the script prints the REST calls it would make.
"""
import argparse, requests, os, sys
from pathlib import Path

def create_repo(endpoint, repo, user=None, password=None, dry_run=True):
    url = f"{endpoint.rstrip('/')}/rest/repositories"
    payload = f"<repository><id>{repo}</id><title>{repo}</title><options></options></repository>"
    print('CREATE REPO POST', url)
    if dry_run:
        return
    r = requests.post(url, data=payload, auth=(user,password) if user and password else None, headers={'Content-Type':'application/xml'})
    r.raise_for_status()
    return r.text


def upload_ttl(endpoint, repo, ttl_path: Path, user=None, password=None, dry_run=True):
    url = f"{endpoint.rstrip('/')}/repositories/{repo}/statements"
    print('PUT TTL to', url)
    if dry_run:
        print('DRY RUN: would PUT file of size', ttl_path.stat().st_size)
        return
    with ttl_path.open('rb') as f:
        r = requests.post(url, data=f, headers={'Content-Type':'text/turtle'}, auth=(user,password) if user and password else None)
    r.raise_for_status()
    return r.text


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--ttl', required=True)
    p.add_argument('--endpoint', default='http://localhost:7200')
    p.add_argument('--repo', default='termit')
    p.add_argument('--user')
    p.add_argument('--password')
    p.add_argument('--publish', action='store_true')
    args=p.parse_args(argv)

    ttl=Path(args.ttl)
    if not ttl.exists():
        print('TTL not found', ttl); return 2
    dry = not args.publish
    create_repo(args.endpoint, args.repo, args.user, args.password, dry_run=dry)
    upload_ttl(args.endpoint, args.repo, ttl, args.user, args.password, dry_run=dry)
    if dry:
        print('\nDry run complete. To publish, re-run with --publish and provide credentials if needed.')
    else:
        print('\nUpload complete.')

if __name__=='__main__':
    raise SystemExit(main())
