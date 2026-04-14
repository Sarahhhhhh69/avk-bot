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

EVENT_REMINDERS_CHANNEL_ID = 1464987172133273664
GAMES_CHANNEL_ID = 1464987164814082199

EVENTS_FILE = "events.json"
TRIVIA_FILE = "trivia.json"

UTC = datetime.timezone.utc

BEAR_TRAP_INTERVAL_DAYS = 2
BEAR_TRAP_START_DATE = datetime.date.today()

REACTIONS = ["🇦", "🇧", "🇨", "🇩"]
TRIVIA_QUESTION_COUNT = 5

# ===================== GLOBAL STATE =====================

# Anti-duplicate reminders (process-safe)
SENT_REMINDERS = set()

# ===================== TRIVIA CATEGORIES =====================

TRIVIA_CATEGORIES = [
    app_commands.Choice(name="Ref", value="Ref"),
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

# ===================== TRIVIA =====================

@bot.tree.command(name="trivia")
@app_commands.choices(category=TRIVIA_CATEGORIES)
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):

    await interaction.response.defer(ephemeral=True)
    category = category.value

    if interaction.channel_id != GAMES_CHANNEL_ID:
        return await interaction.followup.send(
            "❌ This command can only be used in the games channel."
        )

    if category not in TRIVIA_DB or not TRIVIA_DB[category]:
        return await interaction.followup.send(
            "❌ This category has no questions."
        )

    await interaction.followup.send(
        f"🧠 **Trivia Tournament — {category}** starting now!"
    )

    questions = random.sample(
        TRIVIA_DB[category],
        min(TRIVIA_QUESTION_COUNT, len(TRIVIA_DB[category]))
    )

    scores = {}
    channel = interaction.channel

    for q_index, q in enumerate(questions, start=1):
        answered = {}
        correct_order = []

        answers_text = "\n".join(
            f"{REACTIONS[i]} {a}"
            for i, a in enumerate(q["answers"])
        )

        msg = await channel.send(
            f"🧠 **Question {q_index}/{TRIVIA_QUESTION_COUNT}**\n\n"
            f"{q['question']}\n\n"
            f"{answers_text}\n\n⏱️ 10 seconds"
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
                    "reaction_add", timeout=10, check=check
                )
            except asyncio.TimeoutError:
                break

            if user.id in answered:
                continue

            choice = REACTIONS.index(str(reaction.emoji))
            answered[user.id] = choice
            if choice == q["correct"]:
                correct_order.append(user.id)

        for i, uid in enumerate(correct_order):
            scores.setdefault(uid, 0)
            scores[uid] += [5, 3, 2, 1][min(i, 3)]

        await channel.send(
            f"✅ **Correct answer:** {REACTIONS[q['correct']]} {q['answers'][q['correct']]}"
        )
        await asyncio.sleep(2)

    leaderboard = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    result = "🏆 **TRIVIA FINAL LEADERBOARD** 🏆\n\n"
    for i, (uid, pts) in enumerate(leaderboard[:3]):
        result += f"{medals[i]} <@{uid}> — {pts} pts\n"

    await channel.send(result)

# ===================== SCHEDULER =====================

async def scheduler():
    await bot.wait_until_ready()
    channel = bot.get_channel(EVENT_REMINDERS_CHANNEL_ID)

    BEAR_TRAPS = [
        {"name": "Bear Trap 2", "hour": 14},
        {"name": "Bear Trap 1", "hour": 19},
    ]

    while True:
        now = datetime.datetime.now(UTC)

        # ⚔️ ARENA
        arena_key = f"arena_{now.date()}"
        if now.hour == 23 and now.minute == 45 and arena_key not in SENT_REMINDERS:
            try:
await channel.send(
    "⚔️ **Don’t forget Arena!**\n"
    "⏳ Last **15 minutes** before it ends at **00:00 UTC**."
)
                SENT_REMINDERS.add(arena_key)
            except discord.Forbidden:
                pass

        # 🐻 BEAR TRAPS
        if (now.date() - BEAR_TRAP_START_DATE).days % BEAR_TRAP_INTERVAL_DAYS == 0:
            for trap in BEAR_TRAPS:
                event_time = now.replace(hour=trap["hour"], minute=0, second=0)
                delta = int((event_time - now).total_seconds() / 60)
                base = f"{now.date()}_{trap['name']}"

                def send_once(suffix, message):
                    key = f"{base}_{suffix}"
                    if key not in SENT_REMINDERS:
                        SENT_REMINDERS.add(key)
                        return channel.send(message)

                try:
                    if 59 <= delta <= 60:
                        await send_once("60", f"🐻 **{trap['name']}** is getting hungry… **60 minutes left!**")
                    elif 29 <= delta <= 30:
                        await send_once("30", f"🐻 **{trap['name']}** is almost ready… **30 minutes!**")
                    elif 4 <= delta <= 5:
                        await send_once("5", f"🐻 **{trap['name']}** is waking up… **5 minutes remaining!**")
                    elif delta <= 0:
                        await send_once("LIVE", f"🚨🐻 **{trap['name']} IS LIVE — FIGHT!**")
                except discord.Forbidden:
                    pass

        # 📅 CUSTOM EVENTS
        for e in EVENTS:
            dt = datetime.datetime.fromisoformat(e["datetime"])
            delta = int((dt - now).total_seconds() / 60)

            try:
                if delta == 60 and not e["reminded"]["1h"]:
                    await channel.send(f"⏰ **{e['name']} in 1 hour**")
                    e["reminded"]["1h"] = True
                elif delta == 30 and not e["reminded"]["30m"]:
                    await channel.send(f"⏰ **{e['name']} in 30 minutes**")
                    e["reminded"]["30m"] = True
                elif delta == 5 and not e["reminded"]["5m"]:
                    await channel.send(f"⏰ **{e['name']} in 5 minutes**")
                    e["reminded"]["5m"] = True
                elif delta == 0 and not e["reminded"]["start"]:
                    await channel.send(f"🚀 **{e['name']} STARTING NOW!**")
                    e["reminded"]["start"] = True
            except discord.Forbidden:
                pass

        save_json(EVENTS_FILE, EVENTS)
        await asyncio.sleep(60)

# ===================== START =====================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler())

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
