from . import Command, InvalidArgumentsException
from ..GUI import WebApp
from ..Index import Index, IndexException

import asyncio
import logging
import pathlib

logger = logging.getLogger(__name__)

class GUI(Command):
    command = "gui"
    argdesc = "[dirs]"
    helptext = "Run the GUI for the given/current directories in your browser. Currently only one dir supported"

    def __init__(self, cmd, *args):
        if len(args) == 0:
            self.dirs = [ pathlib.Path(".") ]
        else:
            self.dirs = [ Pathlib.Path(p) for p in args ]

    async def run(self):
        try:
            w = [ WebApp(Index(p)) for p in self.dirs ]
            await asyncio.gather(*[ a.run() for a in w ])
        except IndexException as e:
            raise CommandRuntimeException("Failed to open GUI for {e.path}: {''.join(e.args)}") from e

GUI.register()
