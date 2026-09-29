---
name: start-lesson
description: Start a lesson from the beginning for a student. Usage: /start-lesson <lesson-id> <student>
argument-hint: <lesson-id> <student>
disable-model-invocation: true
---

Arguments: $ARGUMENTS  (first = lesson-id, second = student id)

1. Verify `lessons/<lesson-id>/lesson.md` exists; if not, list available lessons and stop.
2. Stop any watcher still running from a previous run.
3. Create `runs/<student>/<lesson-id>/<YYYY-MM-DD_HHMM>/` with `snapshots/`, `parsed/`, empty `log.md` and
   `events.jsonl`, and a fresh `state.json` (step 1, status in_progress). Never reuse or modify an earlier run folder.
4. Read `version` from `prompts/tutor_prompt.md` frontmatter and record it as `tutor_prompt_version`.
5. Get the Scratch editor to the lesson's starting project: ask the adult to load `starter.sb3` via
   File → Load from your computer (give the full path), or start a new empty project if there's no starter.
6. Start `tools/watch_downloads.py --run-dir <run-dir>` in the background.
7. Read `lesson.md`, then open Step 1 with its "Tutor opening". Write the first log entry.
