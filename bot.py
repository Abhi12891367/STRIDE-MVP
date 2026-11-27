import os
import json
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from services import generate_briefing

load_dotenv(override=True)

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0").strip())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

sent_reminders = set()

@bot.event
async def on_ready():
    print(f"Stride Bot logged in as {bot.user}")
    if not reminder_check.is_running():
        reminder_check.start()

@bot.command(name="briefing")
async def briefing(ctx):
    await ctx.send("Generating your Stride Daily Briefing...")
    summary = generate_briefing()
    await ctx.send(summary[:1990])

@tasks.loop(minutes=5)
async def reminder_check():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return
    with open("mock_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for event in data["calendar"]:
        event_id = event["id"]
        if event_id not in sent_reminders:
            sent_reminders.add(event_id)
            await channel.send(
                f"**Upcoming Reminder:** `{event['title']}` ({event['date']} at {event['start']})"
            )

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
