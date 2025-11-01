from aiohttp import web

import asyncio
import errno
import random

class WebApp:
    components = []

    def __init__(self, index):
        self.index = index
        self.app = web.Application()
        for c in self.components:
            ep = c(self)
            self.app.router.add_get(ep.urlbase, ep.get)
            self.app.router.add_post(ep.urlbase, ep.post)
        self.app.on_startup.append(self.open_browser)

    @classmethod
    def register(cls, component):
        cls.components.append(component)

    async def open_browser(self, app):
        await asyncio.create_subprocess_exec("xdg-open", self.url)

    async def run(self):
        self.port = random.randrange(1025, 32768)
        self.host = "[::1]:" + str(self.port)
#        self.host = "127.0.0.1:" + str(self.port)
        self.url = "http://" + self.host + "/"
        try:
            await web._run_app(self.app, port=self.port)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return await self.run()

            raise e

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
from .ImageSingleView import ImageSingleView

from .Controller import Controller
