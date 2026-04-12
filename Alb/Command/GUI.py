from . import Command, CommandRuntimeException, InvalidArgumentsException
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
            self.dirs = [ pathlib.Path(p) for p in args ]

    async def run(self):
        try:
            indices = [ Index(p) for p in self.dirs ]
            # Auto-initialise any directory that has no index.yaml yet
            for idx in indices:
                idx_file = idx.path / "index.yaml"
                if not idx_file.exists():
                    logger.info(f"No index.yaml in {idx.path}, initialising...")
                    await idx.new()
            w = [ WebApp(idx) for idx in indices ]
            await asyncio.gather(*[ a.run() for a in w ])
        except IndexException as e:
            raise CommandRuntimeException(f"Failed to open GUI for {e.path}: {''.join(e.args)}") from e

GUI.register()
