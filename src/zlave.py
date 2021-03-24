# default
import os

# external
import discord
import yaml

# self-made
from tools import database, logger_tools
from playlist import Playlist
import auto_response

# initialization
logger = logger_tools.standard_logger("INFO")
with open("config\\controls.yml") as controls_file:
    controls = yaml.safe_load(controls_file)
ROOT = os.environ["PYTHONPATH"]

# bot stuff
intents = discord.Intents.default()
intents.members = True


class zlave(discord.Client):
    """
    modified client; includes command list and playlist list
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlists = {}
        self.cmdlist = {}
        for file in os.listdir(ROOT + "\\src\\bot_commands"):
            if file.endswith(".py") and not file.startswith("__"):
                # removes .py extension
                file = file[:len(file) - 3]
                command_file = __import__(
                    "bot_commands." + file, fromlist=[""])
                self.cmdlist[file] = command_file.response

    def add_playlist(self, key):
        playlist = self.playlists[str(key)] = Playlist(self)
        return playlist

    def remove_playlist(self, key):
        del self.playlists[str(key)]

    def find_playlist(self, key):
        return self.playlists.get(str(key))

    def get_cmdlist(self):
        return self.cmdlist


client = zlave(intents=intents)


# events
@client.event
async def on_ready():
    """
    startup
    """

    logger.info(f"{client.user} is ready")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=controls["style"]["status"]))


@client.event
async def on_disconnect():
    """
    shutoff
    """

    logger.info(f"{client.user} is shutting off")


@client.event
async def on_guild_join(guild):
    """
    add server and default preferences to database
    """

    logger.info(f"joined new guild \"{guild.name}\" ({guild.id})")
    database.setup(guild.id, "guilds")
    if guild.system_channel:
        with open("config\\default_prefs.yml") as defprefs:
            prefix = yaml.safe_load(defprefs)["guilds"]["prefix"]
        await guild.system_channel.send("WHAT'S UP. MY DEFAULT PREFIX IS `{0}` FOLLOWED BY A SPACE. TRY `{0} help`".format(prefix))


@client.event
async def on_guild_remove(guild):
    """
    remove server from database so it doesn't break
    """

    logger.info(f"removed from guild \"{guild.name}\" ({guild.id})")
    database.db_remove(("id", guild.id), "guilds")


@client.event
async def on_message(message):
    """
    los messages, also handles automatic responses
    """

    # don't reply to self or other bots
    if message.author.bot:
        return

    # sentence
    words = message.content.split(" ")

    # getting the prefix
    cmd_prefix = database.db_get(
        ("id", message.guild.id), "guilds", "prefix")

    # for commands. arg 0 is the prefix, arg 1 is the command, the rest subcommands/input
    if words[0].casefold() == cmd_prefix.casefold() and len(words) > 1:
        cmdname = words[1].casefold()
        if (cmd := client.get_cmdlist().get(cmdname)):
            logger.debug(
                f"running command {cmdname} for guild {message.guild.name} ({message.guild.id})")
            await cmd.run(message, client, words[2:])
        else:
            await message.channel.send(f"INSTRUCTIONS UNCLEAR. I MAY BE STUPID. PLOX ATTEMPT USAGE OF `{cmd_prefix} help`")

    # hardcode for the lulz
    elif words[-1].casefold() == "do":
        await message.channel.send("YOUR MOM LOL")
    elif message.mention_everyone:
        await message.channel.send("LMAO NICE ONE ")

    # passive responses
    elif database.db_get(("id", message.guild.id), "guilds", "auto_response"):
        keyword, responses = auto_response.search(words)
        if keyword and responses:
            for response in responses:
                await auto_response.sauce_msg(response, keyword, message)
            return

    # ponged
    else:
        str_id = str(client.user.id)
        if words[0] in (f"<@{str_id}>", f"<@!{str_id}>"):
            if len(words) == 1:
                await message.channel.send("WHAT'S UP. MY CURRENT PREFIX IS `{0}` FOLLOWED BY A SPACE. TRY `{0} help`".format(cmd_prefix))
            else:
                await message.channel.send("SCREW OFF")

# start bot
try:
    client.run(os.environ["zlave_token"])
except Exception as e:
    logger.critical(
        f"client couldn't start lmao; {e}")
