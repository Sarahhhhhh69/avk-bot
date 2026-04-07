# ============================================================
# ===============   AVK BOT — MAIN FILE ONLY   ===============
# ============================================================

import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import datetime
import random

# ============================================================
# KEEP ALIVE (Render)
# ============================================================
from keep_alive import keep_alive
keep_alive()

# ============================================================
# BOT SETUP
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

GUILD_ID = 1463165558232186910
REMINDERS_CHANNEL_ID = 1464987172133273664  # ✅ #event-reminders

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# BASIC COMMANDS
# ============================================================

@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Pong! AVK Utility Bot is online.")

@bot.tree.command(name="help", description="Show available commands.")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**AVK Utility Bot Commands**\n"
        "/ping – Check bot status\n"
        "/event – Create an event with reminders\n"
        "/trivia – Trivia game\n"
        "/hangman – Hangman game\n"
    )

# ============================================================
# TRIVIA
# ============================================================

TRIVIA_QUESTIONS = [
    ("What is AVK’s primary language?", "english"),
    ("Which season is the coldest?", "winter"),
    ("Which animal represents AVK?", "wolf"),
]

@bot.tree.command(name="trivia", description="Start a trivia question.")
async def trivia(interaction: discord.Interaction):
    question, answer = random.choice(TRIVIA_QUESTIONS)
    await interaction.response.send_message(f"❓ **Trivia Time!**\n{question}")

    def check(msg):
        return msg.channel == interaction.channel and not msg.author.bot

    try:
        msg = await bot.wait_for("message", timeout=20, check=check)
        if msg.content.lower().strip() == answer:
            await interaction.followup.send(f"✅ Correct, {msg.author.mention}!")
        else:
            await interaction.followup.send(f"❌ Wrong. Correct answer: **{answer}**")
    except asyncio.TimeoutError:
        await interaction.followup.send(f"⌛ Time’s up! Answer was **{answer}**")

# ============================================================
# BEAR TRAP — Start 4 April 2026 / Every 2 days / 14:00 & 20:00
# ============================================================

async def beartrap_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    START_DATE = datetime.date(2026, 4, 4)
    SCHEDULE_UTC = [(14, 0), (20, 0)]

    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        days_since = (now.date() - START_DATE).days

        if days_since < 0 or days_since % 2 != 0:
            await asyncio.sleep(3600)
            continue

        for hour, minute in SCHEDULE_UTC:
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                continue
            await asyncio.sleep((target - now).total_seconds())
            if channel:
                await channel.send("🐻❄️ **BEAR TRAP NOW!** Prepare yourselves AVK warriors!")

        await asyncio.sleep(60)

# ============================================================
# ARENA — DAILY REMINDER ONLY (ENDS IN 15 MINUTES)
# ============================================================

async def arena_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(datetime.timezone.utc)

        reminder_time = now.replace(hour=23, minute=45, second=0, microsecond=0)
        if reminder_time <= now:
            reminder_time += datetime.timedelta(days=1)

        await asyncio.sleep((reminder_time - now).total_seconds())

        if channel:
            await channel.send("⚔️ **Arena ends in 15 minutes!** Finish your fights!")

        await asyncio.sleep(60)

# ============================================================
# EVENT REMINDERS (RAM-ONLY)
# ============================================================

EVENTS = {}

@bot.tree.command(name="event", description="Create an event with reminders (UTC).")
@app_commands.describe(name="Event name", date="YYYY-MM-DD", time="HH:MM")
async def event_cmd(interaction: discord.Interaction, name: str, date: str, time: str):
    try:
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return await interaction.response.send_message("❌ Invalid date/time format.")

    if dt <= datetime.datetime.now(datetime.timezone.utc):
        return await interaction.response.send_message("❌ Event must be in the future.")

    await interaction.response.send_message(
        f"✅ **Event created!**\n📌 {name}\n🕒 {time} UTC\n🔔 Reminders: 1h · 30m · 5m · start"
    )

    bot.loop.create_task(handle_event_reminders(interaction.channel_id, name, dt))

async def handle_event_reminders(channel_id: int, name: str, dt: datetime.datetime):
    channel = bot.get_channel(channel_id)

    reminders = [
        ("1 hour", dt - datetime.timedelta(hours=1)),
        ("30 minutes", dt - datetime.timedelta(minutes=30)),
        ("5 minutes", dt - datetime.timedelta(minutes=5)),
        ("NOW", dt),
    ]

    for label, t in reminders:
        wait = (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
        if wait > 0:
            await asyncio.sleep(wait)
        if channel:
            if label == "NOW":
                await channel.send(f"🚀 **{name} is starting NOW!**")
            else:
                await channel.send(f"⏰ **{name} starts in {label}!**")

# ============================================================
# SETUP HOOK
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(beartrap_loop())
    bot.loop.create_task(arena_loop())

# ============================================================
# START BOT
# ============================================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_BOT_TOKEN missing")
