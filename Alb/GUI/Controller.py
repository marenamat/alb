from . import WebApp, View
from aiohttp import web, WSMsgType as msgtype

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
                    await ws.send_str("bad request!" + msg.data["_"])
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
        kk = path.split(".")
        ipos = self.app.index.data
        while len(kk) > 1:
            ipos = ipos[kk[0]]
            kk = kk[1:]
        ipos[kk[0]] = value

        await self.app.index.store()
        return self.app.index.data

Controller.register(Update)

WebApp.register(Controller)
