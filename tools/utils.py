# default
import math
import asyncio
import re
from functools import wraps

# external
import discord
import yaml

# self-made
from tools import logger_tools

# initialization
logger = logger_tools.standard_logger()
with open("config\\controls.yml") as file:
    style_controls = yaml.safe_load(file)["style"]


# functions
async def sauce_pages(page_embeds, message, client, page=0):
    """
    makes sure the raw user input is a valid page number and sauces embeds with page swapping
    """

    if len(page_embeds) == 0:
        await message.channel.send(f"I COULD NOT FIND ANY INFO FOR THIS ENTRY")
        return

    length = len(page_embeds)
    if isinstance(page, str):
        page = int(page) - 1

    if not 0 <= page < length:
        await message.channel.send(f"THIS IS NOT A PAGE. THERE ARE ONLY `{length}` PAGES INCLUDED. IMBECILE")
        return

    bot_message = await message.channel.send(embed=page_embeds[page])
    logger.debug("paged embeds sent")

    # using global. don't try this at home kids
    global new_page
    new_page = page

    async def add_reactions():
        # wtf... are the unicode arrows supposed to look different? cause I hate it. a lot.
        LARR = RARR = ""
        if new_page != 0:
            LARR = "⬅️"
            await bot_message.add_reaction(LARR)
        if new_page != length - 1:
            RARR = "➡️"
            await bot_message.add_reaction(RARR)

        def page_swap(reaction, user):
            if user == message.author and reaction.message == bot_message:
                emoji = str(reaction.emoji)
                global new_page
                if LARR and emoji == LARR:
                    new_page -= 1
                    return True
                elif RARR and emoji == RARR:
                    new_page += 1
                    return True

        async def clear():
            try:
                await bot_message.clear_reactions()
            except discord.Forbidden:
                logger.debug(
                    f"could not remove reactions in guild {message.guild.name} ({message.guild.id}); missing permissions")
            except discord.NotFound:
                pass

        try:
            reaction, user = await client.wait_for("reaction_add", check=page_swap, timeout=60.0)
        except asyncio.TimeoutError:
            await clear()
            return
        else:
            await clear()
            await bot_message.edit(embed=page_embeds[new_page])
            await add_reactions()

    await add_reactions()


def to_minutes(seconds):
    """
    formats seconds to mm:ss
    """

    seconds = int(seconds)
    return "{}:{:02d}".format(math.floor(seconds / 60), seconds % 60)


def from_mention(mention):
    """
    gets user id from mention
    """

    match = re.search(r"<@!?(\d{17,18})>", mention)
    if match:
        return int(match.group(1))
    else:
        return None


# classes
class MyExecutor:
    def __init__(self, loop=asyncio.get_event_loop(), threads=1):
        from concurrent.futures import ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(threads)
        self.loop = loop

    async def __call__(self, func, *args, **kwargs):
        from functools import partial
        return await self.loop.run_in_executor(self.executor, partial(func, *args, **kwargs))


# decorators
def paginated_embeds(populator):
    """
    makes, uh, generic paginated embeds from an embed populator. beautiful, isn't it?
    """

    @wraps(populator)
    def wrapper(title, entries, page_length=style_controls["embeds"]["length"]):
        page_embeds = []

        def create_pages(startindex, entry_number):
            if startindex == len(entries):
                return

            embed = discord.Embed(
                title=title, description=f"page {math.floor(startindex / page_length + 1)} of {math.ceil(len(entries) / page_length)}", color=style_controls["embeds"]["color"])
            for entry in entries[startindex:]:
                populator(embed, entry, entry_number)
                entry_number += 1
                # when the entry count reaches page length a new page is added
                if len(embed.fields) == page_length:
                    page_embeds.append(embed)
                    create_pages(startindex + page_length, entry_number)
                    break
            # adds the final page
            else:
                page_embeds.append(embed)

        create_pages(0, 0)
        return page_embeds
    return wrapper
