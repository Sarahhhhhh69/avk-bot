# ============================================================
# AVK UTILITY BOT — TRIVIA ABCD FULL CATEGORIES
# ============================================================

import os, asyncio, datetime, random
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

keep_alive()

# ================= CONFIG =================

GUILD_ID = 1463165558232186910
UTC = datetime.timezone.utc

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        messages=True,
        message_content=True,
        members=True
    )
)

# ================= TRIVIA QUESTIONS =================

TRIVIA = {

    # ---------------- AVK ----------------
    "AVK": [
        {"q": "Who is the most motivating person in AVK?", "a": ["Sarah", "Coffee", "The Snow", "Lag"], "c": 0},
        {"q": "Who causes chaos but everyone still loves it?", "a": ["Ruti", "Rules", "Order", "Silence"], "c": 0},
        {"q": "Who never seems to sleep during events?", "a": ["Willy Plonka", "The Furnace", "NPCs", "Nobody"], "c": 0},
        {"q": "Who is suspiciously active on Sundays?", "a": ["All Sunday", "Monday", "Tuesday", "Friday"], "c": 0},
        {"q": "Who gives advice like an ancient forest guardian?", "a": ["Treebeard", "A Chair", "A Rock", "A Table"], "c": 0},
        {"q": "Who always brings positive vibes?", "a": ["Miss Sunshine", "Dark Clouds", "Blizzards", "Lag"], "c": 0},
        {"q": "Who stays calm and deadly when needed?", "a": ["Nightwolf", "Goldfish", "Penguin", "Turtle"], "c": 0},
        {"q": "Who has legendary energy levels?", "a": ["Brent", "Low Battery", "Sleep Mode", "AFK"], "c": 0},
        {"q": "Who makes people laugh even during disasters?", "a": ["Tickle", "Taxes", "Cold Weather", "Lag"], "c": 0},
        {"q": "Who combines warning signs with loyalty?", "a": ["RedRabbit", "Blue Turtle", "Green Frog", "Yellow Fish"], "c": 0}
    ],

    # ---------------- SCIENCE ----------------
    "Science": [
        {"q": "What planet is known as the Red Planet?", "a": ["Mars", "Venus", "Jupiter", "Saturn"], "c": 0},
        {"q": "What gas do humans need to breathe?", "a": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"], "c": 0},
        {"q": "What is H2O?", "a": ["Water", "Hydrogen", "Salt", "Oxygen"], "c": 0},
        {"q": "What force keeps us on Earth?", "a": ["Gravity", "Magnetism", "Wind", "Luck"], "c": 0},
        {"q": "What star is closest to Earth?", "a": ["The Sun", "The Moon", "Polaris", "Sirius"], "c": 0},
        {"q": "What organ pumps blood?", "a": ["Heart", "Brain", "Lungs", "Liver"], "c": 0},
        {"q": "What state of matter is air?", "a": ["Gas", "Solid", "Liquid", "Plasma"], "c": 0},
        {"q": "What vitamin comes from sunlight?", "a": ["Vitamin D", "Vitamin C", "Vitamin B", "Vitamin A"], "c": 0},
        {"q": "What planet has rings?", "a": ["Saturn", "Mars", "Earth", "Venus"], "c": 0},
        {"q": "What is the boiling point of water (°C)?", "a": ["100", "50", "0", "200"], "c": 0}
    ],

    # ---------------- GEOGRAPHY ----------------
    "Geography": [
        {"q": "What is the capital of France?", "a": ["Paris", "Rome", "Berlin", "Madrid"], "c": 0},
        {"q": "Which ocean is the largest?", "a": ["Pacific", "Atlantic", "Indian", "Arctic"], "c": 0},
        {"q": "Which continent is Brazil in?", "a": ["South America", "Africa", "Asia", "Europe"], "c": 0},
        {"q": "Mount Everest is in which range?", "a": ["Himalayas", "Alps", "Andes", "Rockies"], "c": 0},
        {"q": "What is the capital of Canada?", "a": ["Ottawa", "Toronto", "Vancouver", "Montreal"], "c": 0},
        {"q": "Which country is an island?", "a": ["Japan", "Germany", "Brazil", "Egypt"], "c": 0},
        {"q": "Which desert is the largest hot desert?", "a": ["Sahara", "Gobi", "Atacama", "Kalahari"], "c": 0},
        {"q": "The Nile flows into which sea?", "a": ["Mediterranean", "Red Sea", "Black Sea", "Arabian Sea"], "c": 0},
        {"q": "Which pole is colder?", "a": ["South Pole", "North Pole", "Same", "Neither"], "c": 0},
        {"q": "What is the longest river?", "a": ["Nile", "Amazon", "Yangtze", "Mississippi"], "c": 0}
    ],

    # ---------------- COOKING ----------------
    "Cooking": [
        {"q": "Which country does pizza come from?", "a": ["Italy", "France", "USA", "Spain"], "c": 0},
        {"q": "What makes bread rise?", "a": ["Yeast", "Salt", "Sugar", "Flour"], "c": 0},
        {"q": "What is sushi mainly made of?", "a": ["Rice", "Beef", "Chicken", "Cheese"], "c": 0},
        {"q": "Which ingredient makes food spicy?", "a": ["Chili", "Sugar", "Salt", "Milk"], "c": 0},
        {"q": "Pasta is usually cooked in…", "a": ["Water", "Oil", "Milk", "Juice"], "c": 0},
        {"q": "Chocolate comes from…", "a": ["Cocoa beans", "Coffee beans", "Wheat", "Grapes"], "c": 0},
        {"q": "What food comes from milk?", "a": ["Cheese", "Bread", "Rice", "Egg"], "c": 0},
        {"q": "Which herb is used in pesto?", "a": ["Basil", "Mint", "Parsley", "Rosemary"], "c": 0},
        {"q": "Which vitamin is in oranges?", "a": ["Vitamin C", "Vitamin D", "Vitamin A", "Vitamin B"], "c": 0},
        {"q": "A knife is used to…", "a": ["Cut food", "Bake food", "Freeze food", "Boil food"], "c": 0}
    ],

    # ---------------- CINEMA ----------------
    "Cinema": [
        {"q": "Who played Jack in Titanic?", "a": ["Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Johnny Depp"], "c": 0},
        {"q": "Which movie features a ring that must be destroyed?", "a": ["Lord of the Rings", "Harry Potter", "Avatar", "Star Wars"], "c": 0},
        {"q": "Which movie has dinosaurs?", "a": ["Jurassic Park", "Titanic", "Inception", "Gladiator"], "c": 0},
        {"q": "Who is Iron Man?", "a": ["Tony Stark", "Bruce Wayne", "Clark Kent", "Peter Parker"], "c": 0},
        {"q": "Which movie says 'May the Force be with you'?", "a": ["Star Wars", "Matrix", "Avatar", "Alien"], "c": 0},
        {"q": "What genre is The Matrix?", "a": ["Science Fiction", "Romance", "Comedy", "Horror"], "c": 0},
        {"q": "Who is the wizard in Lord of the Rings?", "a": ["Gandalf", "Dumbledore", "Merlin", "Saruman"], "c": 0},
        {"q": "Which movie is about dreams within dreams?", "a": ["Inception", "Avatar", "Interstellar", "Joker"], "c": 0},
        {"q": "Who played Wolverine?", "a": ["Hugh Jackman", "Chris Evans", "Robert Downey Jr", "Ben Affleck"], "c": 0},
        {"q": "Which movie is about Pandora?", "a": ["Avatar", "Alien", "Matrix", "Star Trek"], "c": 0}
    ],

    # ---------------- TV SERIES ----------------
    "TV Series": [
        {"q": "Who is the main character in Breaking Bad?", "a": ["Walter White", "Jesse Pinkman", "Saul Goodman", "Hank Schrader"], "c": 0},
        {"q": "Which series features dragons?", "a": ["Game of Thrones", "Friends", "Lost", "Dexter"], "c": 0},
        {"q": "Who lives in Springfield?", "a": ["The Simpsons", "The Griffins", "The Smiths", "The Browns"], "c": 0},
        {"q": "Which series is set in Hawkins?", "a": ["Stranger Things", "Dark", "The 100", "The Boys"], "c": 0},
        {"q": "Who is Sherlock Holmes’ friend?", "a": ["Watson", "Wilson", "Wesley", "Walter"], "c": 0},
        {"q": "Which show is about a paper company?", "a": ["The Office", "Friends", "Suits", "House"], "c": 0},
        {"q": "Which show has zombies?", "a": ["The Walking Dead", "Lost", "Prison Break", "Vikings"], "c": 0},
        {"q": "Who rules Westeros?", "a": ["Iron Throne", "White House", "Hogwarts", "Narnia"], "c": 0},
        {"q": "Which series is about Vikings?", "a": ["Vikings", "Rome", "Spartacus", "Troy"], "c": 0},
        {"q": "Which show features Eleven?", "a": ["Stranger Things", "Dark", "The Boys", "Lost"], "c": 0}
    ],

    # ---------------- MUSIC ----------------
    "Music": [
        {"q": "Who is known as the King of Pop?", "a": ["Michael Jackson", "Elvis Presley", "Prince", "Madonna"], "c": 0},
        {"q": "Which instrument has keys?", "a": ["Piano", "Drum", "Violin", "Guitar"], "c": 0},
        {"q": "Who sang 'Imagine'?", "a": ["John Lennon", "Paul McCartney", "Elton John", "Freddie Mercury"], "c": 0},
        {"q": "Which band sang 'Bohemian Rhapsody'?", "a": ["Queen", "Beatles", "U2", "Pink Floyd"], "c": 0},
        {"q": "What genre is Beethoven?", "a": ["Classical", "Rock", "Pop", "Jazz"], "c": 0},
        {"q": "Which instrument has six strings?", "a": ["Guitar", "Piano", "Trumpet", "Drums"], "c": 0},
        {"q": "Who is famous for 'Like a Virgin'?", "a": ["Madonna", "Beyoncé", "Rihanna", "Adele"], "c": 0},
        {"q": "Which band is from Liverpool?", "a": ["Beatles", "Rolling Stones", "Oasis", "Radiohead"], "c": 0},
        {"q": "What does a DJ do?", "a": ["Mix music", "Cook food", "Paint walls", "Write books"], "c": 0},
        {"q": "What device plays music?", "a": ["Speaker", "Fridge", "Oven", "Lamp"], "c": 0}
    ]
}

# ================= TRIVIA COMMAND =================

@bot.tree.command(name="trivia")
@app_commands.describe(category="Trivia category")
async def trivia(interaction: discord.Interaction, category: str):
    if category not in TRIVIA:
        return await interaction.response.send_message(
            f"Available categories: {', '.join(TRIVIA.keys())}"
        )

    q = random.choice(TRIVIA[category])
    letters = ["🇦", "🇧", "🇨", "🇩"]

    text = f"🧠 **{category} Trivia**\n\n{q['q']}\n"
    for i, ans in enumerate(q["a"]):
        text += f"{letters[i]} {ans}\n"

    await interaction.response.send_message(text)
    msg = await interaction.original_response()

    for l in letters:
        await msg.add_reaction(l)

    def check(reaction, user):
        return (
            user != bot.user
            and reaction.message.id == msg.id
            and str(reaction.emoji) in letters
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=20, check=check)
        idx = letters.index(str(reaction.emoji))
        if idx == q["c"]:
            await interaction.followup.send(f"✅ Correct, {user.mention}!")
        else:
            await interaction.followup.send(
                f"❌ Wrong! Correct answer was **{q['a'][q['c']]}**"
            )
    except asyncio.TimeoutError:
        await interaction.followup.send("⌛ Time’s up!")

# ================= START =================

@bot.event
async def setup_hook():
    await bot.tree.sync()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
