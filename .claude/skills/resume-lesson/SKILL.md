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
3. Ask the adult to load the latest snapshot .sb3 into Scratch (give the full path), so the editor matches where the student left off.
4. Restart the download watcher for this run.
5. Re-orient the student briefly ("last time you were working on ...") and continue the current step.
