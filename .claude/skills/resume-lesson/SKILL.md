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
3. Get a tab open, in a tab you control, matching where the student left off:
   - **If Claude in Chrome's tools are available:** call `tabs_context_mcp` with `createIfEmpty: true` (safe even
     if a group already exists), then `navigate` a tab in that group to the Scratch editor. Tell both the adult
     and the student plainly, in one message: this is the tab to work in from now on.
     - If `last_snapshot` is set: ask the adult to load that snapshot's `.sb3` into *that specific tab* via
       File → Load from your computer (give the full path), so it matches where the student left off.
     - If `last_snapshot` is `null` (the student never actually got a save through, however far they got
       verbally): there's nothing to load -- say so plainly, and treat this like resuming the *current step*
       from its start, in the fresh/blank tab you just opened.
   - **If Claude in Chrome isn't available:** fall back to asking the adult to load the latest snapshot into
     whatever Scratch window they have open themselves (full path), or start fresh if there's no snapshot.
4. Check `<run-dir>/.watcher.pid` for this run. If that PID is still alive, leave it running rather than starting
   a second one; only start a fresh `tools/watch_downloads.py --run-dir <run-dir>` if it's dead or missing.
5. Note the resume in `log.md` (and `state.json`'s `updated_at`) before saying anything to the student.
6. Re-orient the student briefly ("last time you were working on ...") and continue the current step.
