from . import Command, CommandRuntimeException, InvalidArgumentsException
from ..Index import Index

import asyncio
import logging
import mimetypes
import pathlib
import re
import urllib.request
import yaml

logger = logging.getLogger(__name__)


class Migrate(Command):
    command = "migrate"
    argdesc = "<url> <local-dir>"
    helptext = (
        "Migrate an album from the old Perl/pandoc format to the current one.\n"
        "Reads index.md from <local-dir>, matches photos by sorted filename order,\n"
        "and writes index.yaml. The <url> is the old published album URL; its HTML\n"
        "meta tags are used to fill in album title, description and author."
    )

    def __init__(self, cmd, *args):
        if len(args) != 2:
            raise InvalidArgumentsException(self, "requires exactly: <url> <local-dir>")
        self.url = args[0]
        self.path = pathlib.Path(args[1])

    async def run(self):
        path = self.path

        if not path.is_dir():
            raise CommandRuntimeException(f"{path}: not a directory")

        index_yaml = path / "index.yaml"
        if index_yaml.exists():
            raise CommandRuntimeException(
                f"{index_yaml} already exists; remove it first if you want to re-migrate"
            )

        index_md = path / "index.md"
        if not index_md.exists():
            raise CommandRuntimeException(f"{index_md}: not found")

        # --- Scan image files (sorted, same order as genviews.pl) ---
        images = sorted(
            f for f in path.iterdir()
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        if not images:
            raise CommandRuntimeException(f"{path}: no images found")
        print(f"Found {len(images)} image files")

        # --- Fetch HTML meta tags from old URL ---
        meta = self._fetch_meta(self.url)

        # --- Parse index.md ---
        md_text = index_md.read_text(encoding="utf-8")
        frontmatter, photo_blocks = self._parse_index_md(md_text)

        # Merge: frontmatter overrides scraped meta where present
        for key in ("title", "author", "og-description", "og-image", "og-image-alt"):
            if key in frontmatter:
                meta[key] = frontmatter[key]

        # Ensure mandatory meta fields exist
        meta.setdefault("title", str(path.name))
        meta.setdefault("author", "TODO")
        meta.setdefault("og-description", "TODO")
        meta.setdefault("og-image", "TODO")
        meta.setdefault("og-image-alt", "TODO")
        meta["url"] = ""
        meta["thumbnail"] = ""
        meta["access"] = ["public"]

        # --- Match photo blocks to files ---
        if len(photo_blocks) > len(images):
            raise CommandRuntimeException(
                f"index.md has {len(photo_blocks)} photo entries but only "
                f"{len(images)} image files found"
            )

        image_entries = []
        for i, img_path in enumerate(images):
            t, enc = mimetypes.guess_file_type(img_path)
            mime = f"{t};encoding={enc}" if enc else (t or "image/jpeg")
            entry = {
                "orig": img_path.name,
                "mime": mime,
                "cs": "TODO",
                "en": "TODO",
            }
            if i < len(photo_blocks):
                descs = photo_blocks[i]
                for lang, text in descs.items():
                    entry[lang] = text.strip()
            image_entries.append(entry)

        data = {
            "meta": meta,
            "images": image_entries,
            "sizes": {
                "thumbnail": "public",
                "public": {"x": 1024, "y": 1024, "quality": 0.7},
            },
        }

        with open(index_yaml, "w") as f:
            yaml.safe_dump(data, f, allow_unicode=True)

        print(f"Written {index_yaml} with {len(image_entries)} photos")

    def _fetch_meta(self, url):
        """Scrape og/meta tags from the old published album HTML."""
        meta = {}
        try:
            print(f"Fetching {url} ...")
            req = urllib.request.Request(url, headers={"User-Agent": "alb-migrate/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            # og:title → title
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html, re.I)
            if m:
                meta["title"] = m.group(1)

            # og:description → og-description
            m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html, re.I)
            if not m:
                m = re.search(r'<meta\s+name="og:description"\s+content="([^"]*)"', html, re.I)
            if m:
                meta["og-description"] = m.group(1)

            # author meta tag
            m = re.search(r'<meta\s+name="author"\s+content="([^"]*)"', html, re.I)
            if m:
                meta["author"] = m.group(1)

            # og:image → og-image (strip URL prefix, keep just filename)
            m = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', html, re.I)
            if m:
                meta["og-image"] = m.group(1).rsplit("/", 1)[-1]

            # og:image:alt → og-image-alt
            m = re.search(r'<meta\s+property="og:image:alt"\s+content="([^"]*)"', html, re.I)
            if m:
                meta["og-image-alt"] = m.group(1)

            print(f"Scraped meta: {list(meta.keys())}")
        except Exception as e:
            logger.warning(f"Could not fetch {url}: {e}; proceeding without scraped meta")

        return meta

    def _parse_index_md(self, text):
        """
        Parse old pandoc-markdown index.md.

        Returns (frontmatter_dict, photo_blocks) where photo_blocks is a list
        of dicts mapping lang -> description text.
        """
        frontmatter = {}
        photo_blocks = []

        # Strip YAML frontmatter (--- ... ---)
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if fm_match:
            try:
                frontmatter = yaml.safe_load(fm_match.group(1)) or {}
                # Pandoc uses 'title', 'author', 'description' keys
                if "description" in frontmatter and "og-description" not in frontmatter:
                    frontmatter["og-description"] = frontmatter.pop("description")
            except Exception:
                pass
            text = text[fm_match.end():]

        # Parse photo blocks: !!!  (no desc) or !! ... !!
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            # !!!  — photo with no description
            if re.match(r"^!!!$", line):
                photo_blocks.append({})
                i += 1
                continue

            # !!  — start of a described block
            if re.match(r"^!!$", line):
                descs = {}
                last_lang = None
                i += 1
                while i < len(lines):
                    inner = lines[i]
                    if re.match(r"^!!$", inner):
                        # end of block
                        i += 1
                        break
                    # !lang text
                    m = re.match(r"^!([a-z]+)\s+(.*)", inner)
                    if m:
                        last_lang = m.group(1)
                        descs[last_lang] = descs.get(last_lang, "") + m.group(2)
                        i += 1
                        continue
                    # !  continuation
                    m = re.match(r"^!\s+(.*)", inner)
                    if m and last_lang:
                        descs[last_lang] += " " + m.group(1)
                        i += 1
                        continue
                    i += 1

                photo_blocks.append(descs)
                continue

            i += 1

        return frontmatter, photo_blocks


Migrate.register()
