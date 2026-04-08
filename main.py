# ============================================================
# AVK UTILITY BOT — FINAL FIXED VERSION
# ============================================================

import os
import asyncio
import datetime
import random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ============================================================
# CONFIG
# ============================================================

UTC = datetime.timezone.utc
GUILD_ID = 1463165558232186910
REMINDERS_CHANNEL_ID = 1464987172133273664

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
# TRIVIA — AVK HUMOR ONLY
# ============================================================

TRIVIA_AVK = [
    {
        "q": "Who is secretly the strongest player in AVK?",
        "a": ["Sarah", "Willy Plonka", "Nightwolf", "Brent"],
        "c": 0
    },
    {
        "q": "Who always says 'I thought Bear Trap was tomorrow'?",
        "a": ["Ruti", "All Sunday", "Tickle", "Dark"],
        "c": 0
    },
    {
        "q": "Who probably owns the ugliest socks in AVK?",
        "a": ["Treebeard", "ZWG", "Rodina", "Kest AsCat"],
        "c": 0
    },
    {
        "q": "Who thinks upgrading the furnace fixes everything?",
        "a": ["Brent", "Citri", "Mikki", "RedRabbit"],
        "c": 0
    },
    {
        "q": "Who keeps morale high no matter what happens?",
        "a": ["Sarah", "Miss Sunshine", "Nightwolf", "All Sunday"],
        "c": 0
    },
    {
        "q": "Who is always online at strange hours?",
        "a": ["Willy Plonka", "Dark", "Ruti", "Tickle"],
        "c": 0
    },
    {
        "q": "Who would survive the longest in a frozen apocalypse?",
        "a": ["Sarah", "Nightwolf", "Treebeard", "Brent"],
        "c": 0
    },
]

# ============================================================
# COMMAND: /TRIVIA
# ============================================================

@bot.tree.command(name="trivia")
async def trivia(interaction: discord.Interaction):
    q = random.choice(TRIVIA_AVK)
    letters = ["🇦", "🇧", "🇨", "🇩"]

    text = f"😂 **AVK Trivia**\n\n{q['q']}\n"
    for i, ans in enumerate(q["a"]):
        text += f"{letters[i]} {ans}\n"

    await interaction.response.send_message(text)
    msg = await interaction.original_response()

    for l in letters:
        await msg.add_reaction(l)

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
            answer_index = letters.index(str(reaction.emoji))

            if answer_index == q["c"]:
                await interaction.followup.send(
                    f"✅ **Correct!**\n🏆 Winner: {user.mention}\n🎯 Answer: **{q['a'][q['c']]}**"
                )
                answered = True
                break

    except asyncio.TimeoutError:
        if not answered:
            await interaction.followup.send(
                f"⌛ **Time’s up!**\n✅ The correct answer was **{q['a'][q['c']]}**"
            )

# ============================================================
# TICTACTOE — FIXED VERSION
# ============================================================

@bot.tree.command(name="tictactoe")
@app_commands.describe(opponent="The player you want to challenge")
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
        f"❌⭕ **Tic Tac Toe**\n\n{render()}\n\n{players[turn].mention}, choose a number (1–9)."
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

            if board[pos] in ["❌", "⭕"]:
                continue

            board[pos] = symbols[turn]

            if check_win(symbols[turn]):
                return await interaction.followup.send(
                    f"{render()}\n🏆 **{players[turn].mention} wins!**"
                )

            if all(cell in ["❌", "⭕"] for cell in board):
                return await interaction.followup.send(
                    f"{render()}\n🤝 **Draw!**"
                )

            turn = 1 - turn
            await interaction.followup.send(
                f"{render()}\n{players[turn].mention}, your turn."
            )

        except asyncio.TimeoutError:
            return await interaction.followup.send(
                "⌛ **Game ended due to inactivity.**"
            )

# ============================================================
# BASIC HEALTH COMMAND
# ============================================================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

# ============================================================
# START
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_BOT_TOKEN missing")
