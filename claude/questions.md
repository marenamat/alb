# Questions

## GitHub API rate limit

Unauthenticated API calls are rate-limited to 60/hour per IP. The limit gets
exhausted during normal workflow runs (checking issues, pipelines, etc.).

A personal access token (PAT) with read-only repo scope would give 5000 req/hour.
Options:
1. Create a PAT and store it at `~/.github_token` (or similar)
2. Or another location — just tell me where to look
