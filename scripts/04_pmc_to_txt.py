"""
Convert PMC metadata JSONL produced by `scripts/01_fetch_pmc.py` into
plain text files suitable for ingestion by `create_vector_db.py`.

Basic actions:
 - Read `data/pmc/pmc_metadata.jsonl`
 - For each record, extract title/abstract (or body) and write a UTF-8 .txt file
 - Do simple de-identification (mask phone numbers and emails)
 - Write files to `data/pmc_txt/{pmid}.txt`

Usage:
    python scripts/04_pmc_to_txt.py

"""
import json
import re
from pathlib import Path

INPATH = Path("data/pmc/pmc_metadata.jsonl")
OUTDIR = Path("data/pmc_txt")

phone_re = re.compile(r'(?:\+?\d{1,3}[-\.\s]?)?(?:\(?\d{2,4}\)?[-\.\s]?){1,4}\d{3,4}')
email_re = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')


def clean_text(s: str) -> str:
    if not s:
        return ""
    # Normalize whitespace
    text = s.replace('\r', '\n')
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    # De-identify simple patterns
    text = phone_re.sub('[PHONE]', text)
    text = email_re.sub('[EMAIL]', text)
    return text.strip()


def main():
    if not INPATH.exists():
        print(f"Input file not found: {INPATH}. Run scripts/01_fetch_pmc.py first.")
        return
    OUTDIR.mkdir(parents=True, exist_ok=True)

    count = 0
    with INPATH.open('r', encoding='utf-8') as fh:
        for line in fh:
            obj = json.loads(line)
            pmid = obj.get('pmid') or obj.get('id') or obj.get('pmcid') or f'record_{count}'
            title = obj.get('title') or ''
            abstract = obj.get('abstract') or ''
            body = obj.get('body') or ''
            # Prefer title + abstract, fallback to body
            content = '\n\n'.join([p for p in (title, abstract, body) if p])
            if not content:
                # Try serializing the whole record
                content = json.dumps(obj, ensure_ascii=False)

            clean = clean_text(content)
            out_path = OUTDIR / f"{pmid}.txt"
            with out_path.open('w', encoding='utf-8') as outfh:
                outfh.write(clean)
            count += 1

    print(f"Wrote {count} text files to {OUTDIR}/")


if __name__ == '__main__':
    main()
