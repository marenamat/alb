from . import Command, CommandRuntimeException, InvalidArgumentsException
from ..Index import Index, IndexException
from ..Generator import Generator

import asyncio
import logging
import pathlib

logger = logging.getLogger(__name__)


class Generate(Command):
    command = "generate"
    argdesc = "[dirs]"
    helptext = "Generate static website in views/ for the given/current album directories."

    def __init__(self, cmd, *args):
        if len(args) == 0:
            self.dirs = [pathlib.Path(".")]
        else:
            self.dirs = [pathlib.Path(p) for p in args]

    async def run(self):
        try:
            for d in self.dirs:
                idx = Index(d)
                gen = Generator(idx)
                result = await gen.generate()
                print(f"{d}: generated {result['visible']} photos -> {result['views_dir']}")
        except IndexException as e:
            raise CommandRuntimeException(f"Failed to generate for {e.path}: {' '.join(e.args)}") from e


Generate.register()
