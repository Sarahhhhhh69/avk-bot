import os
import json
import asyncio
import random
import datetime
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ============================================================
# CONFIG
# ============================================================

UTC = datetime.timezone.utc
REMINDERS_CHANNEL_ID = 1464987172133273664
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# LOAD TRIVIA
# ============================================================

with open("trivia.json", "r", encoding="utf-8") as f:
    TRIVIA = json.load(f)

TRIVIA_CATEGORIES = list(TRIVIA.keys())
LETTERS = ["🇦", "🇧", "🇨", "🇩"]

# ============================================================
# BASIC COMMAND
# ============================================================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

# ============================================================
# TRIVIA SESSION (20 QUESTIONS)
# ============================================================

@bot.tree.command(name="trivia", description="Start a trivia session")
@app_commands.describe(category="Choose a category")
@app_commands.choices(category=[
    app_commands.Choice(name=cat, value=cat) for cat in TRIVIA_CATEGORIES
])
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):

    questions = TRIVIA[category.value].copy()
    random.shuffle(questions)
    questions = questions[:20]

    scores = {}
    channel = interaction.channel

    await interaction.response.send_message(
        f"🎉 **{category.value} Trivia starting!**\n"
        f"20 questions – fastest correct answer wins!"
    )

    await asyncio.sleep(2)

    for idx, q in enumerate(questions, start=1):
        question_text = f"🧠 **Question {idx}/20**\n\n{q['question']}\n"
        for i, ans in enumerate(q["answers"]):
            question_text += f"{LETTERS[i]} {ans}\n"

        msg = await channel.send(question_text)

        for emoji in LETTERS:
            await msg.add_reaction(emoji)

        answered = False

        def check(reaction, user):
            return (
                user != bot.user and
                reaction.message.id == msg.id and
                str(reaction.emoji) in LETTERS
            )

        try:
            while True:
                reaction, user = await bot.wait_for("reaction_add", timeout=20.0, check=check)
                choice = LETTERS.index(str(reaction.emoji))

                if choice == q["correct"] and not answered:
                    scores[user.display_name] = scores.get(user.display_name, 0) + 1
                    await channel.send(
                        f"✅ **Correct!** 🏆 **{user.display_name}** wins this round\n"
                        f"🎯 Answer: **{q['answers'][q['correct']]}**"
                    )
                    answered = True
                    break
        except asyncio.TimeoutError:
            if not answered:
                await channel.send(
                    f"⌛ **Time’s up!**\n"
                    f"✅ Correct answer: **{q['answers'][q['correct']]}**"
                )

        await asyncio.sleep(3)

    # ========================================================
    # FINAL SCOREBOARD
    # ========================================================

    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        podium = sorted_scores[:3]
        medals = ["🥇", "🥈", "🥉"]

        result = "🏁 **Final Trivia Results** 🏁\n\n"
        for i, (name, score) in enumerate(podium):
            result += f"{medals[i]} **{name}** — {score} points\n"

        await channel.send(result)
    else:
        await channel.send("🤷 Nobody scored any point… impressive 😅")

# ============================================================
# TIC TAC TOE (STABLE)
# ============================================================

@bot.tree.command(name="tictactoe")
@app_commands.describe(opponent="Opponent")
async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):

    if opponent.bot or opponent == interaction.user:
        return await interaction.response.send_message("❌ Choose a valid human opponent.")

    board = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
    players = [interaction.user, opponent]
    symbols = ["❌", "⭕"]
    turn = 0

    def render():
        return (
            f"{board[0]} {board[1]} {board[2]}\n"
            f"{board[3]} {board[4]} {board[5]}\n"
            f"{board[6]} {board[7]} {board[8]}"
        )

    def check_win(sym):
        wins = [
            (0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)
        ]
        return any(all(board[i] == sym for i in combo) for combo in wins)

    await interaction.response.send_message(
        f"❌⭕ **Tic Tac Toe**\n\n{render()}\n\n"
        f"{players[turn].mention}, choose a number (1–9)"
    )

    while True:
        def check(msg):
            return (
                msg.channel == interaction.channel
                and msg.author == players[turn]
                and msg.content in list("123456789")
            )

        try:
            msg = await bot.wait_for("message", timeout=30, check=check)
            pos = int(msg.content) - 1

            if board[pos] in symbols:
                continue

            board[pos] = symbols[turn]

            if check_win(symbols[turn]):
                return await interaction.followup.send(
                    f"{render()}\n🏆 **{players[turn].mention} wins!**"
                )

            if all(cell in symbols for cell in board):
                return await interaction.followup.send(
                    f"{render()}\n🤝 **Draw!**"
                )

            turn = 1 - turn
            await interaction.followup.send(
                f"{render()}\n{players[turn].mention}, your turn"
            )

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Game ended due to inactivity.")

# ============================================================
# STARTUP
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()

bot.run(TOKEN)
``
