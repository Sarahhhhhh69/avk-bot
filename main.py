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

# -----------------------
# KEEP ALIVE (Render)
# -----------------------
from keep_alive import keep_alive
keep_alive()

# -----------------------
# INTENTS & BOT
# -----------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

GUILD_ID = 1463165558232186910  # ✅ AVK server
REMINDERS_CHANNEL_ID = 1464987172133273664  # ✅ #event-reminders
bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# ✅ BASIC COMMANDS
# ============================================================

@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Pong! The bot is running smoothly!")

@bot.tree.command(name="help", description="Show the list of commands.")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📘 AVK BOT — Help",
        description="Available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/ping", value="Check bot status", inline=False)
    embed.add_field(name="/event", value="Create an event with reminders", inline=False)
    embed.add_field(name="/trivia", value="Trivia game", inline=False)
    embed.add_field(name="/hangman", value="Hangman game", inline=False)
    embed.add_field(name="/connect4", value="Connect Four (PvP)", inline=False)
    embed.add_field(name="/tictactoe", value="TicTacToe (PvP)", inline=False)
    embed.add_field(name="/duel", value="Simple duel", inline=False)
    embed.add_field(name="/quiplash", value="Quiplash (simple)", inline=False)
    await interaction.response.send_message(embed=embed)

# ============================================================
# ✅ TRIVIA
# ============================================================

TRIVIA_QUESTIONS = [
    ("What is AVK’s primary language?", "english"),
    ("Which season is the coldest?", "winter"),
    ("What color is snow?", "white"),
    ("Which animal represents AVK?", "wolf"),
]

@bot.tree.command(name="trivia", description="Start a trivia question.")
async def trivia(interaction: discord.Interaction):
    question, answer = random.choice(TRIVIA_QUESTIONS)
    await interaction.response.send_message(f"❓ **Trivia Time!**\n\n{question}")

    def check(msg):
        return msg.channel == interaction.channel and not msg.author.bot

    try:
        msg = await bot.wait_for("message", timeout=20, check=check)
        if msg.content.lower().strip() == answer.lower():
            await interaction.followup.send(f"✅ Correct, {msg.author.mention}!")
        else:
            await interaction.followup.send(f"❌ Wrong. Correct answer: **{answer}**")
    except asyncio.TimeoutError:
        await interaction.followup.send(f"⌛ Time’s up! Answer was **{answer}**")

# ============================================================
# ✅ BEAR TRAP — Start 4 April 2026, every 2 days (14:00 & 20:00 UTC)
# ============================================================

async def beartrap_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    SCHEDULE_UTC = [(14, 0), (20, 0)]
    START_DATE = datetime.date(2026, 4, 4)

    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        days_since = (now.date() - START_DATE).days

        if days_since < 0 or days_since % 2 != 0:
            await asyncio.sleep(3600)
            continue

        for h, m in SCHEDULE_UTC:
            target = now.replace(hour=h, minute=m, second=0, microsecond=0)
            if target <= now:
                continue
            await asyncio.sleep((target - now).total_seconds())
            if bot.is_ready() and channel:
                await channel.send("🐻❄️ **BEAR TRAP NOW!** Prepare yourselves AVK warriors! 🐺")

        await asyncio.sleep(60)

# ============================================================
# ✅ ARENA DAILY — “ENDS IN 15 MINUTES” + START
# ============================================================

async def arena_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(datetime.timezone.utc)

        # Reminder: Arena ends in 15 minutes (23:45 UTC)
        end_soon_time = now.replace(hour=23, minute=45, second=0, microsecond=0)
        if end_soon_time <= now:
            end_soon_time += datetime.timedelta(days=1)

        await asyncio.sleep((end_soon_time - now).total_seconds())
        if bot.is_ready() and channel:
            await channel.send("⚔️ **Arena ends in 15 minutes!** Finish your fights!")

        # Arena start (00:00 UTC)
        start_time = end_soon_time + datetime.timedelta(minutes=15)
        await asyncio.sleep((start_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
        if bot.is_ready() and channel:
            await channel.send("⚔️ **Arena is starting NOW!** Good luck fighters!")

# ============================================================
# ✅ EVENT REMINDERS (RAM-based)
# ============================================================

EVENTS = {}

@bot.tree.command(name="event", description="Create an event with reminders (UTC).")
@app_commands.describe(name="Event name", date="YYYY-MM-DD", time="HH:MM UTC")
async def event_cmd(interaction: discord.Interaction, name: str, date: str, time: str):
    try:
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return await interaction.response.send_message("❌ Invalid date/time format.")

    if dt <= datetime.datetime.now(datetime.timezone.utc):
        return await interaction.response.send_message("❌ Event must be in the future.")

    channel_id = interaction.channel_id
    EVENTS.setdefault(channel_id, []).append({"name": name, "dt": dt.isoformat()})

    await interaction.response.send_message(
        f"✅ **Event created!**\n📌 {name}\n🗓️ {date} at {time} UTC\n🔔 Reminders: 1h • 30m • 5m • start"
    )

    bot.loop.create_task(handle_event_reminders(channel_id, name, dt))

async def handle_event_reminders(channel_id: int, name: str, dt: datetime.datetime):
    channel = bot.get_channel(channel_id)
    checkpoints = [
        ("1 hour", dt - datetime.timedelta(hours=1)),
        ("30 minutes", dt - datetime.timedelta(minutes=30)),
        ("5 minutes", dt - datetime.timedelta(minutes=5)),
        ("NOW", dt),
    ]

    for label, t in checkpoints:
        wait = (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
        if wait > 0:
            await asyncio.sleep(wait)
        if bot.is_ready() and channel:
            if label == "NOW":
                await channel.send(f"🚀 **{name} is starting NOW!**")
            else:
                await channel.send(f"⏰ **{name} starts in {label}!**")

# ============================================================
# ✅ MINI-GAMES (unchanged)
# ============================================================

@bot.tree.command(name="hangman", description="Play Hangman.")
async def hangman_cmd(interaction: discord.Interaction):
    words = ["winter", "survival", "frost"]
    word = random.choice(words)
    guessed, lives = [], 6

    def masked():
        return " ".join(c if c in guessed else "_" for c in word)

    await interaction.response.send_message(f"🎮 **Hangman**\n`{masked()}`\nLives: {lives}")

    def check(msg):
        return msg.channel == interaction.channel and len(msg.content) == 1 and msg.content.isalpha()

    while lives > 0:
        try:
            msg = await bot.wait_for("message", timeout=40, check=check)
            letter = msg.content.lower()
            if letter in guessed:
                continue
            guessed.append(letter)
            if letter not in word:
                lives -= 1
            if "_" not in masked():
                return await interaction.followup.send(f"✅ You won! Word: **{word}**")
            await interaction.followup.send(f"`{masked()}` Lives: {lives}")
        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Game over.")

# ============================================================
# ✅ SETUP HOOK — start loops
# ============================================================

@bot.event
async def setup_hook():
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"Sync error: {e}")

    bot.loop.create_task(beartrap_loop())
    bot.loop.create_task(arena_loop())

# ============================================================
# ✅ START BOT
# ============================================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ Missing DISCORD_BOT_TOKEN")
else:
    bot.run(TOKEN)
