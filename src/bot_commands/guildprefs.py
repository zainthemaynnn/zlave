# default
import asyncio
from functools import wraps

# external
import yaml

# self-made
from tools import commands, database

# initalization
with open("config\\default_prefs.yml") as defprefs_file:
    defprefs = yaml.safe_load(defprefs_file)["guilds"]


# decorators
# I don't even know WTF I did here with the wrappers
# https://stackoverflow.com/q/42043226/15302829
def prefsetter():
    def wrapper(screener):
        @wraps(screener)
        async def wrapped(message, client, prefname):
            """
            receives and writes input. input is processed differently per command so it decorates each.
            """

            def check(response):
                if response.author == message.author:
                    return True

            try:
                response = await client.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                return

            pref = response.content
            if pref.casefold() == "default":
                # swap to default
                pref = defprefs[prefname]["default"]
            elif not (pref := await screener(pref)):
                # check failed; restart
                pref = await wrapped(message, client, prefname)

            @database.query
            def update(conn):
                conn.execute("UPDATE guilds SET {0} = ? WHERE id = ?".format(
                    prefname), (pref, message.guild.id))
                conn.commit()
                conn.close()

            update()
            return pref
        return wrapped
    return wrapper


# response
async def guildprefs(message, client, extra_args):
    """
    modify server preferences
    """

    # running every subcommand
    subcmds = client.get_cmdlist()["guildprefs"].get_subcommands()
    for subcmd in subcmds.values():
        await subcmd.run(message, client, extra_args)


# subcommands
async def prefix(message, client, extra_args):
    """
    change the bot prefix
    """

    await message.channel.send("ENTER A NEW PREFIX OR TYPE `default`")

    @prefsetter()
    async def set_prefix(prefix):
        max_length = defprefs["prefix"]["max_length"]
        if len(prefix) > max_length:
            await message.channel.send(f"PREFIXES CAN ONLY BE UP TO {max_length} CHARACTERS")
            return None
        elif " " in prefix:
            await message.channel.send(f"NO SPACES... WHY DO YOU EVEN WANT SPACES")
            return None
        else:
            return prefix

    pref = await set_prefix(message, client, "prefix")
    await message.channel.send(f"YOUR PREFIX HAS BEEN SET TO `{pref}`")


async def autores(message, client, extra_args):
    """
    toggle automatic responses
    """

    await message.channel.send("ENTER `True` TO ENABLE OR `False` TO DISABLE AUTOMATIC REPLIES OR TYPE `default`")

    @prefsetter()
    async def set_autores(response):
        response = response.casefold()
        if response in ("f", "false"):
            return 0
        elif response in ("t", "true"):
            return 1
        else:
            await message.channel.send("WRONG ANSWER, TRY AGAIN IDIOT")
            return None

    pref = await set_autores(message, client, "auto_response")
    pref = "ENABLED" if pref == 1 else "DISABLED"
    await message.channel.send(f"AUTOMATIC RESPONSES HAVE BEEN `{pref}`")


response = commands.Command(guildprefs, {
    "prefix": commands.Command("prefix"),
    "autores": commands.Command("autores")
}, category="configuration")
