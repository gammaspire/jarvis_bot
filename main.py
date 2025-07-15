import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord.ui import View, Button
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import openai


################################################################################
################################################################################
################################################################################

#general variables

#load environment variables from 'token.env' file
load_dotenv('token.env')

#define intents; required to read message content in on_message
intents = discord.Intents.default()
intents.message_content = True

#create bot instance (inherits from discord.Client)
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)   #I am creating my own help_command

#begin scheduler... will generate scheduled messages!
scheduler = AsyncIOScheduler()

#load api key for openai
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

################################################################################
################################################################################
################################################################################

#commands

@bot.command()
async def ask(ctx, *, question):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    await ctx.send(response.choices[0].message.content)

    
################################################################################
################################################################################
################################################################################

#activate bot

bot.run(os.getenv('TOKEN'))