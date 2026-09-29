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
5. Get the Scratch editor to the lesson's starting project: ask the adult to load `starter.sb3` via
   File → Load from your computer (give the full path), or start a new empty project if there's no starter.
6. Start `tools/watch_downloads.py --run-dir <run-dir>` in the background.
7. Read `lesson.md`, then open Step 1 with its "Tutor opening". Write the first log entry.
