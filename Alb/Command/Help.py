from . import Command, InvalidArgumentsException, ArgvZero

import errno
import logging
import os
import pathlib

logger = logging.getLogger(__name__)

class Help(Command):
    command = "help"
    helptext = "Show this help"

    async def run(self):
        items = []

        for cmd in Command.order:
            name = f"{ArgvZero} {cmd.command}"
            try:
                name += " " + cmd.argdesc
            except AttributeError:
                pass

            items.append((name, cmd.helptext))

        maxleft = max([ len(l[0]) for l in items ])

        try:
            termsize = os.get_terminal_size()
        except OSError as e:
            if e.errno == errno.ENOTTY:
                return self.plain(items)

            raise CommandRuntimeException("Something went wrong when getting terminal size") from e

        leftindent = 8
        colspace = 3
        rightindent = 4

        rightcol = termsize.columns - (leftindent + maxleft + colspace + rightindent)
        if rightcol < 50:
            return self.plain(items)

        if rightcol > 120:
            rightcol = 120

        print("\n    ", end="")
        self.header()
        print()

        for line in items:
            left = " " * leftindent + line[0] + " " * (maxleft - len(line[0]) + colspace)
            right = line[1].split(" ")
            curr = ""
            while len(right) > 0:
                n = curr + " " + right[0]
                if len(n) > rightcol:
                    print(left + curr)
                    left = " " * (leftindent + maxleft + colspace + 1)
                    curr = right[0]
                else:
                    curr = n

                right = right[1:]

            print(left + curr)
            print()

    def header(self):
        print(f"This is Alb, a photo album generator. It has these basic commands:")

    def plain(self):
        self.header()
        for line in items:
            print()
            print(line[0])
            print(line[1])

Help.register()
