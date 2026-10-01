---
name: start-lesson
description: Start a lesson from the beginning for a student. Usage: /start-lesson <lesson-id> <student>
argument-hint: <lesson-id> <student>
disable-model-invocation: true
---

Arguments: $ARGUMENTS  (first = lesson-id, second = student id)

1. Verify `lessons/<lesson-id>/lesson.md` exists; if not, list available lessons and stop.
2. Stop any watcher still running from a previous run.
3. Create `runs/<student>/<lesson-id>/<YYYY-MM-DD_HHMM>/` (the `YYYY-MM-DD_HHMM` is this run's `run_id`) with
   `snapshots/`, `parsed/`, an empty `log.md`, an empty `events.jsonl`, and a fresh `state.json` using **exactly**
   this shape (fill in the placeholders; `steps` starts with only the current step's entry -- add entries for
   later steps as the run reaches them, don't pre-populate them):
   ```json
   {
     "student": "<student>",
     "lesson_id": "<lesson-id>",
     "run_id": "<YYYY-MM-DD_HHMM>",
     "tutor_prompt_version": "<from prompts/tutor_prompt.md frontmatter>",
     "started_at": "<ISO-8601 now>",
     "updated_at": "<ISO-8601 now>",
     "status": "in_progress",
     "current_step": 1,
     "steps": {
       "1": { "status": "in_progress", "started_at": "<ISO-8601 now>", "completed_at": null,
              "hints_given": 0, "attempts": 0, "last_snapshot": null }
     },
     "last_snapshot": null,
     "notes": ""
   }
   ```
   Never reuse or modify an earlier run folder.
4. Read `version` from `prompts/tutor_prompt.md` frontmatter and record it as `tutor_prompt_version` (already
   reflected in the `state.json` above).
5. Get a tab open, in a tab you control, with the lesson's starting project in it:
   - **If Claude in Chrome's tools are available:** call `tabs_context_mcp` with `createIfEmpty: true` (safe even
     if a group already exists -- it's then a no-op), then `navigate` a tab in that group to the Scratch editor.
     Tell both the adult and the student plainly, in one message: this is the tab to work in from now on --
     don't open Scratch anywhere else.
     - If the lesson has a `starter.sb3`: this one file genuinely isn't in the student's own Scratch account (it's
       the lesson's own template, not something they saved), so there's no "My Stuff" equivalent for it. Guide
       the student through File → Load from your computer in *that specific tab*, but expect they'll likely need
       an adult alongside them to actually navigate to the file (give the full path for the adult's benefit).
     - If there's no starter: the blank project already in that tab is the starting point -- nothing else to load.
   - **If Claude in Chrome isn't available:** guide the student the same way in whatever Scratch window they
     already have open (an adult's help finding `starter.sb3` by its full path, or starting a new empty project
     if there's no starter) -- same as if Chrome were never in the picture.
6. Start `tools/watch_downloads.py --run-dir <run-dir>` in the background.
7. Read `lesson.md`, then open Step 1 with its "Tutor opening". Write the first log entry.
