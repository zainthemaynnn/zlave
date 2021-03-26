# default
import os

# self-made
from tools import commands, utils

# initialization
PATH = os.environ["PYTHONPATH"]
app_data = PATH + "\\data\\App_Data.db"


# functions
@utils.paginated_embeds
def populate(embed, command, entry_number):
    """
    add commands to embed pages
    """

    field_name = f"`{command[0]}`"
    category = command[1].category
    if category:
        field_name += f" - {category}"
    embed.add_field(name=field_name,
                    value=command[1].description, inline=False)


# response
async def cmdhelp(message, client, extra_args, command=None):
    """
    read about the commands. try help with a specific command such as player or use page numbers.
    """

    if command:
        title = command[0]
        cmdlist = command[1].get_subcommands()
    else:
        # default pages
        title = "ZAIN TELLS ME I AM NOT USEFUL"
        cmdlist = client.get_cmdlist()

    page = 0
    if extra_args:
        arg0 = extra_args[0]
        # if page number given
        if arg0.isdigit():
            page = arg0
        # if specified
        elif arg0 in cmdlist:
            await cmdhelp(message, client, extra_args[1:], (arg0, cmdlist[arg0]))
            return

    page_embeds = populate(title, list(cmdlist.items()), page_length=5)
    await utils.sauce_pages(page_embeds, message, client, page)

response = commands.Command(cmdhelp, category="information")
