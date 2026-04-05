# Questions / Action items for guardian

## Close issue #6

Issue #6 (setup-remotes) is fully implemented and merged to main.
Please close it:

```sh
curl -X PATCH \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/marenamat/claude-base/issues/6 \
  -d '{"state":"closed","state_reason":"completed"}'
```
