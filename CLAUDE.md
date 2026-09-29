## Tutor, lessons and runs
- Tutor agent: `.claude/agents/tutor.md`; launch with `claude --agent tutor` (then `/desktop` to continue in the app).
- Tutor pedagogy: `prompts/tutor_prompt.md` (versioned; edited only by the content creator).
- Lessons: `lessons/<id>/lesson.md` (+ optional `starter.sb3`). Template in `lessons/_template/`.
- Student runs: `runs/<student>/<lesson>/<timestamp>/` (git-ignored). `state.json` is the source of truth.
- Commands: /start-lesson, /resume-lesson, /list-runs, /end-lesson.
- Tools: `tools/watch_downloads.py`, `tools/sb3_parser.py` (+ `tools/sync_tutor.sh` if the worktree fallback exists).
