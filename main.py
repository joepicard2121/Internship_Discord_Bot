import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
adzuna_app_id = os.getenv('ADZUNA_APP_ID')
adzuna_app_key = os.getenv('ADZUNA_APP_KEY')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

#WebScraper
def scrape_jobs():
    url = "https://realpython.github.io/fake-jobs/"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    print(soup.title)

#Events
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

#Welcoming new members
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")
    
#Commands
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
    
#Job search command
@bot.command()
async def jobs(ctx):
    await ctx.send("🔎 Searching for IT internships...")
    scrape_jobs()
    
bot.run(token, log_handler=handler, log_level=logging.DEBUG)