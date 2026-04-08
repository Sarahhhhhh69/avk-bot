import os
import json
import asyncio
import random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LETTERS = ["🇦", "🇧", "🇨", "🇩"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# LOAD TRIVIA DATA
# ============================================================

with open("trivia.json", "r", encoding="utf-8") as f:
    TRIVIA = json.load(f)

CATEGORIES = list(TRIVIA.keys())

# ============================================================
# BASIC CHECK
# ============================================================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

# ============================================================
# TRIVIA SESSION (20 QUESTIONS, STRICT RULES)
# ============================================================

@bot.tree.command(name="trivia", description="Start a trivia session")
@app_commands.describe(category="Choose a trivia category")
@app_commands.choices(category=[
    app_commands.Choice(name=cat, value=cat) for cat in CATEGORIES
])
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):

    # 1️⃣ Build a fixed list of 20 unique questions
    all_questions = TRIVIA[category.value].copy()
    random.shuffle(all_questions)
    questions = all_questions[:20]  # ✅ impossible to repeat

    scores = {}
    channel = interaction.channel

    await interaction.response.send_message(
        f"🎉 **{category.value} Trivia starting!**\n"
        f"20 questions · Fastest correct answer wins"
    )

    await asyncio.sleep(2)

    # 2️⃣ Ask questions one by one
    for idx, q in enumerate(questions, start=1):

        question_text = f"🧠 **Question {idx}/20**\n\n{q['question']}\n"
        for i, ans in enumerate(q["answers"]):
            question_text += f"{LETTERS[i]} {ans}\n"

        msg = await channel.send(question_text)

        for emoji in LETTERS:
            await msg.add_reaction(emoji)

        answered_users = set()
        question_solved = False

        def check(reaction, user):
            return (
                user != bot.user
                and reaction.message.id == msg.id
                and str(reaction.emoji) in LETTERS
                and user.id not in answered_users
            )

        try:
            while True:
                reaction, user = await bot.wait_for(
                    "reaction_add",
                    timeout=20,
                    check=check
                )

                answered_users.add(user.id)
                choice_index = LETTERS.index(str(reaction.emoji))

                # ✅ FIRST correct answer wins
                if choice_index == q["correct"] and not question_solved:
                    scores[user.display_name] = scores.get(user.display_name, 0) + 1
                    await channel.send(
                        f"✅ **Correct!** 🏆 **{user.display_name} wins**\n"
                        f"🎯 Answer: **{q['answers'][q['correct']]}**"
                    )
                    question_solved = True
                    break
        except asyncio.TimeoutError:
            if not question_solved:
                await channel.send(
                    f"⌛ **Time’s up!**\n"
                    f"✅ Correct answer: **{q['answers'][q['correct']]}**"
                )

        await asyncio.sleep(2)

    # ========================================================
    # FINAL SCOREBOARD
    # ========================================================

    if scores:
        ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        medals = ["🥇", "🥈", "🥉"]

        result = "🏁 **Final Trivia Results** 🏁\n\n"
        for i, (name, score) in enumerate(ranking):
            result += f"{medals[i]} **{name}** — {score} points\n"

        await channel.send(result)
    else:
        await channel.send("🤷 No correct answers — impressive in its own way 😅")

# ============================================================
# STARTUP
# ============================================================

@bot.event
async def setup_hook():
    await bot.tree.sync()

bot.run(TOKEN)
