"""
Fetch Reddit posts using PRAW (requires credentials). Save to data/reddit/*.jsonl
Per-post basic de-identification with regex replacements (not a substitute for robust de-id)
"""
import os
import re
import json
from pathlib import Path
import argparse

try:
    import praw
except Exception:
    praw = None

parser = argparse.ArgumentParser(description="Fetch reddit posts from given subreddit")
parser.add_argument("--subreddit", required=True)
parser.add_argument("--limit", type=int, default=200)
parser.add_argument("--outdir", default="data/reddit")
args = parser.parse_args()

outdir = Path(args.outdir)
outdir.mkdir(parents=True, exist_ok=True)

if praw is None:
    raise RuntimeError("praw not installed. Install with `pip install praw`")

reddit = praw.Reddit(client_id=os.environ.get('REDDIT_CLIENT_ID'),
                     client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                     user_agent=os.environ.get('REDDIT_USER_AGENT','healthcare-scraper'))

phone_re = re.compile(r'(?:\+?\d{1,3}[-\.\s]?)?(?:\(?\d{2,4}\)?[-\.\s]?){1,4}\d{3,4}')
email_re = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')

with open(outdir / f"{args.subreddit}.jsonl", 'w', encoding='utf-8') as fout:
    for post in reddit.subreddit(args.subreddit).search('myocardial infarction OR heart attack', limit=args.limit):
        text = post.title + '\n' + (post.selftext or '')
        # basic de-id
        text = phone_re.sub('[PHONE]', text)
        text = email_re.sub('[EMAIL]', text)
        obj = {
            'id': post.id,
            'created_utc': post.created_utc,
            'url': post.url,
            'text': text,
            'score': post.score
        }
        fout.write(json.dumps(obj, ensure_ascii=False) + '\n')

print('Done')
