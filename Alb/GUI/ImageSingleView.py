from . import WebApp, View
from aiohttp import web

import jinja2
import pathlib

class ImageSingleView(View):
    urlbase = "/single-{id}"

    async def get(self, request):
        img_id = request.match_info["id"]

        td = pathlib.Path(__file__).absolute().parent.parent.parent / "template"
        je = jinja2.Environment(loader=jinja2.FileSystemLoader(td))
        te = je.get_template("single-gui.html.j2")

        rtext = te.render(
                **self.app.index.data,
                app=self.app,
                imgurl=f"/img/orig-{img_id}",
                ).encode("utf8")

        resp = web.StreamResponse()
        resp.content_length = len(rtext)
        resp.content_type = "text/html"
        await resp.prepare(request)
        await resp.write(rtext)
        return resp

WebApp.register(ImageSingleView)
