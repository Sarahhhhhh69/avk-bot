# ============================================================
# AVK UTILITY BOT — TRIVIA ABCD + STABLE REMINDERS
# ============================================================

import os, json, asyncio, datetime, random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ================= CONFIG =================

GUILD_ID = 1463165558232186910
REMINDERS_CHANNEL_ID = 1464987172133273664
EVENTS_FILE = "events.json"
UTC = datetime.timezone.utc

TODAY_BT_TIMES = [(14, 0), (19, 35)]

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        messages=True,
        message_content=True,
        members=True
    )
)

# ================= TRIVIA QUESTIONS =================

TRIVIA = {

    "AVK": [
        {"q": "Who is the most motivating person in AVK?", "a": ["Sarah", "Coffee", "The Cold", "The Furnace"], "c": 0},
        {"q": "Who always brings chaos in a fun way?", "a": ["Ruti", "Rules", "Silence", "Order"], "c": 0},
        {"q": "Who never sleeps during events?", "a": ["Willy Plonka", "The Snow", "NPCs", "Nobody"], "c": 0},
        {"q": "Who is suspiciously active on Sundays?", "a": ["All Sunday", "Monday", "Tuesday", "Thursday"], "c": 0},
        {"q": "Who gives wise advice like an ancient tree?", "a": ["Treebeard", "A Bush", "A Rock", "A Chair"], "c": 0},
        {"q": "Who always brings good vibes?", "a": ["Miss Sunshine", "Storm Clouds", "Blizzards", "Darkness"], "c": 0},
        {"q": "Who is known for stealth and calm?", "a": ["Nightwolf", "Sheep", "Penguin", "Goldfish"], "c": 0},
        {"q": "Who has legendary energy?", "a": ["Brent", "Low Battery", "Idle Mode", "Sleep"], "c": 0},
        {"q": "Who always makes people laugh?", "a": ["Tickle", "Taxes", "Cold Weather", "Lag"], "c": 0},
        {"q": "Who represents warning but loyalty?", "a": ["RedRabbit", "Blue Turtle", "Green Sloth", "Yellow Fish"], "c": 0}
    ],

    "Sciences": [
        {"q": "What planet is known as the Red Planet?", "a": ["Mars", "Venus", "Jupiter", "Saturn"], "c": 0},
        {"q": "What gas do plants breathe in?", "a": ["Carbon Dioxide", "Oxygen", "Helium", "Nitrogen"], "c": 0},
        {"q": "What is H2O?", "a": ["Water", "Fire", "Salt", "Oxygen"], "c": 0},
        {"q": "What force keeps us on the ground?", "a": ["Gravity", "Magic", "Wind", "Luck"], "c": 0},
        {"q": "What star is at the center of our solar system?", "a": ["The Sun", "The Moon", "Polaris", "Alpha Centauri"], "c": 0},
        {"q": "What organ pumps blood?", "a": ["Heart", "Brain", "Liver", "Lungs"], "c": 0},
        {"q": "What particle has a negative charge?", "a": ["Electron", "Proton", "Neutron", "Photon"], "c": 0},
        {"q": "What vitamin comes from sunlight?", "a": ["Vitamin D", "Vitamin C", "Vitamin A", "Vitamin B12"], "c": 0},
        {"q": "What state of matter is air?", "a": ["Gas", "Solid", "Liquid", "Plasma"], "c": 0},
        {"q": "What is the boiling point of water (°C)?", "a": ["100", "50", "0", "200"], "c": 0}
    ],

    "Geography": [
        {"q": "What is the capital of France?", "a": ["Paris", "Rome", "Berlin", "Madrid"], "c": 0},
        {"q": "Which continent is Brazil in?", "a": ["South America", "Africa", "Asia", "Europe"], "c": 0},
        {"q": "What is the largest ocean?", "a": ["Pacific", "Atlantic", "Indian", "Arctic"], "c": 0},
        {"q": "Which country has the most people?", "a": ["China", "USA", "France", "Brazil"], "c": 0},
        {"q": "What desert is the largest hot desert?", "a": ["Sahara", "Gobi", "Kalahari", "Atacama"], "c": 0},
        {"q": "Mount Everest is in which mountain range?", "a": ["Himalayas", "Alps", "Andes", "Rockies"], "c": 0},
        {"q": "What is the longest river?", "a": ["Nile", "Amazon", "Yangtze", "Mississippi"], "c": 0},
        {"q": "Which country is an island?", "a": ["Japan", "Germany", "Brazil", "Egypt"], "c": 0},
        {"q": "What is the capital of Canada?", "a": ["Ottawa", "Toronto", "Vancouver", "Montreal"], "c": 0},
        {"q": "Which pole is colder?", "a": ["South Pole", "North Pole", "Both same", "Neither"], "c": 0}
    ],

    "Cooking": [
        {"q": "What ingredient is used to make bread rise?", "a": ["Yeast", "Salt", "Sugar", "Flour"], "c": 0},
        {"q": "What country is pizza from?", "a": ["Italy", "France", "USA", "Spain"], "c": 0},
        {"q": "What is sushi mainly made of?", "a": ["Rice", "Beef", "Chicken", "Cheese"], "c": 0},
        {"q": "Which herb is common in pesto?", "a": ["Basil", "Parsley", "Mint", "Rosemary"], "c": 0},
        {"q": "What is chocolate made from?", "a": ["Cocoa beans", "Coffee beans", "Grapes", "Wheat"], "c": 0},
        {"q": "What kitchen tool cuts food?", "a": ["Knife", "Spoon", "Plate", "Cup"], "c": 0},
        {"q": "Which ingredient makes food spicy?", "a": ["Chili", "Sugar", "Salt", "Milk"], "c": 0},
        {"q": "What do you boil pasta in?", "a": ["Water", "Oil", "Milk", "Juice"], "c": 0},
        {"q": "What food is made from milk?", "a": ["Cheese", "Bread", "Rice", "Egg"], "c": 0},
        {"q": "What vitamin is found in oranges?", "a": ["Vitamin C", "Vitamin D", "Vitamin B", "Vitamin A"], "c": 0}
    ],

    "WOS": [
        {"q": "What is needed to heal troops?", "a": ["Food", "Steel", "Wood", "Gems"], "c": 0},
        {"q": "What building trains infantry?", "a": ["Barracks", "Hospital", "Warehouse", "Market"], "c": 0},
        {"q": "Bear Trap is a…", "a": ["Alliance event", "Solo mission", "Market trade", "Loot chest"], "c": 0},
        {"q": "What happens if your furnace freezes?", "a": ["Troops weaken", "Nothing", "You gain power", "Instant win"], "c": 0},
        {"q": "What increases furnace level?", "a": ["Resources", "Luck", "Pets", "Snow"], "c": 0},
        {"q": "What event involves fighting a giant boss?", "a": ["Bear Trap", "Arena", "Exploration", "Market"], "c": 0},
        {"q": "What is alliance territory used for?", "a": ["Bonuses", "Decoration", "Trading", "Chat only"], "c": 0},
        {"q": "What does Arena test?", "a": ["PvP strength", "Cooking", "Trading", "Exploration"], "c": 0},
        {"q": "How do you get stronger?", "a": ["Train troops", "Ignore game", "Sleep", "Quit"], "c": 0},
        {"q": "What warms your city?", "a": ["Furnace", "Hospital", "Warehouse", "Scout Camp"], "c": 0}
    ]
}

# ================= TRIVIA COMMAND =================

@bot.tree.command(name="trivia")
@app_commands.describe(category="Trivia category")
async def trivia(interaction: discord.Interaction, category: str):
    if category not in TRIVIA:
        return await interaction.response.send_message(f"Available categories: {', '.join(TRIVIA.keys())}")

    q = random.choice(TRIVIA[category])
    letters = ["🇦", "🇧", "🇨", "🇩"]

    msg_txt = f"🧠 **{category} Trivia**\n\n{q['q']}\n"
    for i, ans in enumerate(q["a"]):
        msg_txt += f"{letters[i]} {ans}\n"

    await interaction.response.send_message(msg_txt)
    msg = await interaction.original_response()
    for l in letters:
        await msg.add_reaction(l)

    def check(reaction, user):
        return user != bot.user and reaction.message.id == msg.id and str(reaction.emoji) in letters

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=20, check=check)
        idx = letters.index(str(reaction.emoji))
        if idx == q["c"]:
            await interaction.followup.send(f"✅ Correct, {user.mention}!")
        else:
            await interaction.followup.send(f"❌ Wrong! Correct answer was **{q['a'][q['c']]}**")
    except asyncio.TimeoutError:
        await interaction.followup.send("⌛ Time's up!")

# ================= START =================

@bot.event
async def setup_hook():
    await bot.tree.sync()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
