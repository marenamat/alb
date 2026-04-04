# Album generator

This should generate websites showing basic photo albums.

There are definitely some questions to be clarified. Ask.

## Landing page

Index of albums, ordered by time, with thumbnails and descriptions.

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

Prototype at: https://alb.jmq.cz/2025-08-nurnberg/

You may use that website as test data.

## Access control

Another YAML, example:

```yaml
users:
  marenamat:
    - nsfw
    - family
    - public
  kmck:
    - nsfw
    - public
  dedecek:
    - family
    - public
```

Every user can have a bunch of capabilities, and that triggers access allowed or
denied. If all capabilities stated in `access` are matched in the user's
capability list, user has access to that resources.

If no access is specified, nobody is allowed to access.

All the website is served by NGINX, design a minimalist cookie-based
and link-based authentication and generate appropriate config files.

This section needs further refinements.

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

By pressing shift+G, open `gimp` with that photo. Supersede every photo named
`<something>.jpg` by `<something>-<mod>.jpg`. Allow displaying photos before
modification.

Save all data to `index.yaml` into the camera dump folder. Every five minutes,
copy `index.yaml` to `backup-yyyy-mm-dd--hh-mm.yaml` if something goes wrong.

Allow editing the album's url, title and description, and selecting its thumbnail.
Allow choosing the album's required access capabilities.

When tools starts again, re-load `index.yaml`.

## Generate the website

On clicking a button, the tool should generate a subdirectory `views` with `index.html`.
Use common CSS and JS for all albums.

There should be also a `Makefile` allowing for `make install` to `rsync` the directory
to a configured server by `make install`, and `make edit` to re-run the editor.

# Details

- Use Bootstrap to create the layouts
- Use Garamond serif fonts
- No other external JS/CSS dependency
- The website should basically work 
- Expect future localization of the app to different languages
