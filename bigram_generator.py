#!/usr/bin/env python3
"""
bigram_generator.py

Prototype of a bigram (order-1 Markov) sentence generator, implemented with
the *same data structure* that will later be built in Scratch:

    from_words  : unique "from" words, one entry each
    start_index : index into to_words where this word's continuations begin
    counts      : how many continuations this word has (its block length)
    to_words    : flat list of "next word" observations, grouped by from_words,
                  WITH repetition -- a continuation that occurred N times in the
                  corpus appears N times in its block. That repetition is what
                  lets a uniform random pick behave as a frequency-weighted
                  pick with no extra weighting logic -- the trick that keeps
                  this fast and simple to port to Scratch.

Sentence boundaries (. ! ?) are respected: a bigram is never formed across a
sentence boundary, and every sentence-initial word is a valid seed to start
generation from.

Usage:
    python bigram_generator.py --file mybook.txt --length 12 --sentences 5
    python bigram_generator.py                       # falls back to a small demo text
    python bigram_generator.py --mode argmax          # deterministic "most likely word" mode
    python bigram_generator.py --export-dir scratch_lists   # also write Scratch-importable list files
"""

import argparse
import random
import re
from collections import defaultdict

SENTENCE_END = re.compile(r"[.!?]+")
# Punctuation to strip before tokenizing (Hebrew + Latin quotes/brackets/commas).
STRIP_PUNCT = re.compile(r"[\"'()\[\]{},;:""''׳״«»]")
# A token made entirely of dash characters (a standalone "–" used as a dialogue/aside
# marker, common in older Hebrew prose) is punctuation, not a word -- drop it. A hyphen
# that joins word-parts with no surrounding space (e.g. "קל-וחומר") stays untouched,
# since it never appears as its own whitespace-separated token.
DASH_ONLY = re.compile(r"^[-–—־]+$")

DEMO_TEXT = (
    "החתול שלי אוהב חלב. הכלב שלי אוהב חלב. החתול שלי ישן על הספה. "
    "הכלב שלי רץ בגינה. החתול אוהב לישון והכלב אוהב לרוץ. "
    "הילד אוהב את הכלב ואת החתול. הילד משחק עם הכלב בגינה."
)


def load_text(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return f.read()
    return DEMO_TEXT


def tokenize_into_sentences(text):
    """
    Strip punctuation, split into sentences, split each sentence into words.
    A newline always ends a sentence too (needed for corpora like one-sentence-
    per-line dumps that carry no trailing period), on top of splitting on . ! ?
    within a line.
    """
    sentences = []
    for line in text.split("\n"):
        line = STRIP_PUNCT.sub(" ", line)
        for chunk in SENTENCE_END.split(line):
            words = [w for w in chunk.split() if not DASH_ONLY.match(w)]
            if words:
                sentences.append(words)
    return sentences


def build_bigram_table(sentences):
    """
    Build the four parallel lists, mirroring the Scratch layout exactly.
    Internally 0-indexed here; add +1 to start_index when exporting for
    Scratch, since Scratch lists are 1-indexed.
    """
    buckets = defaultdict(list)  # from_word -> [to_word, to_word, ...] (with repeats)
    from_order = []              # first-seen order, kept for reproducibility

    for words in sentences:
        for i in range(len(words) - 1):
            w_from, w_to = words[i], words[i + 1]
            if w_from not in buckets:
                from_order.append(w_from)
            buckets[w_from].append(w_to)

    from_words, start_index, counts, to_words = [], [], [], []
    for w in from_order:
        from_words.append(w)
        start_index.append(len(to_words))
        block = buckets[w]
        counts.append(len(block))
        to_words.extend(block)

    return from_words, start_index, counts, to_words


def next_word(current, from_words, start_index, counts, to_words, mode="sample"):
    """
    mode="sample" -> uniform random pick within the block (frequency-weighted
                      automatically, because of repetition)
    mode="argmax" -> most frequent continuation (ties broken by first-seen order)
    Returns None if `current` was never observed as a "from" word (dead end).
    """
    try:
        idx = from_words.index(current)
    except ValueError:
        return None

    start = start_index[idx]
    n = counts[idx]
    block = to_words[start:start + n]

    if mode == "argmax":
        tally = defaultdict(int)
        for w in block:
            tally[w] += 1
        return max(tally.items(), key=lambda kv: kv[1])[0]

    return random.choice(block)


def generate(seed, length, from_words, start_index, counts, to_words, mode="sample"):
    if seed is None:
        seed = random.choice(from_words)
    elif seed not in from_words:
        raise ValueError(f"'{seed}' never appears as a starting word in this corpus.")

    sentence = [seed]
    current = seed
    for _ in range(length - 1):
        nxt = next_word(current, from_words, start_index, counts, to_words, mode)
        if nxt is None:
            break  # dead end: current word never continues anywhere in the corpus
        sentence.append(nxt)
        current = nxt
    return " ".join(sentence)


def export_scratch_lists(out_dir, from_words, start_index, counts, to_words):
    import os
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "from_words.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(from_words))
    with open(os.path.join(out_dir, "start_index.txt"), "w", encoding="utf-8") as f:
        # +1: Scratch lists are 1-indexed
        f.write("\n".join(str(i + 1) for i in start_index))
    with open(os.path.join(out_dir, "count.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(str(c) for c in counts))
    with open(os.path.join(out_dir, "to_words.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(to_words))
    print(f"Scratch-importable lists written to: {out_dir}/"
          f"(from_words.txt, start_index.txt, count.txt, to_words.txt)")


def main():
    parser = argparse.ArgumentParser(description="Bigram sentence generator prototype")
    parser.add_argument("--file", help="path to a plain-text corpus (UTF-8). Defaults to a small built-in Hebrew demo.")
    parser.add_argument("--length", type=int, default=10, help="words per generated sentence")
    parser.add_argument("--sentences", type=int, default=5, help="how many sentences to generate")
    parser.add_argument("--seed-word", default=None, help="force a specific starting word")
    parser.add_argument("--mode", choices=["sample", "argmax"], default="sample",
                         help="'sample' = frequency-weighted random pick (varied); "
                              "'argmax' = always the most frequent continuation (deterministic, tends to repeat/loop)")
    parser.add_argument("--export-dir", default=None,
                         help="if set, also write the four Scratch-importable list files here")
    args = parser.parse_args()

    text = load_text(args.file)
    sentences = tokenize_into_sentences(text)
    from_words, start_index, counts, to_words = build_bigram_table(sentences)

    total_tokens = sum(len(s) for s in sentences)
    print(f"Corpus stats: {total_tokens} tokens, {len(sentences)} sentences, "
          f"{len(from_words)} unique 'from' words, {len(to_words)} bigram observations.\n")

    for i in range(args.sentences):
        try:
            out = generate(args.seed_word, args.length, from_words, start_index, counts, to_words, args.mode)
        except ValueError as e:
            print(f"Error: {e}")
            break
        print(f"{i + 1}. {out}")

    if args.export_dir:
        print()
        export_scratch_lists(args.export_dir, from_words, start_index, counts, to_words)


if __name__ == "__main__":
    main()
