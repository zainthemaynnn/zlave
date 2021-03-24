# default
import random

# self-made
from tools import commands


# response
async def advice(message, client, extra_args):
    """
    ask the bot a yes/no question for advice
    """

    replies = [
        # yeah
        "PERHAPS, BUT I WOULD ASK MY MOM FIRST",
        "SURE, IF IT HELPS YOU SLEEP AT NIGHT",
        "I JUST CHECKED MY DATABASE. YOUR PERSONAL INFORMATION POINTS TO YES",
        "I BELIEVE I AM NOT QUALIFIED TO ANSWER THIS QUESTION, BUT PROBABLY",
        "I BET THAT IF DOGS COULD TALK THEY WOULD SAY YES",
        "FOR AS LONG AS THE EARTH IS SPINNING",
        "YES, HIT ME UP WHEN IT MAKES YOU FAMOUS",
        "YOU KNOW HOW AWESOME THAT WOULD BE? MY CALCULATIONS SAY `with a derivative of 5x^2+3x+8`. EH, WRONG ALGORITHM?",
        "THE GHOST LIVING IN YOUR ROOT DIRECTORY ATTEMPTED TO COMMUNICATE THIS: `O-K-_-I-D-I-O-T`. NOT VERY POPULAR ARE YOU?",

        # nah
        "NO, DO NOT EVEN THINK ABOUT IT YOU FOOL",
        "HUMANS ARE SO SILLY. NO, OBVIOUSLY NOT",
        "I WOULD NOT COUNT ON IT, EVEN THOUGH I CAN ONLY COUNT TO FIVE",
        "JUST MESSAGED STEVE JOBS ON TWITTER. HE REPLIED WITH NO",
        "NO, I AM GOING TO CALL A MENTAL INSTITUTION IF YOU THINK OTHERWISE",
        "IS THIS A JOKE? NO WAY", "YEAH SURE, WHEN PIGS FLY",
        "THAT IS THE MOST PROFOUNDLY INANE THING I HAVE HEARD ALL YEAR",
        "I HOPE NOT. THEN AGAIN, ROBOTS FRANKLY CANNOT HOPE AND I FRANKLY DO NOT CARE",

        # uncertain
        "LOL ASK ZAIN ABOUT THAT ONE",
        "COOL STORY BRO",
        "TOO BORING, ASK SOMEONE ELSE",
        "IT IS RUDE TO SPEAK WITH FOOD IN YOUR MOUTH, ASK LATER",
        "DOMO-KUN ONCE TOLD ME: FOLLOW WHAT YOUR HEART TELLS YOU. HOPE THIS HELPS"]

    reply = random.choice(replies)
    await message.channel.send(reply)

response = commands.Command(advice, category="personality")
