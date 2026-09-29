---
name: end-lesson
description: End the current lesson run, marking it completed or abandoned. Usage: /end-lesson [completed|abandoned]
argument-hint: "[completed|abandoned]"
disable-model-invocation: true
---

Arguments: $ARGUMENTS (optional: "completed" or "abandoned"; default to "completed" if every step's status is done, otherwise "abandoned")

1. Identify the active run for this session (the one most recently started/resumed). If there isn't one, say so and stop.
2. Update `state.json`: set `status` to the resolved value above and `updated_at` to now.
3. Stop the run's watcher: read `<run-dir>/.watcher.pid`, terminate that process if it's still running, then remove the pid file.
4. Compute a short summary from `state.json` and `log.md`:
   - steps completed vs. total steps in `lessons/<lesson_id>/lesson.md`
   - hints given per step
   - total time (`updated_at` - `started_at`)
5. Append that summary to `log.md` as the final entry, then show it to the adult/child.
