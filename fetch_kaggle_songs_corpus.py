#!/usr/bin/env python3
"""
Converts the Kaggle "Hebrew songs lyrics" dataset (guybarash/hebrew-songs-lyrics,
kaggle.csv) into a plain-text, one-"sentence"-per-line corpus file -- the same
format bigram_generator.py expects (--file <this output>).

The dataset has no punctuation and no preserved line/verse breaks: the `songs`
column is a Python-list-literal string of every word in the whole song, already
tokenized and flattened. There is no finer sentence boundary available in the
scraped data, so each song becomes exactly one "sentence" here -- meaning the
bigram model will chain words across an entire song rather than resetting at
verse breaks like it would with real sentence punctuation. That's a real
difference from the Wikipedia corpus, not a bug in this conversion.

Usage:
    python3 fetch_kaggle_songs_corpus.py --csv kaggle_songs_raw/kaggle.csv --out hebrew_songs_lyrics.txt
"""
import argparse
import ast
import csv


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", default="kaggle_songs_raw/kaggle.csv")
    parser.add_argument("--out", default="hebrew_songs_lyrics.txt")
    parser.add_argument("--min-words", type=int, default=5)
    args = parser.parse_args()

    csv.field_size_limit(10_000_000)

    written = 0
    skipped_parse = 0
    skipped_short = 0
    with open(args.csv, encoding="utf-8-sig", newline="") as f_in, \
            open(args.out, "w", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            try:
                words = ast.literal_eval(row["songs"])
            except (ValueError, SyntaxError):
                skipped_parse += 1
                continue
            words = [w for w in words if w.strip()]
            if len(words) < args.min_words:
                skipped_short += 1
                continue
            f_out.write(" ".join(words) + "\n")
            written += 1

    print(f"Wrote {written:,} songs to {args.out} "
          f"(skipped {skipped_parse:,} unparseable, {skipped_short:,} too short).")
    print("Next step: python3 bigram_generator.py --file " + args.out)


if __name__ == "__main__":
    main()
