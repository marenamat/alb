from . import Command, InvalidArgumentsException

import logging
import pathlib

logger = logging.getLogger(__name__)

class Scan(Command):
    command = "scan"
    helptext = "Walk subdirectories and tell if there is an index by the new means, by Maria's old Perl scripts, or simply nothing. Does not check the index consistency."

    def __init__(self, cmd, *args):
        if len(args) != 0:
            raise InvalidArgumentsException(self, "does not take any arguments")

    async def run(self):
        localdir = pathlib.Path(".")
        logger.debug(f"Scanning {localdir} which is {localdir.absolute()}")
        for f in localdir.iterdir():
            if not f.is_dir():
                logger.debug(f"{f} is not a directory")
                continue

            if (f / "index.yaml").exists():
                print(f"[   OK   ]\t{f}")
            elif (f / "index.md").exists():
                print(f"[ LEGACY ]\t{f}")
            else:
                print(f"[  NONE  ]\t{f}")

Scan.register()
