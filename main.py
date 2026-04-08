# ============================================================
# AVK UTILITY BOT — STABLE REMINDER VERSION
# ============================================================

import os
import json
import asyncio
import datetime
import discord
from discord.ext import commands
from discord import app_commands

from keep_alive import keep_alive
keep_alive()

# ============================================================
# CONFIG
# ============================================================

GUILD_ID = 1463165558232186910
REMINDERS_CHANNEL_ID = 1464987172133273664
EVENTS_FILE = "events.json"

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        messages=True,
        message_content=True,
        members=True
    )
)

UTC = datetime.timezone.utc

TODAY_BT_TIMES = [(14, 0), (19, 35)]  # ✅ today only

# ============================================================
# LOAD / SAVE EVENTS (JSON)
# ============================================================

def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)

EVENTS = load_events()

# ============================================================
# BASIC COMMANDS
# ============================================================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

@bot.tree.command(name="event")
@app_commands.describe(name="Event name", date="YYYY-MM-DD", time="HH:MM UTC")
async def event_cmd(interaction: discord.Interaction, name: str, date: str, time: str):
    try:
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
    except ValueError:
        return await interaction.response.send_message("❌ Invalid date/time format.")

    EVENTS.append({
        "name": name,
        "datetime": dt.isoformat(),
        "reminded": {
            "1h": False,
            "30m": False,
            "5m": False,
            "start": False
        },
        "channel_id": interaction.channel_id
    })

    save_events(EVENTS)

    await interaction.response.send_message(
        f"✅ **Event created**\n"
        f"📌 {name}\n"
        f"🕒 {time} UTC\n"
        f"🔔 Reminders: 1h / 30m / 5m / start"
    )

# ============================================================
# GLOBAL SCHEDULER — RUNS EVERY MINUTE
# ============================================================

async def scheduler_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(UTC)

        # ---------- ARENA ----------
        if now.hour == 23 and now.minute == 45:
            today_key = now.strftime("%Y-%m-%d")
            if not hasattr(bot, "arena_sent") or bot.arena_sent != today_key:
                if channel:
                    await channel.send(
                        "⚔️ **Arena ends in 15 minutes!** Finish your fights!"
                    )
                bot.arena_sent = today_key

        # ---------- BEAR TRAP (TODAY ONLY) ----------
        if now.date() == datetime.date.today():
            for h, m in TODAY_BT_TIMES:
                if now.hour == h and now.minute == m:
                    if channel:
                        await channel.send(
                            "🐻❄️ **BEAR TRAP NOW!** Prepare yourselves AVK warriors!"
                        )

        # ---------- EVENTS ----------
        for event in EVENTS[:]:
            event_dt = datetime.datetime.fromisoformat(event["datetime"])
            delta = int((event_dt - now).total_seconds() / 60)

            evt_channel = bot.get_channel(event["channel_id"])

            if delta == 60 and not event["reminded"]["1h"]:
                await evt_channel.send(f"⏰ **{event['name']}** starts in 1 hour!")
                event["reminded"]["1h"] = True

            if delta == 30 and not event["reminded"]["30m"]:
                await evt_channel.send(f"⏰ **{event['name']}** starts in 30 minutes!")
                event["reminded"]["30m"] = True

            if delta == 5 and not event["reminded"]["5m"]:
                await evt_channel.send(f"⏰ **{event['name']}** starts in 5 minutes!")
                event["reminded"]["5m"] = True

            if delta == 0 and not event["reminded"]["start"]:
                await evt_channel.send(f"🚀 **{event['name']}** is starting NOW!")
                event["reminded"]["start"] = True
                save_events(EVENTS)

        await asyncio.sleep(60)

# ============================================================
# STARTUP
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler_loop())

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Missing DISCORD_BOT_TOKEN")
