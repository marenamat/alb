from . import AlbException
from .Resizer import Resizer

import asyncio
import logging
import pathlib
import shutil

import jinja2

logger = logging.getLogger(__name__)

# Directory where vendor static files live (relative to this file)
_VENDOR_DIR = pathlib.Path(__file__).parent.parent / "static" / "vendor"
_TEMPLATE_DIR = pathlib.Path(__file__).parent.parent / "template"


class GeneratorException(AlbException):
    pass


class Generator:
    def __init__(self, index):
        self.index = index

    def _jinja_env(self):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
            autoescape=jinja2.select_autoescape(["html"]),
        )

    async def generate(self):
        """Generate the static website into <album>/views/."""
        views = self.index.path / "views"
        views.mkdir(exist_ok=True)

        # Copy vendor files (Bootstrap)
        for f in _VENDOR_DIR.iterdir():
            if f.is_file():
                dest = views / f.name
                if not dest.exists() or f.stat().st_mtime > dest.stat().st_mtime:
                    shutil.copy2(f, dest)
                    logger.debug(f"Copied vendor file {f.name}")

        # Create thumbnail and public directories
        thumb_dir = views / "thumbnail"
        pub_dir = views / "public"
        thumb_dir.mkdir(exist_ok=True)
        pub_dir.mkdir(exist_ok=True)

        # Resize images
        sizes = self.index.data.get("sizes", {})
        thumb_size_key = sizes.get("thumbnail", "thumbnail")

        # Resolve thumbnail size config
        thumb_cfg = sizes.get(thumb_size_key, {})
        if isinstance(thumb_cfg, str):
            # It's an alias, resolve it
            thumb_cfg = sizes.get(thumb_cfg, {})

        thumb_resizer = Resizer(
            x=thumb_cfg.get("x", 400),
            y=thumb_cfg.get("y", 400),
            quality=thumb_cfg.get("quality", 0.7),
        )

        # Full-size (public) resizer - use the "public" size from config
        pub_cfg = sizes.get("public", {})
        if isinstance(pub_cfg, str):
            pub_cfg = sizes.get(pub_cfg, {})
        pub_resizer = Resizer(
            x=pub_cfg.get("x", 1024),
            y=pub_cfg.get("y", 1024),
            quality=pub_cfg.get("quality", 0.85),
        )

        visible_images = []
        resize_tasks = []

        for img in self.index.data["images"]:
            # Skip deleted or hidden images
            if img.get("deleted") or img.get("hidden"):
                continue
            visible_images.append(img)

            src = self.index.path / img["orig"]

            # Generate thumbnail
            th_dest = thumb_dir / img["orig"]
            if not th_dest.exists():
                resize_tasks.append(thumb_resizer.process(str(src), str(th_dest)))

            # Generate public (full-size) image
            pub_dest = pub_dir / img["orig"]
            if not pub_dest.exists():
                resize_tasks.append(pub_resizer.process(str(src), str(pub_dest)))

        if resize_tasks:
            logger.info(f"Resizing {len(resize_tasks)} images...")
            await asyncio.gather(*resize_tasks)

        # Render templates
        env = self._jinja_env()
        lang = self.index.data.get("meta", {}).get("lang", "en")

        # Build index of visible image positions (for prev/next)
        visible_ids = [
            i for i, img in enumerate(self.index.data["images"])
            if not img.get("deleted") and not img.get("hidden")
        ]

        # Build list of (img_id, img) for visible images to pass to templates
        visible_list = [
            {"img_id": img_id, **self.index.data["images"][img_id]}
            for img_id in visible_ids
        ]

        # Render album index page
        idx_tmpl = env.get_template("album-index.html.j2")
        idx_html = idx_tmpl.render(
            images=visible_list,
            meta=self.index.data["meta"],
            lang=lang,
        )
        (views / "index.html").write_text(idx_html, encoding="utf-8")
        logger.info("Wrote views/index.html")

        # Render single photo pages inside views/photos/
        photos_dir = views / "photos"
        photos_dir.mkdir(exist_ok=True)

        single_tmpl = env.get_template("album-single.html.j2")

        for pos, img_id in enumerate(visible_ids):
            img = self.index.data["images"][img_id]
            prev_id = visible_ids[pos - 1] if pos > 0 else None
            next_id = visible_ids[pos + 1] if pos < len(visible_ids) - 1 else None

            html = single_tmpl.render(
                img=img,
                img_id=img_id,
                total=len(visible_ids),
                prev_id=prev_id,
                next_id=next_id,
                meta=self.index.data["meta"],
                lang=lang,
            )
            (photos_dir / f"{img_id}.html").write_text(html, encoding="utf-8")

        logger.info(f"Wrote {len(visible_ids)} single photo pages")

        # Generate Makefile if it doesn't exist
        makefile = self.index.path / "Makefile"
        if not makefile.exists():
            mk_tmpl = env.get_template("Makefile.j2")
            mk_text = mk_tmpl.render(
                album_url=self.index.data.get("meta", {}).get("url", ""),
                rsync_dest=self.index.data.get("meta", {}).get("rsync-dest", ""),
            )
            makefile.write_text(mk_text, encoding="utf-8")
            logger.info("Wrote Makefile")

        return {
            "visible": len(visible_ids),
            "views_dir": str(views),
        }
