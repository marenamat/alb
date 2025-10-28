from . import WebApp, View
from aiohttp import web

import jinja2
import pathlib

class ImageServeView(View):
    urlbase = "/img/{id}"

    async def get(self, request):
        img_id = request.match_info["id"]
        fpath = self.app.index.path / img_id
        print(request, self.app.index, fpath, img_id)

        resp = web.StreamResponse()
        resp.content_length = fpath.stat().st_size
        resp.content_type = "image/jpeg" # FIXME load from index
        await resp.prepare(request)

        with open(self.app.index.path / img_id, "rb") as f:
            data = f.read()

        await resp.write(data)
        return resp

WebApp.register(ImageServeView)
