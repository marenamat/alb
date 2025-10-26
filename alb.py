#!/usr/bin/python3

import Alb

import asyncio
import jinja2
import logging
import sys
import yaml

logger = logging.getLogger("alb.py")

if __name__ == "__main__":
    # Extract verbosity
    eoa = False
    verbosity = 0
    args = []
    for arg in sys.argv[1:]:
        if arg == "-":
            eoa = True

        if not eoa and arg[0] == "-" and arg[1] != "-":
            v = arg.split("v")
            verbosity += len(v) - 1
            arg = "".join(v)
            if arg == "-":
                continue

        args.append(arg)

    logging.basicConfig(stream=sys.stderr, level={
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
        }[verbosity if verbosity < 3 else 3])
    logger.debug(f"Called command {args[0]} with arguments {args[1:]}, verbosity {verbosity}.")
    logger.debug(f"Original command-line: sys.argv[1:]")
    
    try:
        asyncio.run(Alb.Command(*args).run())
    except Alb.CommandException as e:
        print(e, file=sys.stderr)

        if verbosity > 2:
            raise e

        exit(2)
    except Alb.CommandRuntimeException as e:
        print(e, file=sys.stderr)
        if verbosity > 2:
            raise e

        exit(1)
