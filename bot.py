import discord
from discord.ext import commands
import json
import random
import os

# Load token from environment variable or you can directly paste your token
#TOKEN = os.getenv("TOKEN")  # <- For Railway Hosting
TOKEN = 'TOKEN'  # <- If you are running locally, uncomment this and paste your token here

# Set Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Create Bot
bot = commands.Bot(command_prefix='!', intents=intents)

# XP rates per activity
XP_RATES = {
    'studying': 2,
    'workout': 3,
    'facial_massage': 1
}

# Load user data
try:
    with open('data.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

# Save user data
def save_users():
    with open('data.json', 'w') as f:
        json.dump(users, f, indent=4)

# Get XP required for next level
def xp_for_next_level(level):
    return level * 50

# Update user's XP and Level
def add_xp(user_id, amount):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"xp": 0, "level": 1}

    users[user_id]['xp'] += amount

    # Level up logic
    while users[user_id]['level'] < 100 and users[user_id]['xp'] >= xp_for_next_level(users[user_id]['level']):
        users[user_id]['level'] += 1

    save_users()

# Command: Log Activity
@bot.command()
async def activity(ctx, activity_name: str, minutes: int):
    activity_name = activity_name.lower()
    if activity_name not in XP_RATES:
        await ctx.send(f"Invalid activity. Choose from: {', '.join(XP_RATES.keys())}")
        return

    xp_gained = XP_RATES[activity_name] * minutes
    add_xp(ctx.author.id, xp_gained)

    user_data = users[str(ctx.author.id)]
    current_level = user_data['level']
    current_xp = user_data['xp']
    next_level_xp = xp_for_next_level(current_level)

    await ctx.send(f"{ctx.author.mention} you earned **{xp_gained} XP** for {minutes} minutes of {activity_name.replace('_', ' ')}!\n"
                   f"Current XP: **{current_xp}**, Level: **{current_level}** (Next Level at {next_level_xp} XP)")

# Command: Check XP
@bot.command()
async def xp(ctx):
    user_id = str(ctx.author.id)
    if user_id not in users:
        await ctx.send("You have no XP yet. Start with `!activity`!")
        return

    user_data = users[user_id]
    current_xp = user_data['xp']
    current_level = user_data['level']
    next_level_xp = xp_for_next_level(current_level)

    await ctx.send(f"{ctx.author.mention}\n"
                   f"Level: **{current_level}**\n"
                   f"XP: **{current_xp} / {next_level_xp}**\n"
                   f"XP needed for next level: **{next_level_xp - current_xp} XP**")

# Command: Leaderboard
@bot.command()
async def leaderboard(ctx):
    if not users:
        await ctx.send("No users with XP yet!")
        return

    sorted_users = sorted(users.items(), key=lambda x: x[1]['xp'], reverse=True)
    embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())

    for idx, (user_id, data) in enumerate(sorted_users[:10], start=1):
        try:
            user = await bot.fetch_user(int(user_id))
            username = user.name
        except:
            username = "Unknown User"

        embed.add_field(name=f"{idx}. {username}", value=f"Level {data['level']} - {data['xp']} XP", inline=False)

    await ctx.send(embed=embed)

# Run bot
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.run(TOKEN)
