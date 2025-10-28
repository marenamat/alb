from aiohttp import web

import asyncio

class WebApp:
    components = []

    def __init__(self, index):
        self.index = index
        self.app = web.Application()
        for c in self.components:
            ep = c(self)
            self.app.router.add_get(ep.urlbase, ep.get)
            self.app.router.add_post(ep.urlbase, ep.post)

    @classmethod
    def register(cls, component):
        cls.components.append(component)

    async def open_browser(self, app):
        await asyncio.create_subprocess_shell("xdg-open http://[::1]:6654/")

    async def run(self):
        self.app.on_startup.append(self.open_browser)
        await web._run_app(self.app, port=6654)

class View:
    def __init__(self, app):
        self.app = app

    async def get(self, request):
        raise web.HTTPMethodNotAllowed(
                method="GET",
                allowed_methods=[],
                reason="nothing to GET here")

    async def post(self, request):
        raise web.HTTPMethodNotAllowed(
                method="POST",
                allowed_methods=[],
                reason="no POST office here")

from .MainView import MainView
from .ImageServeView import ImageServeView
