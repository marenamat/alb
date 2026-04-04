from . import Command, CommandRuntimeException, InvalidArgumentsException

import asyncio
import logging
import pathlib
import shutil

import jinja2
import yaml

logger = logging.getLogger(__name__)

# Vendor dir (Bootstrap files)
_VENDOR_DIR = pathlib.Path(__file__).parent.parent.parent / "static" / "vendor"
_TEMPLATE_DIR = pathlib.Path(__file__).parent.parent.parent / "template"


class Landing(Command):
    command = "landing"
    argdesc = "[foto-dir]"
    helptext = (
        "Generate a landing page (index.html) in the given foto directory "
        "(default: current directory). Reads albums.yaml and aggregates from subdirectories."
    )

    def __init__(self, cmd, *args):
        if len(args) == 0:
            self.foto_dir = pathlib.Path(".")
        elif len(args) == 1:
            self.foto_dir = pathlib.Path(args[0])
        else:
            raise InvalidArgumentsException(self, "takes at most one directory argument")

    async def run(self):
        foto_dir = self.foto_dir.resolve()
        if not foto_dir.is_dir():
            raise CommandRuntimeException(f"Not a directory: {foto_dir}")

        albums_yaml = foto_dir / "albums.yaml"
        if not albums_yaml.exists():
            # Aggregate from subdirectories
            await self._aggregate(foto_dir, albums_yaml)

        try:
            with open(albums_yaml) as f:
                albums_data = yaml.safe_load(f)
        except Exception as e:
            raise CommandRuntimeException(f"Failed to read {albums_yaml}: {e}") from e

        # For v1: only show albums that have 'public' in their access list.
        # If access list is absent or empty, unlist the album.
        all_albums = albums_data.get("albums", [])
        public_albums = [
            a for a in all_albums
            if "public" in a.get("access", [])
        ]

        meta = albums_data.get("meta", {
            "author": "",
            "title": "Photo albums",
            "og-description": "",
        })

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
            autoescape=jinja2.select_autoescape(["html"]),
        )
        tmpl = env.get_template("landing.html.j2")

        for lang in ["en", "cs"]:
            html = tmpl.render(albums=public_albums, meta=meta, lang=lang)
            out = foto_dir / f"index-{lang}.html"
            out.write_text(html, encoding="utf-8")
            logger.info(f"Wrote {out}")

        # Default index.html = english
        shutil.copy2(foto_dir / "index-en.html", foto_dir / "index.html")

        # Copy Bootstrap vendor files to foto_dir
        for f in _VENDOR_DIR.iterdir():
            if f.is_file():
                dest = foto_dir / f.name
                if not dest.exists():
                    shutil.copy2(f, dest)

        # Generate root Makefile if missing
        makefile = foto_dir / "Makefile"
        if not makefile.exists():
            self._write_root_makefile(makefile, all_albums)

        print(f"Landing page generated in {foto_dir} ({len(public_albums)} public albums)")

    async def _aggregate(self, foto_dir, albums_yaml):
        """
        Read index.yaml from each subdirectory and build albums.yaml.
        Only includes directories that have an index.yaml with meta.url set.
        """
        albums = []
        for sub in sorted(foto_dir.iterdir()):
            if not sub.is_dir():
                continue
            idx_file = sub / "index.yaml"
            if not idx_file.exists():
                continue
            try:
                with open(idx_file) as f:
                    idx = yaml.safe_load(f)
                meta = idx.get("meta", {})
                album = {
                    "url": meta.get("url", sub.name),
                    "thumbnail": meta.get("og-image", ""),
                    "access": meta.get("access", []),
                }
                # Collect localized title/desc
                for lang in ["cs", "en"]:
                    if f"{lang}-title" in meta or f"{lang}-desc" in meta:
                        album[lang] = {
                            "title": meta.get(f"{lang}-title", ""),
                            "desc": meta.get(f"{lang}-desc", ""),
                        }
                # Fallback: use og-description for english
                if "en" not in album and meta.get("title"):
                    album["en"] = {
                        "title": meta.get("title", ""),
                        "desc": meta.get("og-description", ""),
                    }
                albums.append(album)
            except Exception as e:
                logger.warning(f"Skipping {sub}: {e}")

        data = {
            "albums": albums,
            "meta": {
                "author": "",
                "title": "Photo albums",
                "og-description": "",
            },
        }
        with open(albums_yaml, "w") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
        logger.info(f"Generated {albums_yaml} from {len(albums)} subdirectories")

    def _write_root_makefile(self, makefile, albums):
        """Write a root Makefile that installs everything recursively."""
        album_urls = " ".join(a.get("url", "") for a in albums)
        makefile.write_text(
            f"# Generated by alb landing. Run 'alb landing' to update.\n"
            f"ALBUMS = {album_urls}\n"
            f"\n"
            f".PHONY: install landing $(ALBUMS)\n"
            f"\n"
            f"landing:\n"
            f"\talb.py landing .\n"
            f"\n"
            f"install: landing $(ALBUMS)\n"
            f"\n"
            f"$(ALBUMS):\n"
            f"\t$(MAKE) -C $@ install\n",
            encoding="utf-8",
        )
        logger.info(f"Wrote {makefile}")


Landing.register()
