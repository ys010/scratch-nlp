#!/usr/bin/env python3
"""
Downloads tomron87/hebrew-wikipedia-sentences-corpus from Hugging Face and
writes a plain-text, one-sentence-per-line corpus file -- the same format
bigram_generator.py expects (--file <this output>).

Run this somewhere with normal internet access -- your own machine via
Claude Code or a plain terminal, NOT the sandboxed cloud session, since
huggingface.co is blocked from there.

Prerequisites (installed automatically if missing):
    pip install datasets

Usage:
    # 50,000 randomly-sampled sentences (~a few MB), good default corpus size
    python3 fetch_tomron_corpus.py --sample 50000 --out hebrew_wiki_tomron.txt

    # a single contiguous block instead of scattered random sentences --
    # keeps related sentences (same article) next to each other, which
    # makes for a much less disjointed bigram model than a random sample
    python3 fetch_tomron_corpus.py --contiguous 50000 --start 0 --out hebrew_wiki_tomron.txt

    # the full ~11M-sentence corpus (large: ~1.8GB download)
    python3 fetch_tomron_corpus.py --all --out hebrew_wiki_tomron_full.txt
"""
import argparse
import subprocess
import sys


def ensure(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", type=int, default=None,
                         help="randomly sample this many sentences from across the whole corpus")
    parser.add_argument("--contiguous", type=int, default=None,
                         help="take this many sentences as one contiguous block starting at --start "
                              "(keeps sentences from the same articles adjacent -- better bigram continuity "
                              "than a random --sample)")
    parser.add_argument("--start", type=int, default=0, help="start offset for --contiguous")
    parser.add_argument("--all", action="store_true", help="write the full corpus (~11M sentences, ~1.8GB download)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="hebrew_wiki_tomron.txt")
    parser.add_argument("--min-words", type=int, default=5)
    parser.add_argument("--max-words", type=int, default=50)
    args = parser.parse_args()

    if not args.all and args.sample is None and args.contiguous is None:
        args.contiguous = 50000  # sensible default: one coherent block, not scattered sentences

    ensure("datasets")
    from datasets import load_dataset

    print("Downloading/loading dataset (first run downloads ~1.8GB, cached after that)...")
    ds = load_dataset("tomron87/hebrew-wikipedia-sentences-corpus", split="train")
    print(f"Loaded {len(ds):,} rows total.")

    if args.all:
        subset = ds
    elif args.contiguous is not None:
        end = min(args.start + args.contiguous, len(ds))
        subset = ds.select(range(args.start, end))
        print(f"Taking contiguous rows [{args.start}:{end}] ({end - args.start:,} rows).")
    else:
        n = min(args.sample, len(ds))
        subset = ds.shuffle(seed=args.seed).select(range(n))
        print(f"Randomly sampled {n:,} rows (seed={args.seed}).")

    written = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for row in subset:
            s = (row.get("sentence") or "").strip()
            if not s:
                continue
            wc = row.get("word_count") or len(s.split())
            if args.min_words <= wc <= args.max_words:
                f.write(s + "\n")
                written += 1

    print(f"Wrote {written:,} sentences to {args.out}")
    print("Next step: python3 bigram_generator.py --file " + args.out)


if __name__ == "__main__":
    main()
