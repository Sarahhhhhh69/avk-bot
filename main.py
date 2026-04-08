# ============================================================
# AVK UTILITY BOT — FINAL FULL VERSION
# ============================================================

import os, asyncio, datetime, random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ===================== CONFIG =====================

UTC = datetime.timezone.utc
GUILD_ID = 1463165558232186910
REMINDERS_CHANNEL_ID = 1464987172133273664

TODAY_BT_TIMES = [
    (14, 0),
    (19, 35)
]

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        messages=True,
        message_content=True,
        members=True
    )
)

# ===================== TRIVIA DATA =====================

TRIVIA = {
    "AVK": [
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
        }
    ],
    "Science": [
        {"q": "What planet is known as the Red Planet?", "a": ["Mars","Venus","Jupiter","Saturn"], "c": 0}
    ],
    "Geography": [
        {"q": "What is the capital of France?", "a": ["Paris","Rome","Berlin","Madrid"], "c": 0}
    ],
    "Cooking": [
        {"q": "Which country does pizza come from?", "a": ["Italy","France","USA","Spain"], "c": 0}
    ],
    "WOS": [
        {"q": "Bear Trap is a…", "a": ["Alliance event","Solo mission","Market","Loot chest"], "c": 0}
    ],
    "Cinema": [
        {"q": "Who played Jack in Titanic?", "a": ["Leonardo DiCaprio","Brad Pitt","Tom Cruise","Johnny Depp"], "c": 0}
    ],
    "TV Series": [
        {"q": "Which series has dragons?", "a": ["Game of Thrones","Friends","Lost","Dexter"], "c": 0}
    ],
    "Music": [
        {"q": "Who is known as the King of Pop?", "a": ["Michael Jackson","Elvis Presley","Prince","Madonna"], "c": 0}
    ]
}

# ===================== COMMANDS =====================

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("✅ AVK Utility Bot is online.")

@bot.tree.command(name="trivia", description="Start a trivia")
@app_commands.describe(category="Choose a category")
@app_commands.choices(category=[
    app_commands.Choice(name=k, value=k) for k in TRIVIA.keys()
])
async def trivia(interaction: discord.Interaction, category: app_commands.Choice[str]):
    q = random.choice(TRIVIA[category.value])
    letters = ["🇦","🇧","🇨","🇩"]

    text = f"😂 **{category.value} Trivia**\n\n{q['q']}\n"
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
            picked = letters.index(str(reaction.emoji))
            if picked == q["c"]:
                await interaction.followup.send(
                    f"✅ **Correct!**\n🏆 Winner: {user.mention}\n🎯 Answer: **{q['a'][q['c']]}**"
                )
                answered = True
                break
    except asyncio.TimeoutError:
        if not answered:
            await interaction.followup.send(
                f"⌛ **Time’s up!**\n✅ Correct answer: **{q['a'][q['c']]}**"
            )

# ===================== TICTACTOE =====================

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
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        return any(all(board[i]==sym for i in c) for c in wins)

    await interaction.response.send_message(
        f"❌⭕ **Tic Tac Toe**\n\n{render()}\n\n{players[turn].mention}, choose 1–9"
    )

    while True:
        def check(msg):
            return msg.channel == interaction.channel and msg.author == players[turn] and msg.content in list("123456789")

        try:
            msg = await bot.wait_for("message", timeout=30, check=check)
            pos = int(msg.content)-1

            if board[pos] in ["❌","⭕"]:
                continue

            board[pos] = symbols[turn]

            if win(symbols[turn]):
                return await interaction.followup.send(f"{render()}\n🏆 **{players[turn].mention} wins!**")

            if all(c in ["❌","⭕"] for c in board):
                return await interaction.followup.send(f"{render()}\n🤝 **Draw!**")

            turn = 1-turn
            await interaction.followup.send(f"{render()}\n{players[turn].mention}, your turn")

        except asyncio.TimeoutError:
            return await interaction.followup.send("⌛ Game ended (timeout).")

# ===================== SCHEDULER =====================

arena_sent_date = None
bt_sent = set()

async def scheduler_loop():
    global arena_sent_date
    await bot.wait_until_ready()
    channel = bot.get_channel(REMINDERS_CHANNEL_ID)

    while True:
        now = datetime.datetime.now(UTC)

        # Arena
        if now.hour == 23 and now.minute == 45:
            if arena_sent_date != now.date() and channel:
                await channel.send("⚔️ **Arena ends in 15 minutes!** Finish your fights!")
                arena_sent_date = now.date()

        # Bear Trap
        for h,m in TODAY_BT_TIMES:
            bt = now.replace(hour=h, minute=m, second=0, microsecond=0)
            for label, offset in [("1 hour",60),("30 minutes",30),("5 minutes",5),("NOW",0)]:
                t = bt - datetime.timedelta(minutes=offset)
                key = f"{bt}-{label}"
                if t.hour==now.hour and t.minute==now.minute and key not in bt_sent:
                    bt_sent.add(key)
                    if channel:
                        await channel.send("🐻❄️ **BEAR TRAP NOW!**" if label=="NOW" else f"⏰ **Bear Trap starts in {label}!**")

        await asyncio.sleep(60)

# ===================== START =====================

@bot.event
async def setup_hook():
    await bot.tree.sync()
    bot.loop.create_task(scheduler_loop())

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_BOT_TOKEN missing")
