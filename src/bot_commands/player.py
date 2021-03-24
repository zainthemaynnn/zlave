# default
import urllib.request
import asyncio

# external
import yaml
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

# self-made
from tools import commands, logger_tools, utils

# initialization
with open("config\\controls.yml") as controls_file:
    music_controls = yaml.safe_load(controls_file)["music"]
logger = logger_tools.standard_logger()


# functions
async def get_voice_client(message, client):
    """
    gets the voice client for the guild. kind of like an sql query actually.
    """

    voice_client = [
        voice for voice in client.voice_clients if voice.guild.id == message.guild.id]
    if voice_client:
        return voice_client[0]
    else:
        await message.channel.send("I AM NOT IN A VOICE CHANNEL, IMBECILE")
        return None


async def get_playlist(message, client):
    """
    gets playlist for guild
    """
    playlist = client.find_playlist(message.guild.id)
    if not playlist:
        await message.channel.send("THERE IS NOTHING PLAYING")
    return playlist


# response
@commands.voice_only
async def player(message, client, extra_args):
    """
    play a song from a youtube url. my own playlist by default. it downloads and streams from my computer so it takes a long time and the quality is potato. don't say I didn't warn you.
    """

    if not extra_args:
        await message.channel.send("URL PLOX???")
        return
    else:
        query = extra_args[0]

    voice_channel = message.author.voice.channel
    voice_client = [
        voice for voice in client.voice_clients if voice.guild.id == message.guild.id]
    try:
        if voice_client:
            voice_client = voice_client[0]
            if not voice_client.channel == voice_channel:
                await voice_client.move_to(voice_channel)
                await message.channel.send("I AM SWITCHING VOICE CHANNELS SEE YA")
        else:
            voice_client = await voice_channel.connect()
    except Exception as e:
        logger.warning(f"could not connect to voice channel: {e}")
        await message.channel.send("I WAS UNABLE TO CONNECT TO VOICE; MY LOUD CROATIAN NEIGHBORS PREVENT ME FROM SPEAKING")
        return

    async def get_meta(query):
        YTDL_OPTS = {
            "format": "bestaudio/best",
            "noplaylist": True
        }
        executor = utils.MyExecutor()

        with YoutubeDL(YTDL_OPTS) as ytdl:
            # took so long to figure how to stream from online... and all it took was putting in the url. cute.
            try:
                urllib.request.urlopen(query)

            except ValueError:
                # not a url; search
                await message.channel.send(f"SEARCHING FOR `{query}`")
                if (entries := await executor(lambda: ytdl.extract_info(f"ytsearch:{query}", download=False)["entries"])):
                    return entries[0]
                else:
                    await message.channel.send(f"THERE ARE NO RESULTS FOR `{query}`")

            else:
                try:
                    # simply get url meta
                    await message.channel.send("PLOX STANDBY")
                    return await executor(lambda: ytdl.extract_info(query, download=False))

                except DownloadError:
                    # probably not a yt url or inaccessible
                    await message.channel.send("THIS IS NOT A VALID URL")

            # failed
            return None

    if not (meta := await get_meta(query)):
        return

    title = meta["title"]
    logger.debug("youtube meta downloaded")

    if not (playlist := client.find_playlist(message.guild.id)):
        playlist = client.add_playlist(message.guild.id)

    def video_data(video_meta):
        """
        selects the metadata from a video to be stored
        """

        return {
            "title": video_meta["title"],
            "url": video_meta["url"],
            "duration": video_meta["duration"],
            "uploader": video_meta["uploader"]
        }

    max_length = music_controls["playlist_length"]
    # playlist
    if "entries" in meta:
        await message.channel.send(f"QUEUEING PLAYLIST `{title}`")
        for video_meta in meta["entries"]:
            if not playlist.enqueue(video_data(video_meta)):
                await message.channel.send(f"I HAVE A MAXIMUM PLAYLIST SIZE OF `{max_length}` VIDEOS")
                break
    # video
    else:
        await message.channel.send(f"QUEUEING VIDEO `{title}`")
        if not playlist.enqueue(video_data(meta)):
            await message.channel.send(f"I HAVE A MAXIMUM PLAYLIST SIZE OF `{max_length}` VIDEOS")
            return

    await playlist.run(message.channel, voice_client)


# subcommands
async def loop(message, client, extra_args):
    """
    loops or unloops playlist
    """

    playlist = await get_playlist(message, client)
    if not playlist:
        return

    playlist.toggle_mode()
    if playlist.is_looping():
        await message.channel.send("LOOPED. OH, GOD, THIS PLAYLIST IS GARBAGE")
    else:
        await message.channel.send("UNLOOPED. THANK GOD")


async def move_to(message, client, extra_args):
    """
    switches song to spot on playlist
    """

    playlist = await get_playlist(message, client)
    if not playlist:
        return

    if extra_args and extra_args[0].isnumeric():
        track_number = int(extra_args[0]) - 1
        if 0 <= track_number < len(playlist.get_queue()):
            playlist.set_track_number(track_number)
            playlist.play()
            await message.channel.send(f"SWAPPED TO SONG NUMBER {track_number + 1}")
            return
    # if any checks failed
    await message.channel.send("EXCUSE ME, HOW THE HELL AM I SUPPOSED TO MOVE THERE")


async def pause(message, client, extra_args):
    """
    pauses playlist
    """

    voice_client = await get_voice_client(message, client)
    if not voice_client:
        return

    if not voice_client.is_paused():
        voice_client.pause()
        await message.channel.send("PAUSED")
    else:
        await message.channel.send("I AM ALREADY PAUSED")


async def queue(message, client, extra_args):
    """
    displays queued songs
    """

    playlist = await get_playlist(message, client)
    if not playlist:
        return

    queue = playlist.get_queue()
    if not queue:
        await message.channel.send("PLAYLIST IS EMPTY, YOU CAN HAVE A HAMBURGER WRAPPER THOUGH")
        return

    @utils.paginated_embeds
    def populate(embed, track, track_number):
        """
        add tracks to embed pages
        """

        track_number += 1
        embed.add_field(name="{0}. {1}".format(track_number, track["title"]), value="{0} • {1}".format(
            utils.to_minutes(track["duration"]), track["uploader"]), inline=False)

    page = 0
    if extra_args and extra_args[0].isnumeric():
        page = extra_args[0]

    title = "TRACKLIST" if not playlist.is_looping() else "TRACKLIST (LOOPING)"
    track_embeds = populate(title, queue)
    await utils.sauce_pages(track_embeds, message, client, page)


async def remove(message, client, extra_args):
    """
    removes a song, the one you're on by default
    """

    playlist = await get_playlist(message, client)
    if not playlist:
        return

    track_number = playlist.get_track_number()
    if extra_args and extra_args[0].isnumeric():
        track_number = int(extra_args[0]) - 1

    if playlist.remove(track_number):
        await message.channel.send(f"DELETED SONG NUMBER {track_number + 1}")
    else:
        await message.channel.send("THAT IS NOT A SONG NUMBER YOU GOOD?")


async def resume(message, client, extra_args):
    """
    unpauses playlist
    """

    voice_client = await get_voice_client(message, client)
    if not voice_client:
        return

    if voice_client.is_paused():
        voice_client.resume()
        await message.channel.send("RESUMED")
    else:
        await message.channel.send("I AM ALREADY PLAYING")


async def skip(message, client, extra_args):
    """
    skips any number of songs, one by default
    """

    playlist = await get_playlist(message, client)
    if not playlist:
        return

    skip_count = 1
    if extra_args and extra_args[0].isnumeric():
        skip_count = int(extra_args[0])

    playlist.set_track_number(playlist.get_track_number() + skip_count)
    playlist.play()
    await message.channel.send("SKIPPING")


async def stop(message, client, extra_args):
    """
    stops and disconnects the bot
    """

    playlist = await get_playlist(message, client)
    if not playlist:
        return

    playlist.deactivate()


response = commands.Command(player, category="voice")
player_subcommands = {
    "skip": commands.Command(skip),
    "loop": commands.Command(loop),
    "queue": commands.Command(queue),
    "pause": commands.Command(pause),
    "resume": commands.Command(resume),
    "moveto": commands.Command(move_to),
    "remove": commands.Command(remove),
    "stop": commands.Command(stop)
}
response.add_subcommands(player_subcommands)
