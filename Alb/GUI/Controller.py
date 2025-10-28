from . import WebApp, View
from aiohttp import web

import jinja2
import pathlib

class Controller(View):
    urlbase = "/controller/"
    
    async def get(self, request):
        print("BAGR")
        ws = web.WebSocketResponse()
        await ws.prepare(request)


        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

WebApp.register(Controller)
