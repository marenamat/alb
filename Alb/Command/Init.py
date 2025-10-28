from . import Command, CommandRuntimeException, InvalidArgumentsException
from ..Index import Index, IndexException

import asyncio
import logging
import pathlib

logger = logging.getLogger(__name__)

class Init(Command):
    command = "init"
    argdesc = "[dirs]"
    helptext = "Initialize an index in the given directories. If not given, do it in the current directory. Reinitialization is not well tested; backup your original index.yaml beforehand."

    def __init__(self, cmd, *args):
        if len(args) == 0:
            self.dirs = [ pathlib.Path(".") ]
        else:
            self.dirs = [ pathlib.Path(p) for p in args ]

    async def run(self):
        try:
            indices = [ Index(p) for p in self.dirs ]
            await asyncio.gather(*[ i.new() for i in indices ])
        except IndexException as e:
            raise CommandRuntimeException(f"Failed to initialize index in {e.path}: {''.join(e.args)}") from e

Init.register()
