# self-made
from tools import commands


# response
@commands.operator_only
async def shutoff(message, client, extra_args):
    """
    turn off the bot through discord. the code is literally two lines long lmao
    """

    await message.channel.send("AIGHT SEE YA")
    await client.logout()

response = commands.Command(shutoff, category="configuration")
