# ============================================================
# AVK UTILITY BOT — FINAL STABLE VERSION
# ============================================================

import os
import asyncio
import datetime
import random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ===================== CONFIG =====================

UTC = datetime.timezone.utc
GUILD_ID = 1463165558232186910
REMINDERS_CHANNEL_ID = 1464987172133273664

# Bear Trap times for TODAY (UTC)
TODAY_BT_TIMES = [
    (14, 0),
    (19, 35)
]

# ==================================================
# BOT SETUP
# ==================================================

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        messages=True,
        message_content=True,
        members=True
    )
)

# ===================== TRIVIA DATA =====================

TRIVIA = {
    "AVK": [
        {"q": "Who is the most motivating person in AVK?", "a": ["Sarah", "Coffee", "Snow", "Lag"], "c": 0},
        {"q": "Who causes chaos but everyone still loves?", "a": ["Ruti", "Rules", "Order", "Silence"], "c": 0},
        {"q": "Who never sleeps during events?", "a": ["Willy Plonka", "NPCs", "The Furnace", "Nobody"], "c": 0},
        {"q": "Who is always active on Sundays?", "a": ["All Sunday", "Monday", "Tuesday", "Friday"], "c": 0},
        {"q": "Who gives wise advice like an old tree?", "a": ["Treebeard", "A Rock", "A Chair", "A Table"], "c": 0},
    ],
    "Science": [
        {"q": "What planet is known as the Red Planet?", "a": ["Mars", "Venus", "Jupiter", "Saturn"], "c": 0},
        {"q": "What gas do humans breathe?", "a": ["Oxygen", "Carbon Dioxide", "Helium", "Nitrogen"], "c": 0},
    ],
    "Geography": [
        {"q": "What is the capital of France?", "a": ["Paris", "Rome", "Berlin", "Madrid"], "c": 0},
        {"q": "Which ocean is the largest?", "a": ["Pacific", "Atlantic", "Indian", "Arctic"], "c": 0},
    ],
    "Cooking": [
        {"q": "Which country does pizza come from?", "a": ["Italy", "France", "USA", "Spain"], "c": 0},
        {"q": "What makes bread rise?", "a": ["Yeast", "Salt", "Sugar", "Flour"], "c": 0},
    ],
    "WOS": [
        {"q": "What is needed to heal troops?", "a": ["Food", "Steel", "Wood", "Gems"], "c": 0},
        {"q": "Bear Trap is a…", "a": ["Alliance event", "Solo mission", "Market trade", "Loot chest"], "c": 0},
    ],
    "Cinema": [
        {"q": "Who played Jack in Titanic?", "a": ["Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Johnny Depp"], "c": 0},
        {"q": "Which movie features a powerful ring?", "a": ["Lord of the Rings", "Star Wars", "Matrix", "Avatar"], "c": 0},
    ],
    "TV Series": [
        {"q": "Who is the main character in Breaking Bad?", "a": ["Walter White", "Jesse Pinkman", "Saul Goodman", "Hank"], "c": 0},
        {"q": "Which series has dragons?", "a": ["Game of Thrones", "Friends", "Dexter", "Lost"], "c": 0},
    ],
    "Music": [
        {"q": "Who is known as the King of Pop?", "a": ["Michael Jackson", "Elvis Presley", "Prince", "Madonna"], "c": 0},
        {"q": "Which band sang Bohemian Rhapsody?", "a": ["Queen", "Beatles", "U2", "Oasis"], "c": 0},
    ]
}

# ===================== COMMANDS =====================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

@bot.tree.command(name="trivia")
@app_commands.describe(category="Trivia category")
async def trivia(interaction: discord.Interaction, category: str):
    if category not in TRIVIA:
        return await interaction.response.send_message(
            f"Available categories: {', '.join(TRIVIA.keys())}"
        )

    q = random.choice(TRIVIA[category])
    letters = ["🇦", "🇧", "🇨", "🇩"]

    text = f"🧠 **{category} Trivia**\n\n{q['q']}\n"
    for i, ans in enumerate(q["a"]):
        text += f"{letters[i]} {ans}\n"

    await interaction.response.send_message(text)
    msg = await interaction.original_response()

    for l in letters:
        await msg.add_reaction(l)

    def check(reaction, user):
        return (
            user != bot.user
            and reaction.message.id == msg.id
            and str(reaction.emoji) in letters
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=20, check=check)
        idx = letters.index(str(reaction.emoji))
        if idx == q["c"]:
            await interaction.followup.send(f"✅ Correct, {user.mention}!")
        else:
            await interaction.followup.send(
                f"❌ Wrong! Correct answer was **{q['a'][q['c']]}**"
            )
    except asyncio.TimeoutError:
        await interaction.followup.send("⌛ Time’s up!")

# ===================== SCHEDULER =====================

bt_sent = set()
arena_sent_date = None

async def scheduler_loop():
    global arena_sent_date
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(UTC)

        # -------- ARENA (23:45 UTC) --------
        if now.hour == 23 and now.minute == 45:
            today = now.date()
            if arena_sent_date != today and channel:
                await channel.send(
                    "⚔️ **Arena ends in 15 minutes!** Finish your fights!"
                )
                arena_sent_date = today

        # -------- BEAR TRAP WITH REMINDERS --------
        for hour, minute in TODAY_BT_TIMES:
            bt_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            for label, offset in [("1 hour", 60), ("30 minutes", 30), ("5 minutes", 5), ("NOW", 0)]:
                reminder_time = bt_time - datetime.timedelta(minutes=offset)
                key = f"{bt_time.strftime('%Y-%m-%d %H:%M')}-{label}"

                if reminder_time.hour == now.hour and reminder_time.minute == now.minute:
                    if key not in bt_sent and channel:
                        if label == "NOW":
                            await channel.send(
                                "🐻❄️ **BEAR TRAP NOW!** Prepare yourselves AVK warriors!"
                            )
                        else:
                            await channel.send(f"⏰ **Bear Trap starts in {label}!**")
                        bt_sent.add(key)

        await asyncio.sleep(60)

# ===================== START =====================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler_loop())

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_BOT_TOKEN missing")
