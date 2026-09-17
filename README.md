# Task: pull the tomron87 Hebrew Wikipedia corpus and build its bigram table

## Context

This is one step in a larger project: building a bigram (order-1 Markov chain)
Hebrew sentence generator, eventually implemented in Scratch, currently
prototyped in Python. Two corpora are already done (a Mendele Mocher Sforim
novel, and a 50k-sentence Hebrew Wikipedia sample called SVLM). This task adds
a third, better-curated corpus: `tomron87/hebrew-wikipedia-sentences-corpus`
on Hugging Face (11M deduplicated Hebrew Wikipedia sentences, CC BY-SA 3.0,
filtered to 5-50 words per sentence with high Hebrew-character ratio).

That dataset could **not** be pulled from the sandboxed cloud session this
project was built in — Hugging Face is blocked by that sandbox's network
policy, and going through Hugging Face's paginated preview API via a
summarizing fetch tool only got a small (~4,600 token), disjointed sample
that produced poor generation quality. Running this on a machine with normal,
unrestricted internet access should get a much bigger, cleaner corpus in one
shot.

Two scripts are provided alongside this README — use them as-is, don't
rewrite them:

- `fetch_tomron_corpus.py` — downloads the dataset and writes a plain-text
  corpus file (one sentence per line).
- `bigram_generator.py` — builds the bigram table from any plain-text corpus
  and can generate/sample sentences from it. Already used successfully on the
  other two corpora; the logic here is the reference implementation this
  whole project is standardizing on (it's also being ported to Scratch, so
  don't change its algorithm, only call it).

## Steps

1. Confirm `python3` and `pip` are available.

2. Run the fetch script. Default mode takes a **contiguous** 50,000-sentence
   block (sentences from the same articles stay adjacent to each other,
   which matters a lot for bigram continuity — a random scattered sample
   across many unrelated articles produces much worse, more incoherent
   generated text, confirmed already in this project):

   ```
   python3 fetch_tomron_corpus.py --contiguous 50000 --start 0 --out hebrew_wiki_tomron.txt
   ```

   This downloads the dataset via the `datasets` library (installs it
   automatically if missing) — expect a one-time ~1.8GB download, cached
   afterward by the library. If disk space or bandwidth is a concern, a
   smaller block (e.g. `--contiguous 15000`) is a reasonable fallback — say
   in your final report which size was actually used and why, if you had to
   deviate from 50,000.

3. Run the bigram generator against the fetched corpus to confirm it works
   and to get a feel for output quality:

   ```
   python3 bigram_generator.py --file hebrew_wiki_tomron.txt --sentences 8 --length 12
   python3 bigram_generator.py --file hebrew_wiki_tomron.txt --sentences 4 --length 12 --mode argmax
   ```

   Note the printed corpus stats line (tokens / sentences / unique 'from'
   words / bigram observations) — report these numbers back verbatim, they
   matter for evaluating this corpus against the other two.

4. Export the Scratch-importable bigram table (four parallel list files —
   this is the actual deliverable the rest of the project consumes):

   ```
   python3 bigram_generator.py --file hebrew_wiki_tomron.txt --sentences 1 --export-dir scratch_lists_tomron
   ```

   This produces `scratch_lists_tomron/{from_words,start_index,count,to_words}.txt`.

## What to hand back

- `hebrew_wiki_tomron.txt` (the corpus)
- the `scratch_lists_tomron/` directory (the four exported list files)
- the corpus-stats line and a handful of sample generated sentences (both
  `sample` and `argmax` modes) from step 3, so quality can be compared
  against the Mendele book and SVLM corpora already in hand

If anything in `fetch_tomron_corpus.py` or `bigram_generator.py` actually
fails (not just "took a while"), report the exact error rather than working
around it by changing the scripts' logic — the algorithm needs to stay
identical across every corpus for the comparison to mean anything, since it's
also the spec for the Scratch implementation.
