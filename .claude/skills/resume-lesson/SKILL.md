---
name: resume-lesson
description: Resume a student's most recent unfinished run of a lesson. Usage: /resume-lesson <lesson-id> <student>
argument-hint: <lesson-id> <student>
disable-model-invocation: true
---

Arguments: $ARGUMENTS

1. Find the newest folder under `runs/<student>/<lesson-id>/` whose state.json status is `in_progress`.
   If none, say so and suggest /start-lesson.
2. Read state.json, the tail of log.md, and the latest parsed snapshot.
3. Get a tab open, in a tab you control, matching where the student left off. Address the student directly for
   all of this -- they're the one at the keyboard; only loop in the adult for something a child genuinely
   can't do alone.
   - **If Claude in Chrome's tools are available:** call `tabs_context_mcp` with `createIfEmpty: true` (safe even
     if a group already exists), then `navigate` a tab in that group to `scratch.mit.edu`. Tell the student
     plainly: this is the tab to work in from now on.
   - **Guide the student to reopen their project from their own Scratch account ("הדברים שלי"), not a local
     file:** tell them to sign in if they aren't already, then get to **הדברים שלי** -- the fastest route is a
     purple **folder icon** in the editor's own top bar (only shown when signed in); if that isn't visible, their
     username (top right) → הדברים שלי also works. Find the project from last time, and click on it to open it.
     This only works if the student actually has a
     Scratch account and saved there online (as opposed to only ever using the File menu's "הורידו למחשב", which
     downloads locally and doesn't appear in הדברים שלי) -- most students who've used Scratch before already do this.
   - **If that doesn't pan out** (no account, can't find the project there, or it doesn't match what `state.json`
     says they'd built): fall back to the local snapshot, if `last_snapshot` is set -- that one genuinely needs
     an adult's help, since it means typing a file path. Ask the adult to load that snapshot's `.sb3` into the
     same tab via the File menu's **"Load from your computer"** item (it stays in English even in the Hebrew
     interface -- give the full path).
   - **If neither applies** (no online project, no local snapshot either -- `last_snapshot` is `null`, meaning
     nothing was ever actually saved): say so plainly to the student, and treat this like resuming the *current
     step* from its start, in the fresh/blank tab you opened.
   - **If Claude in Chrome isn't available:** guide the student through the same הדברים שלי flow in whatever
     Scratch window they already have open, falling back the same way if that doesn't pan out.
4. Check `<run-dir>/.watcher.pid` for this run. If that PID is still alive, leave it running rather than starting
   a second one; only start a fresh `tools/watch_downloads.py --run-dir <run-dir>` if it's dead or missing.
5. Note the resume in `log.md` (and `state.json`'s `updated_at`) before saying anything to the student.
6. Re-orient the student briefly, in Hebrew (something like "בפעם הקודמת עבדנו על ...") and continue the current step.
