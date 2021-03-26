# default
from functools import wraps

# external
import yaml

# initialization
with open("config\\secrets.yml") as file:
    permissions = yaml.safe_load(file)["permissions"]


# restrictions
def operator_only(func):
    """
    only the bot owner can use this command
    """

    @wraps(func)
    async def wrapper(message, *args, **kwargs):
        if message.author.id == permissions["owner"]:
            await func(message, *args, **kwargs)
        else:
            await message.channel.send("ONLY MY BOSS CAN USE THIS COMMAND, PEASANT")
    return wrapper


def premium_only(func):
    """
    only premium users (your friends probably), like other admins, can use this command
    """

    @wraps(func)
    async def wrapper(message, *args, **kwargs):
        if message.author.id in permissions["premium"] or message.author.id == permissions["owner"]:
            await func(message, *args, **kwargs)
        else:
            await message.channel.send("YOU MUST ASK MY MASTER FOR ACCESS TO THIS COMMAND LOL GOOD LUCK")
    return wrapper


def admin_only(func):
    """
    only the server admins can use this command
    """

    @wraps(func)
    async def wrapper(message, *args, **kwargs):
        if message.author.guild_permissions.administrator:
            await func(message, *args, **kwargs)
        else:
            await message.channel.send("YOU ARE NOT AN ADMIN. WHO NEEDS RIGHTS ANYWAYS")
    return wrapper


def voice_only(func):
    """
    only users in voice chat can use this command
    """

    @wraps(func)
    async def wrapper(message, *args, **kwargs):
        if message.author.voice:
            await func(message, *args, **kwargs)
        else:
            await message.channel.send("I CANNOT PLAY ANYTHING IF YOU ARE NOT IN A VOICE CHANNEL, PLEASE USE YOUR HEAD SIR AND/OR MA'AM")
    return wrapper


# la classe de commandeu
# probably means something in french I'm sure
class Command:
    """
    commands are chained into subcommands separated by spaces
    """

    def __init__(self, func, subcommands={}, category=None):
        def prepare(func):
            """
            allows chaining of subcommands
            """

            @wraps(func)
            def wrapper(message, client, extra_args, *args, **kwargs):
                if extra_args and self.subcommands and (subcommand := self.subcommands.get(extra_args[0])):
                    # run the subcommand with its own name trimmed off the arguments
                    return subcommand.run(message, client, extra_args[1:], *args, **kwargs)
                else:
                    return func(message, client, extra_args, *args, **kwargs)
            return wrapper

        self.run = prepare(func)
        self.subcommands = subcommands
        self.description = func.__doc__
        self.category = category

    def get_subcommands(self):
        return self.subcommands
