# Questions

## Blocking: `gh` CLI not authenticated

`gh` is installed but not logged in. Please run `gh auth login` so I can:
- Check CI/CD pipeline results
- List and work on GitHub issues

**A**: Use curl and raw API instead.

## Design: Access control — needs further refinement

`claude/design/base.md` says "This section needs further refinements" for access control.

Specific questions:
1. **Link-based authentication** — what does this mean? A secret token in the URL
   (e.g. `https://alb.example.com/family/?token=xyz`) that sets a cookie?
2. **Cookie lifetime** — how long should the session cookie last?
3. **NGINX config** — should the NGINX config use `auth_request` to a helper,
   or is it purely static (sub_filter / map directives)?
4. **How are tokens issued?** Via a separate admin page, or pre-generated
   in the YAML and embedded in invite links?

**A**: Until further notice, ignore access control. Everything public for the
first version, only if `public` is missing from the access list, unlist that
album from the landing page.

## Design: Bootstrap sourcing

`claude/design/base.md` says "Use Bootstrap" and "No other external JS/CSS dependency".

- Should Bootstrap be self-hosted (bundled into the repo / served from the album)?
- Or is loading from a CDN acceptable as a single exception?
- Which Bootstrap version? (5.x is current)

**A**: Selfhosted and served from the album as a separate file. Version 5.x is ok.

## Design: GIMP integration — modified file naming

The design says: "Supersede every photo named `<something>.jpg` by `<something>-<mod>.jpg`".

- Does `alb` need to watch for file changes after GIMP exits and auto-rename
  the modified file, or is the `-<mod>` suffix a convention the user applies
  manually in GIMP before saving?
- Should the original file be kept alongside the modified version, or hidden?

**A**: There may be various suffixes, e.g. `<something>-orez.jpg` or `<something>-rot.jpg`.
Watch for new file creation. Do not touch the original file, just auto-mark
it hidden.

## Design: Landing page — where does the YAML live?

The design shows a `albums:` YAML structure for the landing page,
but doesn't specify where this file should be stored.

- Is it a separate `albums.yaml` at the server root?
- Or does `alb` aggregate `index.yaml` files from subdirectories?
- Where should the generated landing page HTML go?

**A**: There will be a directory, e.g. `~/foto`. In that directory,
there will be `albums.yaml` which should be aggregated by Alb from
subdirectories. The generated landing page should be generated in the same
directory. Add `Makefile` so that `make install` installs everything
recursively.

## Packages needed (please install)

The following Alpine packages are required to run `alb`:

```
apk add py3-yaml py3-jinja2 py3-aiohttp
```

These provide:
- `py3-yaml` — YAML loading/saving (`import yaml`)
- `py3-jinja2` — HTML template rendering (`import jinja2`)
- `py3-aiohttp` — async HTTP server + WebSocket (`import aiohttp`)
