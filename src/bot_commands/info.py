# default
import os

# external
import discord
import yaml

# self-made
from tools import commands, utils

# initialization
PATH = os.environ["PYTHONPATH"]


# functions
def gimme_info_pages(client):
    """
    generate pages of info
    """

    with open("config\\info.yml") as info_file:
        info_data = yaml.safe_load(info_file)
    page_embeds = []
    pagecount = len(info_data)
    pagenum = 0

    # embed 0: bot specific info
    pagenum += 1
    embed = discord.Embed(title="client info", description="page {0} of {1}".format(
        pagenum, pagecount), color=0xc500ff)
    embed.add_field(name="bot operator", value=client.get_user(
        int(os.environ["zlave_owner"])), inline=False)
    embed.add_field(name="invite me", value=discord.utils.oauth_url(
        client.user.id, discord.Permissions().general()), inline=False)
    embed.add_field(name="disclaimer", value="the invite above gives general privileges by default. know that some commands will only work with certain administration privileges.", inline=False)
    page_embeds.append(embed)

    # embed 1: general info
    pagenum += 1
    embed = discord.Embed(title="general info", description="page {0} of {1}".format(
        pagenum, pagecount), color=0xc500ff)
    for field in info_data["general"]:
        embed.add_field(name=field.replace("_", " "),
                        value=info_data["general"][field], inline=False)
    page_embeds.append(embed)

    return page_embeds


# response
async def info(message, client, extra_args):
    """
    read bot info
    """

    page = 0
    if extra_args and extra_args[0].isdigit():
        page = extra_args[0]
    page_embeds = gimme_info_pages(client)
    await utils.sauce_pages(page_embeds, message, client, page)

response = commands.Command(info, category="information")
