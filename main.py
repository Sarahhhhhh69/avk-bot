# ============================================================
# AVK UTILITY BOT — EVENTS + TRIVIA TOURNAMENT (FINAL)
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

# ===================== CONFIG =====================

GUILD_ID = 1463165558232186910
EVENT_REMINDERS_CHANNEL_ID = 1464987172133273664
GAMES_CHANNEL_ID = 1464987164814082199

EVENTS_FILE = "events.json"
TRIVIA_FILE = "trivia.json"

UTC = datetime.timezone.utc

BEAR_TRAP_TIMES = [(14, 0), (19, 35)]
BEAR_TRAP_INTERVAL_DAYS = 2
BEAR_TRAP_START_DATE = datetime.date.today()

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]

# ===================== TRIVIA CATEGORIES (DROPDOWN) =====================

TRIVIA_CATEGORIES = [
    app_commands.Choice(name="Fun / Memes", value="Fun/Memes"),
    app_commands.Choice(name="Cinema", value="Cinema"),
    app_commands.Choice(name="Music", value="Music"),
    app_commands.Choice(name="Sciences", value="Sciences"),
    app_commands.Choice(name="Geography", value="Geography"),
    app_commands.Choice(name="History", value="History"),
]

# ===================== BOT =====================

intents = discord.Intents(
    guilds=True,
    messages=True,
    reactions=True,
    message_content=True
)

bot = commands.Bot(command_prefix="!", intents=intents)

# ===================== HELPERS =====================

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

EVENTS = load_json(EVENTS_FILE, [])
TRIVIA_DB = load_json(TRIVIA_FILE, {})

# ===================== BASIC =====================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Bot is online.")

# ===================== EVENT CREATION =====================

@bot.tree.command(name="event")
async def create_event(interaction: discord.Interaction, name: str, date: str, time: str):
    try:
        dt = datetime.datetime.strptime(
            f"{date} {time}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=UTC)
    except ValueError:
        return await interaction.response.send_message(
            "❌ Format: YYYY-MM-DD HH:MM UTC",
            ephemeral=True
        )

    EVENTS.append({
        "name": name,
        "datetime": dt.isoformat(),
        "reminded": {"1h": False, "30m": False, "5m": False, "start": False}
    })
    save_json(EVENTS_FILE, EVENTS)

    await interaction.response.send_message(
        f"✅ Event **{name}** created.",
        ephemeral=True
    )

# ===================== TRIVIA TOURNAMENT =====================

@bot.tree.command(name="trivia", description="Start a Trivia Tournament")
@app_commands.choices(category=TRIVIA_CATEGORIES)
async def trivia(
    interaction: discord.Interaction,
    category: app_commands.Choice[str]
):
    category = category.value

    if interaction.channel_id != GAMES_CHANNEL_ID:
        return await interaction.response.send_message(
            "❌ This command can only be used in the games channel.",
            ephemeral=True
        )

    if category not in TRIVIA_DB:
        return await interaction.response.send_message(
            "❌ Category not found.",
            ephemeral=True
        )

    await interaction.response.send_message(
        f"🧠 **Trivia Tournament — {category}**\n20 questions incoming…",
        ephemeral=True
    )

    questions = random.sample(TRIVIA_DB[category], 20)
    scores = {}

    channel = interaction.channel

    for q_index, q in enumerate(questions, start=1):
        answered = {}
        correct_order = []

        msg = await channel.send(
            f"🧠 **Question {q_index}/20**\n\n"
            f"{q['question']}\n\n"
            "🇦 🇧 🇨 🇩  (10s)"
        )

        for r in REACTIONS:
            await msg.add_reaction(r)

        def check(reaction, user):
            return (
                reaction.message.id == msg.id
                and str(reaction.emoji) in REACTIONS
                and not user.bot
            )

        start = datetime.datetime.now(UTC)

        while (datetime.datetime.now(UTC) - start).seconds < 10:
            try:
                reaction, user = await bot.wait_for(
                    "reaction_add",
                    timeout=10,
                    check=check
                )
            except asyncio.TimeoutError:
                break

            if user.id in answered:
                continue

            chosen = REACTIONS.index(str(reaction.emoji))
            answered[user.id] = chosen

            if chosen == q["correct"]:
                correct_order.append(user.id)

        # Scoring
        for idx, uid in enumerate(correct_order):
            scores.setdefault(uid, 0)
            if idx == 0:
                scores[uid] += 5
            elif idx == 1:
                scores[uid] += 3
            elif idx == 2:
                scores[uid] += 2
            else:
                scores[uid] += 1

        correct_letter = REACTIONS[q["correct"]]
        await channel.send(f"✅ **Correct answer:** {correct_letter}")
        await asyncio.sleep(2)

    # ===================== FINAL LEADERBOARD =====================

    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    if not leaderboard:
        return await channel.send("😢 No correct answers this time!")

    result = "🏆 **TRIVIA FINAL LEADERBOARD** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (uid, pts) in enumerate(leaderboard[:3]):
        member = channel.guild.get_member(uid)
        name = member.display_name if member else "Unknown"
        result += f"{medals[i]} **{name}** — {pts} pts\n"

    await channel.send(result)

# ===================== SCHEDULER =====================

async def scheduler():
    await bot.wait_until_ready()
    channel = bot.get_channel(EVENT_REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(UTC)

        # ARENA
        if now.hour == 23 and now.minute == 45:
            key = now.strftime("%Y-%m-%d")
            if getattr(bot, "arena_sent", None) != key:
                await channel.send("⚔️ **Arena in 15 minutes! (00:00 UTC)**")
                bot.arena_sent = key

        # BEAR TRAP
        if (now.date() - BEAR_TRAP_START_DATE).days % BEAR_TRAP_INTERVAL_DAYS == 0:
            for h, m in BEAR_TRAP_TIMES:
                event = now.replace(hour=h, minute=m, second=0)
                delta = int((event - now).total_seconds() / 60)

                if delta in (60, 30, 5):
                    await channel.send(f"🐻 **Bear Trap in {delta} minutes**")
                if delta == 0:
                    await channel.send("🚨 **BEAR TRAP IS LIVE!**")

        # CUSTOM EVENTS
        for e in EVENTS:
            dt = datetime.datetime.fromisoformat(e["datetime"])
            delta = int((dt - now).total_seconds() / 60)

            if delta == 60 and not e["reminded"]["1h"]:
                await channel.send(f"⏰ **{e['name']} in 1 hour**")
                e["reminded"]["1h"] = True

            if delta == 30 and not e["reminded"]["30m"]:
                await channel.send(f"⏰ **{e['name']} in 30 minutes**")
                e["reminded"]["30m"] = True

            if delta == 5 and not e["reminded"]["5m"]:
                await channel.send(f"⏰ **{e['name']} in 5 minutes**")
                e["reminded"]["5m"] = True

            if delta == 0 and not e["reminded"]["start"]:
                await channel.send(f"🚀 **{e['name']} STARTING NOW!**")
                e["reminded"]["start"] = True

        save_json(EVENTS_FILE, EVENTS)
        await asyncio.sleep(60)

# ===================== START =====================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler())

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
