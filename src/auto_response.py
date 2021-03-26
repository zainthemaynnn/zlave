# default
import re
import json
import random

# external
import discord
import yaml

# self-made
from tools import logger_tools

# initialization
logger = logger_tools.standard_logger()
with open("config\\controls.yml") as file:
    autores_controls = yaml.safe_load(file)["data"]["autores"]


# functions
def search(words):
    """
    matches the first keyword to an array of words, if so returns the appropriate response(s) else None
    """

    with open(autores_controls["path"]) as file:
        passive_responses = json.load(file)
        for word in words:
            # stripping word boundaries. for commands it needs to be specific so word boundaries are not stripped.
            if match := re.search(r"\b(.+)\b", word.casefold()):
                word = match.group(1)
            else:
                # it's not a word; continue
                continue

            if response_list := passive_responses["keywords"].get(word):
                logger.debug(f"keyword match: {word}")
                # random response from keyword list
                response = passive_responses["responses"][random.choice(response_list)]
                return word, response
            else:
                # the word didn't exist; continue
                continue

    return None, None


async def sauce_msg(response_obj, keyword, message):
    """
    processes content from search() to be sent
    """

    ctype = response_obj["type"]
    content = response_obj["content"]

    # sends per-case. wish I had a switch statement.
    if ctype == "simple":
        await message.channel.send(content)
    elif ctype == "insert":
        await message.channel.send(f"<@{message.author.id}> {content.format(keyword.upper())}")
    elif ctype == "media":
        await message.channel.send(file=discord.File(content))
    else:
        logger.error(f"undefined content type detected: {ctype}")
