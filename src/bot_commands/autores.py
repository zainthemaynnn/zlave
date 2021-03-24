# warning: EXTREMELY MESSY! and probably inefficient too!

# default
import json
import asyncio

# external
import discord
import yaml

# self-made
from tools import commands, utils
with open("config\\controls.yml") as controls_file:
    controls = yaml.safe_load(controls_file)
    ext_folders = controls["data"]["ext_folders"]
    autores_controls = controls["data"]["autores"]
    json_path = autores_controls["path"]


# function
async def confirm(message, client, extra_args, data=None):
    """
    asks for confirmation
    """

    if data:
        await message.channel.send(json.dumps(data, indent=4, sort_keys=True))

    def check(response):
        if response.author == message.author:
            return True

    try:
        response = await client.wait_for("message", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        return False
    else:
        response = response.content.casefold()
        affirmatives = ("y", "yes", "yeah", "k", "ok", "okay")
        for yeah in affirmatives:
            if yeah in response:
                await message.channel.send("AIGHT")
                return True
        else:
            await message.channel.send("DO IT RIGHT NEXT TIME, IDIOT")
            return False


# response
@commands.premium_only
async def auto_res(message, client, extra_args):
    """
    make automatic responses so we don't have to write json by hand
    """

    cmdlist = client.get_cmdlist()
    await cmdlist["help"].run(message, client, extra_args, command=("autores", cmdlist["autores"]))


# subcommands
@commands.premium_only
async def gimme_restypes(message, client, extra_args):
    """
    sauces list of valid content types
    """

    @utils.paginated_embeds
    def populate(embed, entry, position):
        embed.add_field(
            name=entry[0], value=entry[1], inline=False)

    res_types = autores_controls["res_types"]
    data = []
    for rtype in res_types:
        data.append((rtype, res_types[rtype]))

    page_embeds = populate("VALID CONTENT TYPES", data)
    await utils.sauce_pages(page_embeds, message, client)


@commands.premium_only
async def newres(message, client, extra_args):
    """
    add to or create a new a response. leave blank for usage.
    """

    # this code si really janky. sorry about that.
    usage = "RESPONSE_NAME, CONTENT_TYPE, \"CONTENT\" IF TEXT OR ATTACHMENT IF FILE"
    if len(extra_args) < 2:
        await message.channel.send("USAGE: " + usage)
        return

    res_types = autores_controls["res_types"]
    if not (rtype := extra_args[1].casefold()) in res_types:
        await gimme_restypes(message, client, extra_args)
        return

    if rtype in ("simple", "insert"):
        if len(extra_args) < 3:
            await message.channel.send("YOUR TEXT FIELD IS MISSING")
            return
        else:
            content = " ".join(extra_args[2:])

    elif rtype in "media":
        if not message.attachments:
            await message.channel.send("YOUR ATTACHMENT IS MISSING")
            return
        else:

            attachment = message.attachments[0]
            folder = None
            for ext_folder in ext_folders:
                if not folder:
                    for ext in ext_folders[ext_folder]:
                        if attachment.filename.endswith(ext):
                            folder = ext_folder
                            break

            if not folder:
                await message.channel.send("UNSUPPORTED FILE TYPE")
                return

            filepath = f"resources\\{folder}\\{attachment.filename}"
            await attachment.save(filepath)
            content = filepath

    with open(json_path) as json_file:
        passive_responses = json.load(json_file)
        name = extra_args[0].casefold()

        if not (res_table := passive_responses["responses"].get(name)):
            await message.channel.send(f"RESPONSE NOT FOUND; I AM CREATING A NEW RESPONSE CALLED `{name}`")
            res_table = passive_responses["responses"][name] = []

        res_table.append({
            "type": rtype,
            "content": content
        })

        passive_responses["responses"][name] = res_table

    await message.channel.send("ARE YOU SURE YOU WANT TO DO THIS?")
    if await confirm(message, client, extra_args, {name: res_table}):
        with open(json_path, "w") as json_file:
            json.dump(passive_responses, json_file, separators=(",", ":"))


@commands.premium_only
async def keys_to_res(message, client, extra_args):
    """
    assign multiple keywords to one response. response name first, then any number of keywords
    """

    if len(extra_args) < 2:
        await message.channel.send("PLEASE GIVE ME SOMETHING TO WORK WITH")
        return

    with open(json_path) as json_file:
        passive_responses = json.load(json_file)
        resname = extra_args[0].casefold()

        if not passive_responses["responses"].get(resname):
            await message.channel.send(f"`{resname}` IS NOT AN EXISTING RESPONSE")
            return

        keywords = passive_responses["keywords"]
        added_keys = []
        new_keys = []
        for kw in extra_args[1:]:
            kw = kw.casefold().strip(",;")
            if not keywords.get(kw):
                keywords[kw] = []
                new_keys.append(kw)

            if resname not in keywords[kw]:
                keywords[kw].append(resname)
                added_keys.append(kw)
            else:
                await message.channel.send(f"RESPONSE `{resname}` ALREADY ADDED. SKIPPING...")
                continue

    data = {"resname": resname, "added_keys": added_keys, "new_keys": new_keys}
    await message.channel.send("ARE YOU SURE YOU WANT TO DO THIS? (DOES NOT OVERWRITE OLD KEYS)")
    if await confirm(message, client, extra_args, data):
        with open(json_path, "w") as json_file:
            json.dump(passive_responses, json_file, separators=(",", ":"))


@commands.premium_only
async def res_to_key(message, client, extra_args):
    """
    assign multiple responses to one keyword. keyword first, then any number of responses
    """

    if len(extra_args) < 2:
        await message.channel.send("PLEASE GIVE ME SOMETHING TO WORK WITH")
        return

    with open(json_path) as json_file:
        passive_responses = json.load(json_file)
        kw = extra_args[0].casefold()

        keywords = passive_responses["keywords"]
        responses = passive_responses["responses"]

        if not keywords.get(kw):
            await message.channel.send(f"KEYWORD `{kw}` DOES NOT YET EXIST. CREATE?")
            if await confirm(message, client, extra_args):
                keywords[kw] = []
            else:
                return

        added_res = []
        for resname in extra_args[1:]:
            resname = resname.casefold().strip(",;")
            if not responses.get(resname):
                await message.channel.send(f"RESPONSE `{resname}` DOES NOT YET EXIST. SKIPPING...")
                continue
            else:
                if resname not in keywords[kw]:
                    keywords[kw].append(resname)
                    added_res.append(resname)
                else:
                    await message.channel.send(f"KEYWORD `{kw}` ALREADY HAS THIS RESPONSE. SKIPPING...")
                    continue

    data = {"keyword": kw, "added_responses": added_res}
    await message.channel.send("ARE YOU SURE YOU WANT TO DO THIS? (DOES NOT OVERWRITE OLD RESPONSES)")
    if await confirm(message, client, extra_args, data):
        with open(json_path, "w") as json_file:
            json.dump(passive_responses, json_file, separators=(",", ":"))


@commands.premium_only
async def view_res(message, client, extra_args):
    """
    view response data
    """

    page = 0
    if extra_args and extra_args[0].isnumeric():
        page = extra_args[0]

    with open(json_path) as json_file:
        responses = list(sorted(json.load(json_file)["responses"].items()))

    @utils.paginated_embeds
    def populate(embed, entry, entry_number):
        messages = entry[1]
        desc = []
        for msg in messages:
            desc.append("{0} • {1}".format(msg["type"], msg["content"]))
        desc = "\n".join(desc)
        embed.add_field(name=entry[0], value=desc, inline=False)

    page_embeds = populate("RESPONSE DATA", responses, page_length=10)
    await utils.sauce_pages(page_embeds, message, client, page)


@commands.premium_only
async def view_keys(message, client, extra_args):
    """
    view keyword data
    """

    page = 0
    if extra_args and extra_args[0].isnumeric():
        page = extra_args[0]

    with open(json_path) as json_file:
        keywords = list(sorted(json.load(json_file)["keywords"].items()))

    @utils.paginated_embeds
    def populate(embed, entry, entry_number):
        embed.add_field(name=entry[0], value=", ".join(entry[1]))

    page_embeds = populate("KEYWORD DATA", keywords, page_length=24)
    await utils.sauce_pages(page_embeds, message, client, page)


@commands.premium_only
async def delres(message, client, extra_args):
    """
    delete responses, give list of names. keywords will be automatically deleted if all of their responses were removed.
    """

    if not extra_args:
        return

    deleted = []
    with open(json_path) as json_file:
        passive_responses = json.load(json_file)
        for resname in extra_args:
            if passive_responses["responses"].pop(resname, None):
                deleted.append(resname)
            else:
                await message.channel.send(f"RESPONSE `{resname}` NOT FOUND")
                continue

        def remove(word):
            return False if word in extra_args else True

        # empty keywords
        keywords = passive_responses["keywords"]
        deadkeys = []
        for kw in keywords:
            filtered = list(filter(remove, keywords[kw]))
            if filtered:
                keywords[kw] = filtered
            else:
                deadkeys.append(kw)

        for kw in deadkeys:
            del keywords[kw]

    data = {"deleted_responses": deleted}
    await message.channel.send("ARE SURE YOU WANT TO DO THIS?")
    if await confirm(message, client, extra_args, data):
        with open(json_path, "w") as json_file:
            json.dump(passive_responses, json_file, separators=(",", ":"))


@commands.premium_only
async def delkeys(message, client, extra_args):
    """
    delete keywords, give list of names. NOTE: responses that have no references will still not be removed.
    """

    if not extra_args:
        return

    deleted = []
    with open(json_path) as json_file:
        passive_responses = json.load(json_file)
        for kw in extra_args:
            if passive_responses["keywords"].pop(kw, None):
                deleted.append(kw)
            else:
                await message.channel.send(f"KEYWORD `{kw}` NOT FOUND")
                continue

    data = {"deleted_keys": deleted}
    await message.channel.send("ARE SURE YOU WANT TO DO THIS?")
    if await confirm(message, client, extra_args, data):
        with open(json_path, "w") as json_file:
            json.dump(passive_responses, json_file, separators=(",", ":"))


@commands.premium_only
async def sauce(message, client, extra_args):
    """
    sends the actual json file
    """

    await message.channel.send(file=discord.File(json_path))


response = commands.Command(auto_res, category="special")
response_subcommands = {
    "newres": commands.Command(newres),
    "kw2res": commands.Command(keys_to_res),
    "res2kw": commands.Command(res_to_key),
    "viewres": commands.Command(view_res),
    "viewkw": commands.Command(view_keys),
    "delres": commands.Command(delres),
    "delkw": commands.Command(delkeys),
    "rtypes": commands.Command(gimme_restypes),
    "sauce": commands.Command(sauce)
}
response.add_subcommands(response_subcommands)
