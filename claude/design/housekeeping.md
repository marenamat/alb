# Housekeeping (issue #15)

Daily automated health check for claude-base projects.

---

## Goal

Keep the project in a consistently clean state between regular Claude runs:

- All open issues are either being worked on (branch exists) or pending review
  (branch has unmerged commits and a PR is open / ready to merge).
- All local branches are rebased onto main.
- `claude/questions.md` contains no open items.

A guardian can glance at `clanker-housekeeping.json` (or the dashboard) to
see the project health without reading git log or issue tracker directly.

---

## How it works

`clanker-housekeeping` is a thin shell wrapper around `clanker-run`.  It sets:

```sh
CLANKER_PROMPT="perform housekeeping as specified in CLAUDE.md"
CLANKER_TASK="housekeeping"
```

`clanker-run` reads these env vars and passes the custom prompt to Claude.
The live session record in `clanker-current.json` includes `"task": "housekeeping"`
so the dashboard can distinguish housekeeping runs from regular ones.

---

## Schedule

`clanker-setup` installs a second timer/cron entry that runs
`clanker-housekeeping` once a day at 03:00 local time (systemd: `OnCalendar`;
cron: `0 3 * * *`).

Both `clanker-run` and `clanker-housekeeping` share `clanker.lock`, so they
never run concurrently.

---

## Machine-readable output: `clanker-housekeeping.json`

Written by Claude at the end of each housekeeping run (see CLAUDE.md for the
exact schema).  Not committed to git — it is a transient status file like
`clanker-prep.json`.

Added to `.gitignore`.

### Dashboard integration

The dashboard reads `clanker-housekeeping.json` alongside `clanker-prep.json`
and `clanker-runs.jsonl` to show:

- **Pending review** badge on issues awaiting guardian merge.
- **Needs attention** badge on issues with no active branch.
- **Questions open** indicator when `claude/questions.md` is non-empty.
- `all_clean: true` green status when everything is tidy.
