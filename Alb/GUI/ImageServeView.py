from . import WebApp, View
from aiohttp import web

import jinja2
import pathlib

class ImageServeView(View):
    urlbase = "/img/{size}-{id}"

    async def get(self, request):
        img_id = request.match_info["id"]
        img_size = request.match_info["size"]
        try:
            img_info = self.app.index.data["images"][int(img_id) - 1]
        except IndexError as e:
            logger.info(f"Bad index {img_id}", e)
            raise web.HTTPNotFound() from e

        if img_size == "orig":
            fpath = self.app.index.path / img_info["orig"]
        else:
            try:
                sz = self.app.index.data["sizes"][img_size]
                if type(sz) is str and sz in self.app.index.data["sizes"][img_size]:
                    raise web.HTTPTemporaryRedirect(location=f"/img/{sz}-{img_id}")

                fpath = self.app.index.path / "www" / img_size / img_info["orig"]
            except IndexError as e:
                logger.info(f"Bad size {img_size}", e)
                raise web.HTTPNotFound() from e

        try:
            bytesize = fpath.stat().st_size
        except FileNotFoundError as e:
            if img_size == "orig":
                raise web.HTTPNotFound() from e
            else:
                raise web.HTTPTemporaryRedirect(location=f"/img/orig-{img_id}") from e

        resp = web.StreamResponse()
        resp.content_length = bytesize
        resp.content_type = img_info["mime"]
        try:
            await resp.prepare(request)

            with open(fpath, "rb") as f:
                data = f.read()

            await resp.write(data)
        except ConnectionError:
            pass

        return resp

WebApp.register(ImageServeView)
