# default
import asyncio

# external
import discord
import yaml

# self-made
from tools.utils import to_minutes

# initialization
with open("config\\controls.yml") as controls_file:
    music_controls = yaml.safe_load(controls_file)["music"]


class Playlist:
    """
    playlist, one per guild
    """

    def __init__(self, client):
        self.queue = []
        self.client = client

        self.active = False
        self.looping = False

        self.play_next = False
        self.track_number = 0
        self.max_length = music_controls["playlist_length"]
        self.volume = music_controls["volume"]

    async def play_track(self, channel, voice_client):
        """
        begin playing current track from url
        """

        voice_client.stop()

        if not self.looping and self.track_number > 0:
            # remove previous songs
            self.queue = self.queue[self.track_number:]
            self.track_number = 0
        elif self.looping:
            # modulus in case it skipped past the end
            self.track_number %= len(self.queue)

        if not self.queue:
            return

        video = self.queue[self.track_number]
        await channel.send("NOW PLAYING `{0} • {1}`".format(video["title"], to_minutes(video["duration"])))

        FFMPEG_OPTS = {
            # pretty sure this strips the video portion
            "options": "-vn",
            # https://stackoverflow.com/a/62637605/15302829
            # please god work, pasted code EDIT: it did B)
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(video["url"], **FFMPEG_OPTS), volume=self.volume)
        try:
            voice_client.play(source)
        except discord.ClientException:
            # bot disconnected
            pass

    async def run(self, channel, voice_client):
        """
        playing routine
        """

        if self.active:
            return

        self.active = True
        looptime = music_controls["looptime"]
        timeout = music_controls["timeout"]
        time_alone = 0.0

        await self.play_track(channel, voice_client)

        while self.active:
            if not self.queue:
                break

            # forces bot to disconnect after certain number of loops by itself
            if len(voice_client.channel.members) > 1 and time_alone > 0.0:
                time_alone = 0.0
            else:
                if time_alone >= timeout:
                    await channel.send("GET SOMEONE ELSE IF YOU'RE GOING TO LEAVE ME HERE NEXT TIME")
                    break
                else:
                    time_alone += looptime
                

            # changed externally
            if self.play_next:
                self.play_next = False
                await self.play_track(channel, voice_client)

            elif not voice_client.is_playing() and not voice_client.is_paused():
                self.track_number += 1
                await self.play_track(channel, voice_client)

            await asyncio.sleep(looptime)

        self.active = False
        voice_client.stop()
        self.client.remove_playlist(voice_client.guild.id)
        await channel.send("PLAYLIST COMPLETE")
        await voice_client.disconnect()

    def enqueue(self, video):
        if len(self.queue) == self.max_length:
            return False
        else:
            self.queue.append(video)
        return True

    def play(self):
        self.play_next = True

    def toggle_mode(self):
        self.looping = not self.looping
        if not self.looping:
            # delete all previous songs
            self.queue = self.queue[self.track_number:]
            self.track_number = 0

    def is_looping(self):
        return self.looping

    def get_queue(self):
        return self.queue

    def get_track_number(self):
        return self.track_number

    def set_track_number(self, number):
        self.track_number = number

    def remove(self, number):
        if 0 <= number < len(self.queue):
            del self.queue[number]
            # move on if it deleted the one it was on
            if number == self.track_number:
                self.play_next = True
            return True
        else:
            return False

    def deactivate(self):
        self.active = False
