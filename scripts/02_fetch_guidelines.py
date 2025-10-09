"""
Fetch PDFs from WHO/CDC or specified guideline URLs and extract text to data/guidelines/*.txt
This script requires `requests` and `pdfplumber`.
"""
from pathlib import Path
import requests
import argparse
import pdfplumber

parser = argparse.ArgumentParser(description="Download guideline PDFs and extract text")
parser.add_argument("--urls", nargs='+', required=True, help="List of PDF URLs")
parser.add_argument("--outdir", default="data/guidelines")
args = parser.parse_args()

outdir = Path(args.outdir)
outdir.mkdir(parents=True, exist_ok=True)

for url in args.urls:
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Failed to download {url}: {r.status_code}")
        continue
    fname = url.split('/')[-1]
    p = outdir / fname
    p.write_bytes(r.content)
    # extract text
    try:
        text = []
        with pdfplumber.open(p) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or '')
        txt = '\n'.join(text)
        (outdir / (fname + '.txt')).write_text(txt, encoding='utf-8')
        print(f"Extracted {fname}")
    except Exception as e:
        print("PDF parse failed:", e)
