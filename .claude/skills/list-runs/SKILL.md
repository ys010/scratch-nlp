---
name: list-runs
description: List lesson runs, optionally filtered to one student. Usage: /list-runs [student]
argument-hint: "[student]"
disable-model-invocation: true
---

Arguments: $ARGUMENTS (optional: a single student id to filter to)

1. If a student id was given, look under `runs/<student>/*/*/`. Otherwise look under `runs/*/*/*/`.
2. For each run folder found, read its `state.json` (skip silently if missing or unreadable -- a run mid-creation).
3. Print a table sorted by `updated_at` descending, with columns:
   student, lesson_id, run_id, status, current_step (e.g. "2/3", using the lesson's step count from `lessons/<lesson_id>/lesson.md` if easy to determine, otherwise just the number), tutor_prompt_version.
4. If no runs match, say so plainly (e.g. "No runs yet for <student>." or "No runs yet.").
