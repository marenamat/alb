# Questions

## Markdown rendering for photo descriptions

The design says photo descriptions "should be interpreted as markdown" on the
generated static pages. No Python markdown library is currently installed.

Options (need one installed):
1. `python-markdown` (`import markdown`) — most common, pip: `pip install Markdown`
2. `mistletoe` — fast CommonMark parser, pip: `pip install mistletoe`

Please install one. Once available, descriptions in `album-index.html.j2` and
`album-single.html.j2` will be rendered as HTML via a Jinja2 filter in `Generator.py`.

## GitHub API rate limit

Unauthenticated API calls are rate-limited to 60/hour per IP. The limit gets
exhausted during normal workflow runs (checking issues, pipelines, etc.).

A personal access token (PAT) with read-only repo scope would give 5000 req/hour.
Options:
1. Create a PAT and store it at `~/.github_token` (or similar)
2. Or another location — just tell me where to look
