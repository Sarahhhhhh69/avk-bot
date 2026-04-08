# ============================================================
# AVK UTILITY BOT — EVENTS + GAMES (STABLE)
# ============================================================

import os
import json
import asyncio
import datetime
import random
import discord
from discord.ext import commands
from discord import app_commands

from keep_alive import keep_alive
keep_alive()

# ============================================================
# CONFIG
# ============================================================

GUILD_ID = 1463165558232186910

EVENT_REMINDERS_CHANNEL_ID = 1464987172133273664
GAMES_CHANNEL_ID = 1464987164814082199

EVENTS_FILE = "events.json"
TRIVIA_FILE = "trivia.json"

UTC = datetime.timezone.utc

BEAR_TRAP_TIMES = [(14, 0), (19, 35)]
BEAR_TRAP_INTERVAL_DAYS = 2
BEAR_TRAP_START_DATE = datetime.date.today()

# ============================================================
# BOT
# ============================================================

intents = discord.Intents(
    guilds=True,
    messages=True,
    message_content=True,
    members=True,
    reactions=True
)

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# JSON HELPERS
# ============================================================

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

EVENTS = load_json(EVENTS_FILE, [])
TRIVIA_DB = load_json(TRIVIA_FILE, {})

# ============================================================
# BASIC
# ============================================================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Bot online.")

# ============================================================
# EVENT CREATION
# ============================================================

@bot.tree.command(name="event")
async def create_event(
    interaction: discord.Interaction,
    name: str,
    date: str,
    time: str
):
    try:
        dt = datetime.datetime.strptime(
            f"{date} {time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=UTC)
    except ValueError:
        return await interaction.response.send_message("❌ Format: YYYY-MM-DD HH:MM (UTC)")

    EVENTS.append({
        "name": name,
        "datetime": dt.isoformat(),
        "channel_id": EVENT_REMINDERS_CHANNEL_ID,
        "reminded": {"1h": False, "30m": False, "5m": False, "start": False}
    })

    save_json(EVENTS_FILE, EVENTS)

    await interaction.response.send_message(
        f"✅ Event **{name}** created at {time} UTC"
    )

# ============================================================
# GAMES — TRIVIA
# ============================================================

@bot.tree.command(name="trivia")
async def trivia(interaction: discord.Interaction, category: str):
    if interaction.channel_id != GAMES_CHANNEL_ID:
        return

    if category not in TRIVIA_DB:
        return await interaction.response.send_message("❌ Category not found.")

    question = random.choice(TRIVIA_DB[category])
    msg = await interaction.channel.send(
        f"🧠 **TRIVIA — {category}**\n\n"
        f"{question['question']}\n\n"
        "🇦 🇧 🇨 🇩 (20s)"
    )

    reactions = ["🇦", "🇧", "🇨", "🇩"]
    for r in reactions:
        await msg.add_reaction(r)

    await asyncio.sleep(20)
    await interaction.channel.send(
        f"✅ **Correct answer:** {question['answer']}"
    )

    await interaction.response.send_message("Trivia launched ✅", ephemeral=True)

# ============================================================
# GAMES — TIC TAC TOE
# ============================================================

@bot.tree.command(name="tictactoe")
async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):
    if interaction.channel_id != GAMES_CHANNEL_ID:
        return

    board = ["⬜"] * 9
    players = [(interaction.user, "❌"), (opponent, "⭕")]
    turn = 0

    def render():
        return (
            f"{board[0]}{board[1]}{board[2]}\n"
            f"{board[3]}{board[4]}{board[5]}\n"
            f"{board[6]}{board[7]}{board[8]}"
        )

    msg = await interaction.channel.send(
        f"🎯 **Tic Tac Toe**\n{players[turn][0].mention}'s turn\n\n{render()}"
    )

    for emojis in ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]:
        await msg.add_reaction(emojis)

    def check_win(symbol):
        wins = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]
        return any(all(board[i] == symbol for i in w) for w in wins)

    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=60,
                check=lambda r,u: u == players[turn][0] and r.message.id == msg.id
            )
        except asyncio.TimeoutError:
            return await interaction.channel.send("⏱️ Game aborted.")

        idx = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"].index(str(reaction.emoji))
        if board[idx] != "⬜":
            continue

        board[idx] = players[turn][1]

        if check_win(players[turn][1]):
            return await interaction.channel.send(f"🏆 {players[turn][0].mention} wins!\n{render()}")

        if "⬜" not in board:
            return await interaction.channel.send(f"🤝 Draw!\n{render()}")

        turn = 1 - turn
        await msg.edit(content=f"{players[turn][0].mention}'s turn\n\n{render()}")

# ============================================================
# SCHEDULER
# ============================================================

async def scheduler():
    await bot.wait_until_ready()
    channel = bot.get_channel(EVENT_REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(UTC)

        # ----- ARENA -----
        if now.hour == 23 and now.minute == 45:
            key = now.strftime("%Y-%m-%d")
            if getattr(bot, "arena_sent", None) != key:
                await channel.send("⚔️ **Arena in 15 minutes! (00:00 UTC)**")
                bot.arena_sent = key

        # ----- BEAR TRAP -----
        if (now.date() - BEAR_TRAP_START_DATE).days % BEAR_TRAP_INTERVAL_DAYS == 0:
            for h, m in BEAR_TRAP_TIMES:
                event = now.replace(hour=h, minute=m, second=0)
                diff = int((event - now).total_seconds() / 60)

                if diff in (60, 30, 5):
                    await channel.send(f"🐻 Bear Trap in **{diff} minutes**!")
                if diff == 0:
                    await channel.send("🚨 **BEAR TRAP IS LIVE!**")

        # ----- CUSTOM EVENTS -----
        for e in EVENTS:
            dt = datetime.datetime.fromisoformat(e["datetime"])
            delta = int((dt - now).total_seconds() / 60)

            if delta == 60 and not e["reminded"]["1h"]:
                await channel.send(f"⏰ **{e['name']}** in 1h")
                e["reminded"]["1h"] = True

            if delta == 30 and not e["reminded"]["30m"]:
                await channel.send(f"⏰ **{e['name']}** in 30m")
                e["reminded"]["30m"] = True

            if delta == 5 and not e["reminded"]["5m"]:
                await channel.send(f"⏰ **{e['name']}** in 5m")
                e["reminded"]["5m"] = True

            if delta == 0 and not e["reminded"]["start"]:
                await channel.send(f"🚀 **{e['name']} STARTING NOW!**")
                e["reminded"]["start"] = True

        save_json(EVENTS_FILE, EVENTS)
        await asyncio.sleep(60)

# ============================================================
# START
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler())

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
