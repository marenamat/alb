from . import WebApp, View
from aiohttp import web, WSMsgType as msgtype
from ..Generator import Generator

import asyncio
import jinja2
import json
import logging
import pathlib

logger = logging.getLogger(__name__)

class Controller(View):
    urlbase = "/controller/"

    commands = {}

    @classmethod
    def register(cls, command):
        assert(command.name not in cls.commands)
        cls.commands[command.name] = command
    
    async def get(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == msgtype.TEXT:
                logger.debug(f"Got message: {msg.data}")
                try:
                    data = json.loads(msg.data)
                    cmd = data["_"]
                    del data["_"]
                    await ws.send_str(json.dumps(await self.commands[cmd](self.app).run(**data)))
                except KeyError:
                    await ws.send_str("bad request!" + msg.data)
            elif msg.type == msgtype.ERROR:
                logger.warn('ws connection closed with exception %s' %
                      ws.exception())

        logger.info('websocket connection closed')

        return ws

class CC:
    def __init__(self, app):
        self.app = app

    async def run(self):
        return {}

class Index(CC):
    name = "index"
    async def run(self):
        return self.app.index.data

Controller.register(Index)

class Update(CC):
    name = "update"
    async def run(self, path, value):
        ipos = self.app.index.data
        while len(path) > 1:
            ipos = ipos[path[0]]
            path = path[1:]
        ipos[path[0]] = value

        await self.app.index.store()
        return self.app.index.data

Controller.register(Update)

class Gimp(CC):
    name = "gimp"

    async def run(self, id):
        img = self.app.index.data["images"][id]
        orig_path = self.app.index.path / img["orig"]
        logger.info(f"Opening GIMP for image {id}: {orig_path}")

        # Launch GIMP (don't await - let it run in background)
        proc = await asyncio.create_subprocess_exec("gimp", str(orig_path))

        # Watch directory for new files derived from this image (in background)
        asyncio.create_task(self._watch_for_gimp_output(id, orig_path, proc))
        return {}

    async def _watch_for_gimp_output(self, img_id, orig_path, proc):
        """
        Poll the album directory for new files that look like GIMP-modified
        versions of orig_path (e.g. photo-orez.jpg, photo-rot.jpg).
        When found, mark the original as hidden in the index.
        """
        # Stem without extension, e.g. "IMG_1234"
        stem = orig_path.stem
        suffix = orig_path.suffix.lower()
        album_dir = orig_path.parent

        # Collect files present before GIMP starts
        before = set(album_dir.iterdir())

        # Poll every 2 seconds while GIMP is running (max 2 hours)
        for _ in range(3600):
            await asyncio.sleep(2)
            after = set(album_dir.iterdir())
            new_files = after - before

            for f in new_files:
                # Match <stem>-<anything>.<same-ext>
                if (f.stem.startswith(stem + "-")
                        and f.suffix.lower() == suffix
                        and f.is_file()):
                    logger.info(f"GIMP output detected: {f.name}; hiding original {orig_path.name}")
                    # Mark original as hidden
                    self.app.index.data["images"][img_id]["hidden"] = True
                    await self.app.index.store()
                    # Done - stop watching
                    return

            if proc.returncode is not None:
                # GIMP exited; do a final check then stop
                await asyncio.sleep(1)
                after = set(album_dir.iterdir())
                new_files = after - before
                for f in new_files:
                    if (f.stem.startswith(stem + "-")
                            and f.suffix.lower() == suffix
                            and f.is_file()):
                        logger.info(f"GIMP output detected on exit: {f.name}; hiding original {orig_path.name}")
                        self.app.index.data["images"][img_id]["hidden"] = True
                        await self.app.index.store()
                return

        logger.warning(f"GIMP watcher timed out for {orig_path.name}")


Controller.register(Gimp)

class ToggleDelete(CC):
    # Mark or unmark a photo for omission (does not delete the file)
    name = "toggle_delete"
    async def run(self, id):
        img = self.app.index.data["images"][id]
        img["deleted"] = not img.get("deleted", False)
        await self.app.index.store()
        return self.app.index.data

Controller.register(ToggleDelete)


class GenerateAlbum(CC):
    # Generate static website in views/
    name = "generate"
    async def run(self):
        gen = Generator(self.app.index)
        result = await gen.generate()
        return {"ok": True, "visible": result["visible"], "views_dir": result["views_dir"]}

Controller.register(GenerateAlbum)

WebApp.register(Controller)
