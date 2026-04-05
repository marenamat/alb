# Questions for Maria

## Issues ready to close on GitHub

All three open issues are implemented and merged to main. Please close them:

- **#2 Restart the runner if updated by git** — implemented in `clanker-run` (checksum/re-exec logic)
- **#3 Prepare your own website** — website in `docs/`, deployed via GitHub Pages, pipeline green
- **#4 If rebase fails, run clanker** — implemented in `clanker-prep` (rebase_failed triggers INVOKE_CLAUDE)

Until these are closed, `clanker-prep` will keep flagging #2 and #4 as "unhandled issues" (no branch contains "2" or "4"), invoking Claude unnecessarily each run.
