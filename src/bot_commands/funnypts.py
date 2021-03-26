# default
from datetime import datetime

# external
import yaml

# self-made
from tools import commands, database, utils

with open("config\\controls.yml") as file:
    controls = yaml.safe_load(file)
    db = controls["data"]["database"]
    funny_controls = controls["data"]["funnypts"]


# functions
async def funnypts_transaction(message, client, extra_args, operation):
    """
    adds or removes a point of funny (functions are more or less the same thing)
    """

    awarder = message.author.id

    # input screening
    if len(extra_args) < 2:
        await message.channel.send(f"PLEASE USE THIS: `funnypts {operation} user_mention reason`")
        return False

    if not (awardee := utils.from_mention(extra_args[0])):
        await message.channel.send("PLEASE MENTION SOMEONE. WHAT ARE THEY GONNA DO, CRY?")
        return False

    reason_length = funny_controls["reason_length"]
    if len(reason := " ".join(extra_args[1:])) > reason_length:
        await message.channel.send(F"APOLOGIES, I ONLY STORE DESCRIPTIONS OF UP TO {reason_length} CHARACTERS. WELCOME TO TWITTER")
        return False

    if client.get_user(awarder).bot or client.get_user(awardee).bot:
        return False

    if awarder == awardee:
        await message.channel.send("WHAT ARE YOU, AN EGOMANIAC?")
        return False

    # writing
    if operation == "add":
        transaction = 1
    elif operation == "remove":
        transaction = -1

    @database.query
    def write_entry(conn):
        conn.execute("INSERT INTO funnypts VALUES(?, ?, ?, ?, ?)",
                     (awarder, awardee, reason, transaction, datetime.now()))
        conn.commit()
        conn.close()

    write_entry()
    return True


# response
async def funnypts(message, client, extra_args):
    """
    think someone is cool? or did they post something cringe? document it.
    """

    await message.channel.send("CHECK WHAT YOU CAN DO WITH `help funnypts`")


# subcommands
async def add(message, client, extra_args):
    """
    adds a point of funny
    """

    if await funnypts_transaction(message, client, extra_args, "add"):
        await message.channel.send("FUNNYPOINT ADDED. CONGRATULATIONS, COMEDY HAS BEEN ACHIEVED")


async def leaderboard(message, client, extra_args):
    """
    displays who the user thinks is the funniest, yourself by default
    """

    if not extra_args or not (user_id := utils.from_mention(extra_args[0])):
        user_id = message.author.id
    page_length = controls["style"]["embeds"]["length"]

    @database.query
    def find_people(conn):
        cursor = conn.cursor()
        # the limit forces the leaderboard to match the chosen page length
        cursor.execute("SELECT awarder, SUM(operation) AS aggregate FROM funnypts WHERE awardee = ? GROUP BY awarder ORDER BY aggregate DESC LIMIT {0}".format(
            page_length), (user_id,))
        awarder_lb = cursor.fetchall()
        cursor.execute("SELECT awardee, SUM(operation) AS aggregate FROM funnypts WHERE awarder = ? GROUP BY awardee ORDER BY aggregate DESC LIMIT {0}".format(
            page_length), (user_id,))
        awardee_lb = cursor.fetchall()
        cursor.close()
        conn.close()
        return (awarder_lb, awardee_lb)

    boards = find_people()
    entries = []
    for lb in boards:
        for entry in lb:
            entries.append(entry)
        # fill empty entries
        for i in range(len(lb), page_length):
            entries.append(("--", "--"))

    @utils.paginated_embeds
    def populate(embed, entry, position):
        if entry[0] != "--":
            username = client.get_user(entry[0]).name.split("#", 1)[0]
            desc = str(entry[1])
            desc += " POINT AWARDED" if desc == "1" else " POINTS AWARDED"
        else:
            username = desc = "--"
        position = position % page_length + 1
        embed.add_field(name="{0}. {1}".format(
            position, username), value=desc, inline=False)

    page_embeds = populate("P1: AWARDED FROM | P2: AWARDED TO", entries)
    await utils.sauce_pages(page_embeds, message, client)


async def history(message, client, extra_args):
    """
    view a person's funnypoint history, yourself by default
    """

    if not extra_args or not (user_id := utils.from_mention(extra_args[0])):
        user_id = message.author.id

    @database.query
    def get_transactions(conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM funnypts WHERE awarder = ? OR awardee = ? ORDER BY date DESC", (user_id, user_id))
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()
        return transactions

    if not (transactions := get_transactions()):
        await message.channel.send("THIS USER HAS NO HISTORY, THEY SHOULD THOUGH")
        return

    @utils.paginated_embeds
    def populate(embed, entry, entry_number):
        awarder = client.get_user(entry[0]).name.split("#", 1)[0]
        awardee = client.get_user(entry[1]).name.split("#", 1)[0]
        transaction = "GIVEN TO" if entry[3] > 0 else "TAKEN FROM"
        date = entry[4].split(" ", 1)[0]
        reason = "\"{0}\"".format(entry[2])

        embed.add_field(
            name="{0} — {2} — {1} • {3}".format(awarder, awardee, transaction, date), value=reason, inline=False)

    title = f"{client.get_user(user_id).name}'s FUNNYPOINT HISTORY"
    embeds = populate(title, transactions, page_length=5)
    await utils.sauce_pages(embeds, message, client)


async def remove(message, client, extra_args):
    """
    removes a point of funny
    """

    if await funnypts_transaction(message, client, extra_args, "remove"):
        await message.channel.send("BRUH, THAT WAS CRINGE. SOMEONE JUST REVOKED YOUR FUNNYPOINT")


response = commands.Command(funnypts, {
    "add": commands.Command(add),
    "remove": commands.Command(remove),
    "history": commands.Command(history),
    "lb": commands.Command(leaderboard)
}, "games")
