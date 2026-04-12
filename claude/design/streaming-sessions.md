# Streaming in-progress session info (issue #12)

Design proposal for streaming live session data from `clanker-run` to
`claude-dashboard`.

---

## Goal

Allow `claude-dashboard` to show:

- which project sessions are currently running
- live log output from the running Claude invocation
- token counts and cost as they accumulate

---

## Approach: file-based live state

`clanker-run` is a shell script with no persistent process. The simplest
reliable method is writing a **current-run file** that lives for the
duration of the invocation and is consumed by the dashboard.

No server process, no sockets, no new dependencies.

---

## 1. `clanker-current.json` — active run record

`clanker-run` writes this file immediately before invoking Claude and
**deletes it** (or replaces it with a "done" marker) on exit.

```json
{
  "pid":        12345,
  "start":      "2026-04-12T10:00:00+00:00",
  "project":    "/home/user/myproject",
  "log_file":   "/tmp/clanker-run-12345.jsonl",
  "status":     "running",
  "tokens_in":  0,
  "tokens_out": 0,
  "cost_usd":   null
}
```

Fields:

- **pid**: PID of the bash process running clanker-run (for alive-check).
- **start**: ISO 8601 start time.
- **project**: absolute path to the project directory (same as `selfdir`).
- **log_file**: path to the temp file receiving raw stream-json output.
  The dashboard can tail this file for live log lines.
- **status**: `"running"` while active; `"done"` briefly before deletion
  (lets the dashboard distinguish "gone" from "never existed").
- **tokens_in / tokens_out / cost_usd**: updated in-place from the
  stream-json `result` message as soon as it arrives.

The file is written to `$selfdir/clanker-current.json` so the dashboard
can find it alongside `clanker-runs.jsonl`.

### Heartbeat / stale detection

If the process dies without cleanup (power loss, SIGKILL), the file is
left behind. The dashboard should treat the record as stale if:

- `status == "running"` AND
- `pid` no longer exists (`kill -0 $pid` fails) AND
- current time − `start` > some timeout (e.g. 4 hours)

---

## 2. Live token/cost updates

`clanker-run` already parses stream-json lines to extract the final
`result` record. With small modifications it can update
`clanker-current.json` incrementally:

- On each `assistant` message, accumulate `usage.input_tokens` and
  `usage.output_tokens` from the delta, update the file in-place.
- On the final `result` message, write the authoritative values.

In-place update is a single `jq` call or a small Python snippet; it is
cheap enough to run per-message.

---

## 3. Changes to `clanker-run`

```
Before claude invocation:
  write clanker-current.json  (status: running)

While claude runs (stream-json tee loop):
  on each parsed line:
    if type == "assistant" and usage present:
      update tokens_in/tokens_out in clanker-current.json
    if type == "result":
      update all cost/token fields, set status = "done"

After claude exits:
  if status != "done": update status = "done" in the file
  rm clanker-current.json   (or keep for 60 s for dashboard to read final state)
```

The tee loop replaces the current `claude ... >"$tmp_out"` pattern.
Instead of buffering everything and then dumping to the log, we:

1. Run Claude with output going to a named temp file (already done).
2. In a background `tail -f` fed through the Python parser, update
   `clanker-current.json` as lines arrive.
3. On exit, append `$tmp_out` to `clanker.log` as now.

---

## 4. Dashboard integration

`claude-dashboard` reads `clanker-runs.jsonl` for finished runs (already
specified in `claude-base.md` §6). For live sessions it adds:

1. **Poll** each configured project directory for `clanker-current.json`
   every few seconds (e.g. 3 s).
2. If the file is present and `status == "running"`:
   - Show a "LIVE" badge on the project card.
   - Display `tokens_in`, `tokens_out`, `cost_usd` from the file.
   - Offer a "tail log" view that reads `log_file` and streams the last N
     lines to the UI (dashboard is local, so direct file access works).
3. Parse stream-json lines from `log_file` to render human-readable
   assistant messages in the live log view (strip json envelope, show
   `content` blocks).
4. When `clanker-current.json` disappears, refresh the finished-runs list
   from `clanker-runs.jsonl`.

### Dashboard config

The dashboard needs to know which directories to watch. Options:

a. A config file listing project paths (simplest).
b. A glob pattern (e.g. `~/projects/*/clanker-current.json`).
c. A central registry file written by `clanker-run` on first use.

Option (b) with a configurable glob is recommended — zero extra setup for
the common single-machine case, and the dashboard just scans matching
paths on each poll cycle.

---

## 5. Summary of new/changed files

| File | Change |
|------|--------|
| `clanker-run` | Write/update/delete `clanker-current.json`; add per-line token update loop |
| `clanker-current.json` | New ephemeral file (not committed, add to `.gitignore`) |
| `claude-dashboard` `generate-data.py` | Poll project dirs for `clanker-current.json`, expose in API/data |

No new runtime dependencies beyond what is already present (Python 3,
bash, jq or inline Python for JSON update).

---

## Open questions for guardian

1. Is the dashboard local-only (file access is fine) or does it need to
   work over HTTP/SSH to a remote machine?  If remote, we need a small
   HTTP server or SSH-based file fetch rather than direct file reads.
2. Should `clanker-current.json` be written to `$selfdir` (project dir)
   or to a central location (e.g. `~/.clanker/`)?  Central location
   simplifies dashboard discovery but requires coordination between
   multiple concurrent projects.
3. Desired poll interval for the dashboard?
