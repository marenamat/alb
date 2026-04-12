# Album generator

This should generate websites showing basic photo albums.

There are definitely some questions to be clarified. Ask.

## Landing page

Index of albums, ordered by time, with thumbnails and descriptions.

The photo library lives in a directory (e.g. `~/foto`). In that directory, there
is an `albums.yaml` which `alb` aggregates from per-album `index.yaml` files in
subdirectories. The generated landing page `index.html` is written to that same
directory. A top-level `Makefile` provides `make install` to recursively rsync
everything to the configured server.

There should be multiple landing pages pre-generated, based on what capabilities
are allowed by the current user, showing only that.

Stored in YAML, example:

```yaml
albums:
  - url: 2025-10-barcelona
    thumbnail: 0O9A1835.JPG
    cs:
      title: Říjen 2025, dovolená v Barceloně
      desc: Montserrat z jihu; Vilanova i la Geltrú a železniční muzeum; Barcelona
    en:
      title: October 2025, vacation in Barcelona
      desc: Montserrat, southern path; Vilanova i la Geltrú and railway museum; Barcelona
    access:
      - public
  - url: 2025-09-rodinna-oslava
    thumbnail: P15342.JPG
    cs:
      title: Září 2025, rodina
      desc: Oslavy narozenin
    en:
      title: September 2025, family
      desc: Birthday parties
    access:
      - family
  - url: 2026-02-nsfw
    thumbnail: IMG1248.JPG
    en:
      title: Únor 2026, selfies
      desc: redacted
    access:
      - nsfw

meta:
  author: Maria Matejka
  title: Photo album list
  og-description: Various photosets
  thumbnail:
    album: 2025-10-barcelona
    photo: 0O9A1853.JPG
    alt: Abandoned piece of road nearby Barcelona
```

## Albums

Thumbnails of photos, ordered by time. Click to open larger (max 1024x1024),
showing descriptions.

Truncated descriptions (2 lines max) are displayed below each thumbnail on the
album index page. The full description is shown on hover. The `title` attribute
carries the full text for no-JS fallback.

Prototype at: https://alb.jmq.cz/2025-08-nurnberg/

You may use that website as test data.

## Access control

For the first version, everything is public. The `access` list in `albums.yaml`
controls only whether an album appears on the landing page:

- If an album has `public` in its `access` list, it is listed on the public landing page.
- If `public` is absent from `access`, the album is unlisted (not shown on landing page),
  but still accessible by direct URL.

Full per-user capability-based access control is deferred to a future version.

# Owner workflow

## Input

Photo dump from a camera. Run a CLI command pointing to a camera dump folder and open a
preliminary website locally (run HTTP server, `xdg-open URL`) displaying all photos
as if published. That folder is one future album.

By pressing DELETE key, mark the photo for omission but do not delete it. Allow
displaying all photos including deleted ones, and undeleting.

By pressing ENTER, open photo description editor allowing to enter localized descriptions.
By default, open CS and EN descriptions; commit the description by ENTER, 
allow adding explicit newline by shift+ENTER and ctrl+enter. The description
should be interpreted as markdown.

By pressing shift+G, open `gimp` with that photo. Watch for new files created
in the album directory while GIMP is open. A modified photo will be saved under
a name like `<something>-orez.jpg` or `<something>-rot.jpg` (various suffixes).
When such a file appears, automatically mark the original `<something>.jpg` as
hidden (but do not delete it). Allow displaying photos before modification.

Save all data to `index.yaml` into the camera dump folder. Every five minutes,
copy `index.yaml` to `backup-yyyy-mm-dd--hh-mm.yaml` if something goes wrong.

Allow editing the album's url, title and description, and selecting its thumbnail.
Allow choosing the album's required access capabilities.

When tools starts again, re-load `index.yaml`.

## Generate the website

On clicking a button, the tool should generate a subdirectory `views` with `index.html`.
Use common CSS and JS for all albums.

There should be also a `Makefile` allowing for:
- `make install` to `rsync` the directory to a configured server
- `make edit` to re-run the editor

# Details

- Use Bootstrap 5.x for layouts; self-hosted, served from the album as a separate file
- Use Garamond serif fonts
- No other external JS/CSS dependency
- The website should work in basic mode even without JS
- Upgrade to newer Bootstrap when a new version is released
- Expect future localization of the app to different languages

# Miscellaneous

- This project has no Github actions. No need to check them.
- Do not create github actions even if the claude-base repository requires
  them, it's irrelevant for this project.
