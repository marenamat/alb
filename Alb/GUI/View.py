class View:
    def __init__(self, app):
        self.app = app

    async def get(self, request):
        raise web.HTTPMethodNotAllowed(reason="nothing to GET here")

    async def post(self, request):
        raise web.HTTPMethodNotAllowed(reason="no POST office here")
