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

# ================= CONFIG =================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
UTC = datetime.timezone.utc

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= LOAD TRIVIA =================

with open("trivia.json", "r", encoding="utf-8") as f:
    TRIVIA = json.load(f)

CATEGORIES = list(TRIVIA.keys())
LETTERS = ["🇦", "🇧", "🇨", "🇩"]

# ================= BASIC =================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

# ================= TRIVIA =================

@bot.tree.command(name="trivia", description="Start a trivia session")
@app_commands.describe(category="Choose a category")
@app_commands.choices(category=[app_commands.Choice(name=c, value=c) for c in CATEGORIES])
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
        text = f"🧠 **Question {idx}/20**\n\n{q['question']}\n"
        for i, ans in enumerate(q["answers"]):
            text += f"{LETTERS[i]} {ans}\n"

        msg = await channel.send(text)

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
                reaction, user = await bot.wait_for("reaction_add", timeout=20, check=check)
                choice = LETTERS.index(str(reaction.emoji))

                if choice == q["correct"] and not answered:
                    scores[user.display_name] = scores.get(user.display_name, 0) + 1
                    await channel.send(
                        f"✅ **Correct!** 🏆 **{user.display_name}** wins\n"
                        f"🎯 Answer: **{q['answers'][q['correct']]}**"
                    )
                    answered = True
                    break
        except asyncio.TimeoutError:
            if not answered:
                await channel.send(
                    f"⌛ **Time’s up!** Correct answer: **{q['answers'][q['correct']]}**"
                )

        await asyncio.sleep(3)

    if scores:
        final = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        medals = ["🥇", "🥈", "🥉"]

        result = "🏁 **Final Results** 🏁\n\n"
        for i, (name, score) in enumerate(final):
            result += f"{medals[i]} **{name}** — {score} points\n"

        await channel.send(result)
    else:
        await channel.send("🤷 Nobody scored any point 😅")

# ================= TICTACTOE =================

@bot.tree.command(name="tictactoe")
@app_commands.describe(opponent="Opponent")
async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):

    if opponent.bot or opponent == interaction.user:
        return await interaction.response.send_message("❌ Invalid opponent.")

    board = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
    players = [interaction.user, opponent]
    symbols = ["❌","⭕"]
    turn = 0

    def render():
        return f"{board[0]} {board[1]} {board[2]}\n{board[3]} {board[4]} {board[5]}\n{board[6]} {board[7]} {board[8]}"

    def win(sym):
        combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        return any(all(board[i] == sym for i in c) for c in combos)

    await interaction.response.send_message(f"❌⭕ Tic Tac Toe\n\n{render()}\n\n{players[turn].mention}, choose 1–9")

    while True:
        def check(msg):
            return msg.channel == interaction.channel and msg.author == players[turn] and msg.content in "123456789"

        try:
            msg = await bot.wait_for("message", timeout=30, check=check)
            pos = int(msg.content) - 1

            if board[pos] in symbols:
                continue

            board[pos] = symbols[turn]

            if win(symbols[turn]):
                return await interaction.followup.send(f"{render()}\n🏆 **{players[turn].mention} wins!**")

            if all(c in symbols for c in board):
                return await interaction.followup.send(f"{render()}\n🤝 Draw")

            turn = 1 - turn
            await interaction.followup.send(f"{render()}\n{players[turn].mention}, your turn")

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Game ended.")

# ================= START =================

@bot.event
async def setup_hook():
    await bot.tree.sync()

bot.run(TOKEN)
``
