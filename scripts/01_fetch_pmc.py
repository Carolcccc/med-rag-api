"""
Download article metadata from PubMed for a given query and fetch full text links when available.
This script uses Entrez (Biopython). It does NOT download PMC bulk; for that you should use FTP bulk.

Outputs: writes JSONL files to data/pmc_metadata.jsonl containing basic metadata and possible pmc_url.
"""
from pathlib import Path
import json
import os
import argparse
try:
    from Bio import Entrez
except Exception:
    Entrez = None

if Entrez is not None:
    Entrez.email = os.environ.get("ENTREZ_EMAIL", "you@example.com")

parser = argparse.ArgumentParser(description="Fetch PubMed IDs and metadata for a query")
parser.add_argument("--query", required=True)
parser.add_argument("--retmax", type=int, default=100)
parser.add_argument("--outdir", default="data/pmc")
args = parser.parse_args()

outdir = Path(args.outdir)
outdir.mkdir(parents=True, exist_ok=True)

if Entrez is None:
    raise RuntimeError("Biopython is not installed. Install with `pip install biopython` to use this script")

handle = Entrez.esearch(db="pubmed", term=args.query, retmax=args.retmax)
ids = Entrez.read(handle)["IdList"]
print(f"Found {len(ids)} PMIDs")

with open(outdir / "pmc_metadata.jsonl", "w", encoding="utf-8") as f:
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        records = Entrez.efetch(db="pubmed", id=','.join(batch), rettype="xml")
        docs = Entrez.read(records)
        for article in docs['PubmedArticle']:
            meta = {}
            try:
                meta['pmid'] = article['MedlineCitation']['PMID']
                meta['title'] = article['MedlineCitation']['Article']['ArticleTitle']
                meta['abstract'] = ' '.join([x for x in article['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', [])])
            except Exception:
                continue
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")

print('Done')
