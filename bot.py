import discord
from discord.ext import commands
import json
import os

# Load or create data file
if not os.path.exists('data.json'):
    with open('data.json', 'w') as f:
        json.dump({}, f)

with open('data.json', 'r') as f:
    users = json.load(f)

# Constants
MAX_LEVEL = 100
XP_PER_MINUTE = {
    "study": 2,        # 2 XP per minute studying
    "workout": 3,      # 3 XP per minute workout
    "massage": 1       # 1 XP per minute facial massage
}
BASE_XP = 100  # XP needed for first level
XP_INCREMENT = 50  # Additional XP needed per level

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Save user data
def save_users():
    with open('data.json', 'w') as f:
        json.dump(users, f, indent=4)

# Calculate XP needed for next level
def xp_for_next_level(level):
    return BASE_XP + (level - 1) * XP_INCREMENT

# Add XP and handle level up
def add_xp(user_id, amount):
    if str(user_id) not in users:
        users[str(user_id)] = {"xp": 0, "level": 1}
    
    users[str(user_id)]["xp"] += amount

    while users[str(user_id)]["level"] < MAX_LEVEL and users[str(user_id)]["xp"] >= xp_for_next_level(users[str(user_id)]["level"]):
        users[str(user_id)]["xp"] -= xp_for_next_level(users[str(user_id)]["level"])
        users[str(user_id)]["level"] += 1

    save_users()

# Commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def study(ctx, minutes: int):
    xp_gained = minutes * XP_PER_MINUTE["study"]
    add_xp(ctx.author.id, xp_gained)
    await ctx.send(f'{ctx.author.mention} studied for {minutes} minutes and earned {xp_gained} XP!')

@bot.command()
async def workout(ctx, minutes: int):
    xp_gained = minutes * XP_PER_MINUTE["workout"]
    add_xp(ctx.author.id, xp_gained)
    await ctx.send(f'{ctx.author.mention} worked out for {minutes} minutes and earned {xp_gained} XP!')

@bot.command()
async def massage(ctx, minutes: int):
    xp_gained = minutes * XP_PER_MINUTE["massage"]
    add_xp(ctx.author.id, xp_gained)
    await ctx.send(f'{ctx.author.mention} did a facial massage for {minutes} minutes and earned {xp_gained} XP!')

@bot.command()
async def xp(ctx):
    if str(ctx.author.id) not in users:
        await ctx.send("You don't have any XP yet!")
        return

    xp = users[str(ctx.author.id)]["xp"]
    level = users[str(ctx.author.id)]["level"]
    next_level_xp = xp_for_next_level(level) - xp

    await ctx.send(f'{ctx.author.mention} is Level {level} with {xp} XP. {next_level_xp} XP needed for next level!')

@bot.command()
async def leaderboard(ctx):
    leaderboard = sorted(users.items(), key=lambda x: (x[1]['level'], x[1]['xp']), reverse=True)
    description = ""
    for i, (user_id, data) in enumerate(leaderboard[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        description += f"{i}. {user.name}: Level {data['level']} ({data['xp']} XP)\n"

    embed = discord.Embed(title="Leaderboard", description=description, color=discord.Color.blue())
    await ctx.send(embed=embed)

# Start bot
bot.run(os.getenv("TOKEN"))
    
