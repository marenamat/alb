from . import AlbException

import logging
import mimetypes
import yaml

logger = logging.getLogger(__name__)

class IndexException(AlbException):
    def __init__(self, path, *args):
        self.path = path
        super().__init__(*args)

class IndexNotFoundException(IndexException):
    def __init__(self, path):
        super().__init__(path, "not found")

class Index:
    def __init__(self, path):
        self.path = path
        self.require(self.path.is_dir(), "not a directory")

    def require(self, test: bool, info: str):
        if not test:
            self.bad(info)

    def bad(self, info: str):
        raise IndexException(self.path, info)

    def __getattr__(self, attr):
        return {
                "data": self.load,
                }[attr]()

    def load(self):
        try:
            fp = self.path / 'index.yaml'
            logger.debug(f"Loading index from {fp}")
            with open(fp, "r") as f:
                self.data = yaml.safe_load(f)
            self.require("images" in self.data, "needs images section")
            self.require("meta" in self.data, "needs meta section")
        except FileNotFoundError as e:
            raise IndexNotFoundException(self.path) from e
        except Exception as e:
            raise IndexException(self.path, "malformed index") from e

        return self.data

    async def store(self):
        try:
            fp = self.path / 'index.yaml'
            logger.debug(f"Storing index to {fp}")
            with open(fp, "w") as f:
                yaml.safe_dump(self.data, f)
        finally:
            pass

    async def new(self):
        # Check existing index
        try:
            await self.load()
        except IndexNotFoundException:
            logger.debug(f"Index not found in {self.path}")
            self.data = {
                    "images": [],
                    "meta": {
                        "title": str(self.path),
                        "author": "TODO",
                        "og-description": "TODO",
                        "og-image": "TODO",
                        "og-image-alt": "TODO",
                        }
                    }

        # Scan directory
        logger.debug(f"Scanning directory {self.path} for images")
        found = {}
        for f in self.path.iterdir():
            if not f.is_file():
                logger.info(f"Ignoring {f}: not a file")
                continue

            t, e = mimetypes.guess_file_type(f)
            logger.debug(f"Found file {f}, type {t}, encoding {e}")

            if not t.startswith("image/"):
                logger.info(f"Ignoring {f}: detected as {t};encoding={e}")
                continue

            found[f] = f"{t};encoding={e}" if e is not None else t

        for img in self.data["images"]:
            if self.path / img["orig"] in found:
                del found[self.path / img["orig"]]
            else:
                logger.warning(f"Found description for {self.path / img['orig']} which does not exist")
            
        for f in found:
            self.data["images"].append({
                "orig": str(f.relative_to(self.path)),
                "mime": found[f],
                "cs": "TODO",
                "en": "TODO",
                })

        await self.store()
