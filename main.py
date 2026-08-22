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

#WebScraper TEST
def scrape_test_jobs():
    url = "https://realpython.github.io/fake-jobs/"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    jobs = soup.find_all("h2" , class_="title")
    
    for job in jobs:
        print(job.text.strip())

#scraping for jobs on adzuna
def scrape_adzuna_jobs():
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

    params = {
        "app_id": adzuna_app_id,
        "app_key": adzuna_app_key,
        "results_per_page": 5,
        "what": "IT Intern",
        "where": "United States",
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)

    data = response.json()

    jobs = data.get("results", [])

    return jobs

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
# @bot.command()
# async def jobs(ctx):
#     await ctx.send("🔎 Searching for IT internships...")

#     jobs_found = scrape_adzuna_jobs()

#     for job in jobs_found:
#         title = job.get("title", "Unknown Job")

#         await ctx.send(f"💼 **{title}**")

@bot.command()
async def jobs(ctx):
    await ctx.send("🔎 Searching for IT internships...")

    jobs_found = scrape_adzuna_jobs()

    for job in jobs_found:
        title = job.get("title", "Unknown Job")

        company = job.get("company", {}).get(
            "display_name",
            "Unknown Company"
        )

        location = job.get("location", {}).get(
            "display_name",
            "Unknown Location"
        )

        link = job.get("redirect_url", "No link available")

        await ctx.send(
            f"**{title}**\n"
            f"**Company:** {company}\n"
            f"**Location:** {location}\n"
            f"**Apply:** {link}"
        )
    
bot.run(token, log_handler=handler, log_level=logging.DEBUG)