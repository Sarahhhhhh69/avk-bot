# ============================================================
# AVK UTILITY BOT — TRIVIA ENGINE + GAMES
# ============================================================

import os, json, asyncio, random, datetime
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

UTC = datetime.timezone.utc
REMINDERS_CHANNEL_ID = 1464987172133273664
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        messages=True,
        message_content=True,
        members=True
    )
)

# ============================================================
# LOAD TRIVIA QUESTIONS
# ============================================================

with open("trivia.json", "r", encoding="utf-8") as f:
    TRIVIA = json.load(f)

# ============================================================
# TRIVIA SESSION (20 questions)
# ============================================================

@bot.tree.command(name="trivia", description="Start a trivia session")
@app_commands.describe(category="Choose a category")
@app_commands.choices(category=[
    app_commands.Choice(name=k, value=k) for k in [
        "AVK", "Science", "Geography", "Cooking",
        "WOS", "Cinema", "TV Series", "Music"
    ]
])
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):

    questions = TRIVIA[category.value].copy()
    random.shuffle(questions)
    questions = questions[:20]

    scores = {}
    letters = ["🇦", "🇧", "🇨", "🇩"]

    await interaction.response.send_message(
        f"🎉 **{category.value} Trivia starting!**\n20 questions, fastest wins!"
    )

    await asyncio.sleep(2)

    for index, q in enumerate(questions, start=1):
        text = f"🧠 **Question {index}/20**\n\n{q['question']}\n"
        for i, ans in enumerate(q['answers']):
            text += f"{letters[i]} {ans}\n"

        await interaction.channel.send(text)
        msg = await interaction.channel.send("⏳ You have 20 seconds!")

        for r in letters:
            await msg.add_reaction(r)

        answered = False

        def check(reaction, user):
            return (
                user != bot.user
                and reaction.message.id == msg.id
                and str(reaction.emoji) in letters
            )

        try:
            while True:
                reaction, user = await bot.wait_for("reaction_add", timeout=20, check=check)
                chosen = letters.index(str(reaction.emoji))
                if chosen == q["correct"]:
                    scores[user.display_name] = scores.get(user.display_name, 0) + 1
                    await interaction.channel.send(
                        f"✅ **Correct!** 🏆 {user.display_name}\n"
                        f"🎯 Answer: **{q['answers'][q['correct']]}**"
                    )
                    answered = True
                    break
        except asyncio.TimeoutError:
            if not answered:
                await interaction.channel.send(
                    f"⌛ **Time's up!** Correct answer: **{q['answers'][q['correct']]}**"
                )

        await asyncio.sleep(3)

    # ========================================================
    # FINAL SCOREBOARD
    # ========================================================

    if scores:
        final = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        medals = ["🥇", "🥈", "🥉"]

        result = "🏁 **Final Results** 🏁\n\n"
        for i, (name, score) in enumerate(final):
            result += f"{medals[i]} **{name}** — {score} points\n"

        await interaction.channel.send(result)
    else:
        await interaction.channel.send("🤷 No correct answers… wow 😅")

# ============================================================
# TICTACTOE (STABLE)
# ============================================================

@bot.tree.command(name="tictactoe")
@app_commands.describe(opponent="Opponent")
async def tictactoe(interaction: discord.Interaction, opponent: discord.Member):

    if opponent.bot or opponent == interaction.user:
        return await interaction.response.send_message("❌ Invalid opponent.")

    board = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
    players = [interaction.user, opponent]
    symbols = ["❌", "⭕"]
    turn = 0

    def render():
        return f"{board[0]} {board[1]} {board[2]}\n{board[3]} {board[4]} {board[5]}\n{board[6]} {board[7]} {board[8]}"

    def win(sym):
        combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        return any(all(board[i] == sym for i in c) for c in combos)

    await interaction.response.send_message(
        f"❌⭕ **Tic Tac Toe**\n\n{render()}\n\n{players[turn].mention}, choose 1–9"
    )

    while True:
        def check(msg):
            return msg.channel == interaction.channel and msg.author == players[turn] and msg.content in list("123456789")

        try:
            msg = await bot.wait_for("message", timeout=30, check=check)
            pos = int(msg.content) - 1

            if board[pos] in symbols:
                continue

            board[pos] = symbols[turn]

            if win(symbols[turn]):
                return await interaction.followup.send(f"{render()}\n🏆 **{players[turn].mention} wins!**")

            if all(c in symbols for c in board):
                return await interaction.followup.send(f"{render()}\n🤝 **Draw!**")

            turn = 1 - turn
            await interaction.followup.send(f"{render()}\n{players[turn].mention}, your turn")

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Game ended due to inactivity.")

# ============================================================
# START
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()

bot.run(BOT_TOKEN)
``
