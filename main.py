import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import requests
#from bs4 import BeautifulSoup
import sqlite3

#creating discord bot
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
adzuna_app_id = os.getenv('ADZUNA_APP_ID')
adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
job_channel_id = int(os.getenv('JOB_CHANNEL_ID'))

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

#Database setup (had help from chatgpt to create database)
conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS posted_jobs (
job_id TEXT PRIMARY KEY
)
""")

conn.commit()

#Helper functions for database (had help from chatgpt to make database)
def job_already_posted(job_id):
    cursor.execute(
        "SELECT 1 FROM posted_jobs WHERE job_id = ?",
        (job_id,)
    )

    return cursor.fetchone() is not None


def save_posted_job(job_id):
    cursor.execute(
        "INSERT OR IGNORE INTO posted_jobs (job_id) VALUES (?)",
        (job_id,)
    )

    conn.commit()

#scraping for jobs on adzuna
def scrape_adzuna_jobs():
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

    params = {
        "app_id": adzuna_app_id,
        "app_key": adzuna_app_key,
        "results_per_page": 50,
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
    
    if not automatic_job_search.is_running():
        automatic_job_search.start()

#Welcoming new members
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")
    
#Commands
    
#Job search command
# @bot.command()
# async def jobs(ctx):
#     await ctx.send("🔎 Searching for IT internships...")

#     jobs_found = scrape_adzuna_jobs()

#     for job in jobs_found:
#         title = job.get("title", "Unknown Job")

#         company = job.get("company", {}).get(
#             "display_name",
#             "Unknown Company"
#         )

#         location = job.get("location", {}).get(
#             "display_name",
#             "Unknown Location"
#         )

#         link = job.get("redirect_url", "No link available")

#         await ctx.send(
#             f"**{title}**\n"
#             f"**Company:** {company}\n"
#             f"**Location:** {location}\n"
#             f"**Apply:** {link}"
#         )

#timer for automatic job searches
@tasks.loop(minutes=30)
async def automatic_job_search():
    print("Searching for new jobs...")

    channel = bot.get_channel(job_channel_id)

    if channel is None:
        print("Job channel not found.")
        return

    jobs_found = scrape_adzuna_jobs()

    for job in jobs_found:
        job_id = job.get("id")

        if not job_id:
            continue

        if job_already_posted(job_id):
            print(f"Skipping duplicate job: {job_id}")
            continue

        title = job.get("title", "Unknown Job")

        company = job.get("company", {}).get(
            "display_name",
            "Unknown Company"
        )

        location = job.get("location", {}).get(
            "display_name",
            "Unknown Location"
        )

        link = job.get(
            "redirect_url",
            "No link available"
        )

        await channel.send(
            f"**{title}**\n"
            f"**Company:** {company}\n"
            f"**Location:** {location}\n"
            f"**Apply:** {link}"
        )

        save_posted_job(job_id)
 
 #bot run   
bot.run(token, log_handler=handler, log_level=logging.DEBUG)