import os, json, asyncio, random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
LETTERS = ["🇦","🇧","🇨","🇩"]
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

with open("trivia.json","r",encoding="utf-8") as f:
    TRIVIA = json.load(f)
CATEGORIES = list(TRIVIA.keys())

@bot.tree.command(name="trivia")
@app_commands.choices(category=[app_commands.Choice(name=c,value=c) for c in CATEGORIES])
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):
    pool = TRIVIA[category.value][:]
    random.shuffle(pool)
    questions = pool[:20]

    scores = {}
    await interaction.response.send_message(f"🎉 {category.value} Trivia — 10 seconds per question")

    for idx, q in enumerate(questions, start=1):
        msg = await interaction.channel.send("
".join([
            f"🧠 Question {idx}/20",
            q['question'],
            *(f"{LETTERS[i]} {a}" for i,a in enumerate(q['answers']))
        ]))
        for e in LETTERS:
            await msg.add_reaction(e)

        answered = {}
        start = asyncio.get_event_loop().time()

        def check(reaction,user):
            return user!=bot.user and reaction.message.id==msg.id and str(reaction.emoji) in LETTERS and user.id not in answered

        try:
            while asyncio.get_event_loop().time() - start < 10:
                reaction, user = await bot.wait_for("reaction_add", timeout=10, check=check)
                answered[user.id] = LETTERS.index(str(reaction.emoji))
        except asyncio.TimeoutError:
            pass

        correct_users = [(uid, t) for uid,t in answered.items() if t == q['correct']]
        ordered = list(correct_users)

        awards = [5,3,2]
        announce = []
        for i,(uid,_) in enumerate(ordered):
            name = next(m.display_name for m in interaction.guild.members if m.id==uid)
            pts = awards[i] if i < 3 else 1
            scores[name] = scores.get(name, 0) + pts
            announce.append(f"{name} +{pts}")

        if announce:
            await interaction.channel.send(
                f"✅ Correct answer: {q['answers'][q['correct']]}
" +
                "🏆 This round: " + " | ".join(announce)
            )
            # show round top 3
            top_round = sorted([(a.split()[0], int(a.split('+')[1])) for a in announce], key=lambda x:x[1], reverse=True)[:3]
            await interaction.channel.send(
                "🥇🥈🥉 Round Top 3:
" + "
".join(f"{i+1}. {n} ({p})" for i,(n,p) in enumerate(top_round))
            )
        else:
            await interaction.channel.send(f"⌛ Time's up! Correct answer: {q['answers'][q['correct']]}")

        await asyncio.sleep(1)

    if scores:
        final = sorted(scores.items(), key=lambda x:x[1], reverse=True)[:3]
        medals = ["🥇","🥈","🥉"]
        await interaction.channel.send(
            "🏁 FINAL TOP 3:
" + "
".join(f"{medals[i]} {n} — {s}" for i,(n,s) in enumerate(final))
        )

@bot.event
async def setup_hook(): await bot.tree.sync()
bot.run(TOKEN)
