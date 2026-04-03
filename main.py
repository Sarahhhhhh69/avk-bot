# ============================================================
# ===============   AVK BOT — MAIN FILE ONLY   ===============
# ============================================================

import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import datetime
import pytz
import random

# -----------------------
# KEEP ALIVE (Render/Flask)
# -----------------------
from keep_alive import keep_alive
keep_alive()

# -----------------------
# INTENTS & BOT
# -----------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

GUILD_ID = 1463165558232186910  # ✅ Ton serveur AVK
bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# ✅ COMMANDES D’INFORMATION
# ============================================================

@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Pong! The bot is running smoothly!")

@bot.tree.command(name="help", description="Show the list of commands.")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📘 AVK BOT — Help Menu",
        description="Here are all available commands and features:",
        color=discord.Color.blue()
    )
    embed.add_field(name="🧊 /ping", value="Check if the bot is alive", inline=False)
    embed.add_field(name="🧠 /trivia", value="Start an AVK trivia question", inline=False)
    embed.add_field(name="🎮 /connect4", value="Play Connect4", inline=False)
    embed.add_field(name="🧩 /tictactoe", value="Play TicTacToe", inline=False)
    embed.add_field(name="😵 /hangman", value="Play Hangman", inline=False)
    embed.add_field(name="⚔️ /duel", value="Start a duel against someone", inline=False)
    embed.add_field(name="🎤 /quiplash", value="Start a Quiplash round", inline=False)
    embed.add_field(name="📆 /event", value="Create an event with reminders (UTC)", inline=False)
    embed.add_field(name="📜 /rules", value="Show AVK rules", inline=False)
    embed.add_field(name="🔗 /links", value="Useful links", inline=False)
    embed.add_field(name="❄️ /about", value="About AVK bot", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="about", description="Information about AVK BOT.")
async def about_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❄️ About AVK BOT",
        description=(
            "This bot was created for the **AVK Alliance**.\n"
            "It includes games, reminders, BearTrap automation, trivia,\n"
            "and custom features to support the AVK community."
        ),
        color=discord.Color.purple()
    )
    embed.set_footer(text="Made with ❤️ for AVK")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rules", description="Show the AVK rules.")
async def rules_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 AVK Rules",
        description=(
            "1️⃣ Be respectful\n"
            "2️⃣ English only\n"
            "3️⃣ No spam or harassment\n"
            "4️⃣ Follow leadership directions\n"
            "5️⃣ No cheating\n"
            "6️⃣ Protect the community\n"
            "7️⃣ Respect event planning & timings\n"
        ),
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="links", description="Show useful AVK links.")
async def links_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔗 Useful Links",
        description=(
            "**AVK Discord Invite** : https://discord.gg/VH4wHwUwJe\n"
            "**Whiteout Survival** : https://www.whiteoutsurvival.com/\n"
        ),
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

# ============================================================
# ✅ TRIVIA AVK
# ============================================================

TRIVIA_QUESTIONS = [
    ("What is AVK’s primary language?", "english"),
    ("Which season is the coldest?", "winter"),
    ("What color is snow?", "white"),
    ("What is the leader of AVK called?", "chieftain"),
    ("Which animal represents AVK?", "wolf"),
    ("What is needed to trigger Bear Trap?", "activity"),
    ("How many alliances form AVK?", "one"),
    ("Which day does Bear Trap trigger on?", "odd"),
    ("What does AVK stand for?", "alliance"),
    ("What climate dominates Whiteout Survival?", "frozen"),
    ("Name a resource starting with F.", "food"),
    ("Name a resource starting with W.", "wood"),
    ("Which building trains soldiers?", "barracks"),
]

@bot.tree.command(name="trivia", description="Start an AVK trivia question.")
async def trivia(interaction: discord.Interaction):

    question, correct_answer = random.choice(TRIVIA_QUESTIONS)

    await interaction.response.send_message(
        f"❓ **Trivia Time!**\n\n{question}\n✍️ *20 seconds to answer!*"
    )

    def check(msg):
        return msg.channel == interaction.channel and not msg.author.bot

    try:
        msg = await bot.wait_for("message", timeout=20, check=check)

        if msg.content.lower().strip() == correct_answer.lower():
            await interaction.followup.send(f"✅ Correct! Well played, {msg.author.mention}! 💙")
        else:
            await interaction.followup.send(f"❌ Wrong! The correct answer was **{correct_answer}**.")

    except asyncio.TimeoutError:
        await interaction.followup.send(f"⌛ Time’s up! Correct answer: **{correct_answer}**.")

# ============================================================
# ✅ BEAR TRAP — Début fixe 4 avril 2026 → tous les 2 jours
# ============================================================

async def beartrap_loop():
    await bot.wait_until_ready()

    channel_id = 1463165559171584033  # ✅ Ton canal BearTrap AVK
    channel = bot.get_channel(channel_id)

    SCHEDULE_UTC = [(14, 0), (20, 0)]
    START_DATE = datetime.date(2026, 4, 4)

    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        today = now.date()

        days_since_start = (today - START_DATE).days

        # Si aujourd’hui < 4 avril → attendre 4 avril 14:00
        if days_since_start < 0:
            target = datetime.datetime(2026, 4, 4, 14, 0, tzinfo=datetime.timezone.utc)
            wait = (target - now).total_seconds()
            print(f"⏳ BearTrap commencera le 4 avril à 14:00 UTC")
            await asyncio.sleep(max(0, wait))
            continue

        # BT tous les deux jours : 0,2,4,6...
        is_beartrap_day = (days_since_start % 2 == 0)

        if not is_beartrap_day:
            await asyncio.sleep(3600)
            continue

        # Aujourd’hui est un jour BearTrap
        for hour, minute in SCHEDULE_UTC:
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if target <= now:
                continue

            wait = (target - now).total_seconds()
            print(f"⏳ Prochain BearTrap : {target} UTC")
            await asyncio.sleep(wait)

            if bot.is_ready() and channel:
                await channel.send(
                    "🐻❄️ **BEAR TRAP NOW!**\nPrepare yourselves AVK warriors — the hunt begins! 🐺"
                )

        await asyncio.sleep(60)

# ============================================================
# ✅ EVENT REMINDERS (1h / 30m / 5m / start)
# ============================================================

EVENTS = {}

@bot.tree.command(name="event", description="Create an event with automatic reminders (UTC).")
@app_commands.describe(
    name="Event name",
    date="YYYY-MM-DD",
    time="HH:MM (UTC)"
)
async def event_cmd(interaction: discord.Interaction, name: str, date: str, time: str):

    try:
        event_dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        event_dt = event_dt.replace(tzinfo=datetime.timezone.utc)
    except:
        return await interaction.response.send_message("❌ Invalid date/time format.", ephemeral=True)

    now = datetime.datetime.now(datetime.timezone.utc)
    if event_dt <= now:
        return await interaction.response.send_message("❌ Event must be in the future.", ephemeral=True)

    channel_id = interaction.channel_id

    if channel_id not in EVENTS:
        EVENTS[channel_id] = []

    EVENTS[channel_id].append({"name": name, "datetime": event_dt.isoformat()})

    await interaction.response.send_message(
        f"✅ **Event created!**\n📌 {name}\n🗓️ {date} at {time} UTC\n🔔 Reminders: 1h • 30m • 5m • start"
    )

    bot.loop.create_task(handle_event_reminders(channel_id, name, event_dt))


async def handle_event_reminders(channel_id: int, name: str, event_dt):
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    reminder_times = {
        "1h":  event_dt - datetime.timedelta(hours=1),
        "30m": event_dt - datetime.timedelta(minutes=30),
        "5m":  event_dt - datetime.timedelta(minutes=5),
        "start": event_dt
    }

    for label, target_time in reminder_times.items():
        now = datetime.datetime.now(datetime.timezone.utc)
        wait = (target_time - now).total_seconds()

        if wait > 0:
            await asyncio.sleep(wait)

        if not bot.is_ready():
            return

        if label == "1h":
            await channel.send(f"⏰ **{name} starts in 1 hour!** (UTC)")
        elif label == "30m":
            await channel.send(f"⏰ **{name} starts in 30 minutes!** (UTC)")
        elif label == "5m":
            await channel.send(f"⏰ **{name} starts in 5 minutes!** (UTC)")
        elif label == "start":
            await channel.send(f"🚀 **{name} is starting NOW!**")

# ============================================================
# ✅ CONNECT4 — FULL
# ============================================================

CONNECT4_EMPTY = "⚪"
CONNECT4_RED = "🔴"
CONNECT4_YELLOW = "🟡"

def create_connect4_board():
    return [[CONNECT4_EMPTY for _ in range(7)] for _ in range(6)]

def drop_piece(board, col, piece):
    for row in reversed(board):
        if row[col] == CONNECT4_EMPTY:
            row[col] = piece
            return True
    return False

def render_board(board):
    return "\n".join("".join(row) for row in board)

def check_win(board, piece):
    for r in range(6):
        for c in range(4):
            if all(board[r][c+i] == piece for i in range(4)):
                return True

    for r in range(3):
        for c in range(7):
            if all(board[r+i][c] == piece for i in range(4)):
                return True

    for r in range(3):
        for c in range(4):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True

    for r in range(3, 6):
        for c in range(4):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True

    return False

@bot.tree.command(name="connect4", description="Play Connect 4.")
async def connect4_cmd(interaction: discord.Interaction, opponent: discord.Member):

    if opponent.bot:
        return await interaction.response.send_message("❌ Cannot play against bots.")
    if opponent == interaction.user:
        return await interaction.response.send_message("❌ You cannot play against yourself.")

    board = create_connect4_board()
    players = [interaction.user, opponent]
    pieces = [CONNECT4_RED, CONNECT4_YELLOW]
    turn = 0

    await interaction.response.send_message(
        f"🎮 **Connect4** — {players[0].mention} vs {players[1].mention}\n"
        f"{render_board(board)}\n"
        f"👉 {players[turn].mention}, choose a column (0–6)."
    )

    while True:
        def check(msg):
            return (
                msg.channel == interaction.channel and
                msg.author == players[turn] and
                msg.content.isdigit() and
                0 <= int(msg.content) <= 6
            )

        try:
            msg = await bot.wait_for("message", timeout=40, check=check)
            col = int(msg.content)

            if not drop_piece(board, col, pieces[turn]):
                await interaction.followup.send("❌ Column full, choose another one.")
                continue

            if check_win(board, pieces[turn]):
                return await interaction.followup.send(
                    f"{render_board(board)}\n🏆 **{players[turn].mention} wins!** 🎉"
                )

            turn = 1 - turn
            await interaction.followup.send(
                f"{render_board(board)}\n👉 {players[turn].mention}, your turn!"
            )

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Timeout — game ended.")

# ============================================================
# ✅ TIC TAC TOE
# ============================================================

TICTACTOE_EMPTY = "➖"
TICTACTOE_X = "❌"
TICTACTOE_O = "⭕"

def create_ttt_board():
    return [[TICTACTOE_EMPTY for _ in range(3)] for _ in range(3)]

def ttt_winner(board, p):
    for i in range(3):
        if all(board[i][j] == p for j in range(3)): return True
        if all(board[j][i] == p for j in range(3)): return True
    if all(board[i][i] == p for i in range(3)): return True
    if all(board[i][2-i] == p for i in range(3)): return True
    return False

def render_ttt(board):
    return "\n".join("".join(row) for row in board)

@bot.tree.command(name="tictactoe", description="Play TicTacToe.")
async def tictactoe_cmd(interaction: discord.Interaction, opponent: discord.Member):

    if opponent.bot:
        return await interaction.response.send_message("❌ Cannot play against bots.")
    if opponent == interaction.user:
        return await interaction.response.send_message("❌ You cannot play against yourself.")

    board = create_ttt_board()
    players = [interaction.user, opponent]
    pieces = [TICTACTOE_X, TICTACTOE_O]
    turn = 0

    await interaction.response.send_message(
        f"🎮 **TicTacToe** — {players[0].mention} vs {players[1].mention}\n"
        f"{render_ttt(board)}\n"
        f"👉 {players[turn].mention}, play using `row col` (0–2)."
    )

    while True:
        def check(msg):
            return (
                msg.channel == interaction.channel and
                msg.author == players[turn] and
                len(msg.content.split()) == 2 and
                all(x.isdigit() for x in msg.content.split())
            )

        try:
            msg = await bot.wait_for("message", timeout=40, check=check)
            r, c = map(int, msg.content.split())

            if not (0 <= r < 3 and 0 <= c < 3):
                await interaction.followup.send("❌ Invalid move.")
                continue

            if board[r][c] != TICTACTOE_EMPTY:
                await interaction.followup.send("❌ Cell already used.")
                continue

            board[r][c] = pieces[turn]

            if ttt_winner(board, pieces[turn]):
                return await interaction.followup.send(
                    f"{render_ttt(board)}\n🥇 **{players[turn].mention} wins!**"
                )

            turn = 1 - turn
            await interaction.followup.send(
                f"{render_ttt(board)}\n👉 {players[turn].mention}, your turn."
            )

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Timeout — game ended.")

# ============================================================
# ✅ DUEL
# ============================================================

@bot.tree.command(name="duel", description="Challenge someone to a duel!")
async def duel_cmd(interaction: discord.Interaction, opponent: discord.Member):
    if opponent.bot:
        return await interaction.response.send_message("❌ Cannot duel bots.")
    if opponent == interaction.user:
        return await interaction.response.send_message("❌ You cannot duel yourself 😂")

    winner = random.choice([interaction.user, opponent])
    await interaction.response.send_message(
        f"⚔️ **Duel Started!**\n{interaction.user.mention} vs {opponent.mention}\n\n"
        f"🏆 **Winner: {winner.mention}!**"
    )

# ============================================================
# ✅ HANGMAN
# ============================================================

HANGMAN_WORDS = ["winter", "survival", "frost", "blizzard", "viking", "shield"]

@bot.tree.command(name="hangman", description="Play Hangman.")
async def hangman_cmd(interaction: discord.Interaction):

    word = random.choice(HANGMAN_WORDS)
    guessed = []
    lives = 6

    def masked():
        return " ".join(c if c in guessed else "_" for c in word)

    await interaction.response.send_message(
        f"🎮 **Hangman Started!**\nWord: `{masked()}`\nLives: ❤️❤️❤️❤️❤️❤️"
    )

    def check(msg):
        return msg.channel == interaction.channel and len(msg.content) == 1 and msg.content.isalpha()

    while lives > 0:
        try:
            msg = await bot.wait_for("message", timeout=40, check=check)
            letter = msg.content.lower()

            if letter in guessed:
                await interaction.followup.send(f"⚠️ `{letter}` already guessed.")
                continue

            guessed.append(letter)

            if letter in word:
                if "_" not in masked():
                    return await interaction.followup.send(
                        f"✅ Correct! The word was **{word}** 🎉"
                    )
                await interaction.followup.send(f"✅ `{letter}` is correct!\n`{masked()}`")
            else:
                lives -= 1
                if lives == 0:
                    return await interaction.followup.send(
                        f"💀 No lives left! The word was **{word}**."
                    )
                await interaction.followup.send(
                    f"❌ Wrong!\n`{masked()}`\nLives left: {lives}"
                )

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Timeout — game over!")

# ============================================================
# ✅ QUIPLASH
# ============================================================

QUIPLASH_PROMPTS = [
    "If AVK had a slogan, what would it be?",
    "Worst thing to say during Bear Trap?",
    "What should be banned in Whiteout Survival?",
]

@bot.tree.command(name="quiplash", description="Start a Quiplash round.")
async def quiplash_cmd(interaction: discord.Interaction):

    prompt = random.choice(QUIPLASH_PROMPTS)

    await interaction.response.send_message(
        f"🎤 **Quiplash Prompt:**\n{prompt}\n\n"
        f"✍️ Everyone: send your answer (30 seconds)."
    )

    answers = []

    def check(msg):
        return msg.channel == interaction.channel and not msg.author.bot

    try:
        while True:
            msg = await bot.wait_for("message", timeout=30, check=check)
            answers.append((msg.author, msg.content))

    except asyncio.TimeoutError:
        pass

    if not answers:
        return await interaction.followup.send("❌ No answers submitted.")

    text = "\n".join([f"• **{a.display_name}**: {t}" for a, t in answers])
    await interaction.followup.send(f"🗳️ **Voting time!**\n{text}\n✅ React to vote!")

# ============================================================
# ✅ ON READY
# ============================================================

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

    guild = discord.Object(id=GUILD_ID)

    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ {len(synced)} commandes synchronisées pour AVK.")
    except Exception as e:
        print(f"❌ Erreur sync : {e}")

    bot.loop.create_task(beartrap_loop())

    print("✅ AVK BOT prêt à l'action !")

# ============================================================
# ✅ START BOT
# ============================================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if TOKEN is None:
    print("❌ ERREUR : DISCORD_BOT_TOKEN manquant (Render > Environment)")
else:
    bot.run(TOKEN)
