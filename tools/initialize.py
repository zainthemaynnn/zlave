# can't really write yaml very well in a batch command
# this is just a helper file to do that part in setup
# pretty messy, but I'm only using it once hecks dee

import yaml

with open("install\\secrets.yml") as file:
    secrets = yaml.safe_load(file)

with open("config\\secrets.yml", "w") as file:
    # token
    msg = ("every discord bot has a \"client token\". to get one:\n"
           "-go to discord.com/developers\n"
           "-click \"create a bot\"\n"
           "-click \"copy\" under \"token\"")
    print(msg)
    secrets["tokens"]["discord"] = input("BOT TOKEN: ")
    print("")

    # owner
    msg = ("every user has a \"user id\". to get one:\n"
           "-go to the discord app\n"
           "-enable \"developer mode\" in settings\n"
           "-right click yourself and click \"copy id\"")
    print(msg)

    while not (owner_id := input("OWNER ID: ")).isdigit():
        print("I need a number, idiot")
    secrets["permissions"]["owner"] = int(owner_id)
    print("")

    yaml.safe_dump(secrets, file, default_flow_style=False)
