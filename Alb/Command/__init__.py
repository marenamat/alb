class CommandException(Exception):
    pass

class CommandRuntimeException(Exception):
    pass

class UnknownCommandException(CommandException):
    def __init__(self, cmd):
        self.cmd = cmd
        super().__init__(f"Unknown command: {cmd}")

class NoCommandException(CommandException):
    def __init__(self):
        super().__init__("No command")

class InvalidCommandException(CommandException):
    def __init__(self, cls):
        super().__init__(f"Command {cls} does not implement mandatory items")

class InvalidArgumentsException(CommandException):
    def __init__(self, cls, msg):
        super().__init__(f"Command '{cls.command}' {msg}")

class Command:
    kw = {}

    def __new__(cls, *args, **kwargs):
        if cls != Command:
            return super(Command, cls).__new__(cls)

        if len(args) == 0:
            raise NoCommandException()

        cmd = args[0]

        if cmd not in cls.kw:
            raise UnknownCommandException(cmd)

        return cls.kw[cmd].__new__(cls.kw[cmd], *args[1:], **kwargs)

    def __init__(self, cmd, *args):
        self.cmd = cmd
        self.args = args

    @classmethod
    def register(cls):
        try:
            cls.run(None).close() # This should create and delete an empty coroutine
            Command.kw[cls.command] = cls
        except Exception as e:
            raise InvalidCommandException(cls) from e

# Import the classes here to modify Command
from .Scan import Scan
from .Init import Init
