# ============================================================
# AVK UTILITY BOT — EVENTS + TRIVIA TOURNAMENT (STABLE)
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

SENT_REMINDERS = set()

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
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
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
    await interaction.response.send_message(f"✅ Event **{name}** created.", ephemeral=True)

# ===================== TRIVIA =====================

@bot.tree.command(name="trivia")
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):

    await interaction.response.defer(ephemeral=True)
    category = category.value

    if interaction.channel_id != GAMES_CHANNEL_ID:
        return await interaction.followup.send("❌ Use this command in the games channel.")

    if category not in TRIVIA_DB or not TRIVIA_DB[category]:
        return await interaction.followup.send("❌ This category has no questions.")

    await interaction.followup.send(f"🧠 **Trivia Tournament — {category}** starting now!")

# ===================== SCHEDULER =====================

async def scheduler():
    await bot.wait_until_ready()
    channel = bot.get_channel(EVENT_REMINDERS_CHANNEL_ID)

    BEAR_TRAPS = [
        {"name": "Bear Trap 2", "hour": 13, "minute": 30},
        {"name": "Bear Trap 1", "hour": 18, "minute": 10},
    ]

    while True:
        now = datetime.datetime.now(UTC)

        # ⚔️ ARENA (daily, ends at 00:00 UTC)
        arena_key = f"arena_{now.date()}"
        if now.hour == 23 and now.minute == 45 and arena_key not in SENT_REMINDERS:
            SENT_REMINDERS.add(arena_key)
            await channel.send(
                "@everyone\n⚔️ **Don't forget Arena!**\n"
                "⏳ Last **15 minutes** before it ends at **00:00 UTC**."
            )

        # 🐻 BEAR TRAPS (every 2 days)
        if (now.date() - BEAR_TRAP_START_DATE).days % BEAR_TRAP_INTERVAL_DAYS == 0:
            for trap in BEAR_TRAPS:
                event_time = now.replace(
                    hour=trap["hour"],
                    minute=trap["minute"],
                    second=0
                )
                delta = int((event_time - now).total_seconds() / 60)
                base = f"{now.date()}_{trap['name']}"

                def send(suffix, msg):
                    key = f"{base}_{suffix}"
                    if key not in SENT_REMINDERS:
                        SENT_REMINDERS.add(key)
                        return msg
                    return None

                if 59 <= delta <= 60:
                    msg = send("60", f"🐻 **{trap['name']}** — 60 minutes left!")
                    if msg: await channel.send(msg)

                elif 29 <= delta <= 30:
                    msg = send("30", f"🐻 **{trap['name']}** — 30 minutes left!")
                    if msg: await channel.send(msg)

                elif 4 <= delta <= 5:
                    msg = send("5", f"🐻 **{trap['name']}** — 5 minutes remaining!")
                    if msg: await channel.send(msg)

                elif delta <= 0:
                    msg = send("LIVE", f"@everyone\n🚨🐻 **{trap['name']} IS LIVE — FIGHT!**")
                    if msg: await channel.send(msg)

        # 📅 CUSTOM EVENTS
        for e in EVENTS:
            dt = datetime.datetime.fromisoformat(e["datetime"])
            delta = int((dt - now).total_seconds() / 60)

            if delta == 60 and not e["reminded"]["1h"]:
                await channel.send(f"⏰ **{e['name']} in 1 hour**")
                e["reminded"]["1h"] = True

            elif delta == 30 and not e["reminded"]["30m"]:
                await channel.send(f"⏰ **{e['name']} in 30 minutes**")
                e["reminded"]["30m"] = True

            elif delta == 5 and not e["reminded"]["5m"]:
                await channel.send(f"⏰ **{e['name']} in 5 minutes**")
                e["reminded"]["5m"] = True

            elif delta <= 0 and not e["reminded"]["start"]:
                await channel.send(f"@everyone\n🚀 **{e['name']} STARTING NOW!**")
                e["reminded"]["start"] = True

        save_json(EVENTS_FILE, EVENTS)
        await asyncio.sleep(60)

# ===================== START =====================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler())

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
