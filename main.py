import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord.ui import View, Button
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from llama_cpp import Llama

# Load environment variables
load_dotenv('token.env')

#dummy goldfish memory system
user_histories = {}
MAX_HISTORY = 5

#load model using llama-cpp-python
model_path = os.getenv("MODEL_PATH")
llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0,     #add this line for CPU-only systems
    temperature=0.7,    #adjust accordingly. higher temperature yields a more...creative response.
    top_p=0.95,
    repeat_penalty=1.1,
    verbose=False
)

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)

#force it to be a snarky S.O.B.
def build_prompt(user_prompt, message_author):
    username = message_author.name
    history = user_histories.get(username, [])

    #append the latest user message
    history.append(f"User: {user_prompt}")
    
    #keep only the last few messages
    history = history[-MAX_HISTORY:]

    #save it back
    user_histories[username] = history

    #define chat history
    chat_history = '\n'.join(history)

    if username.lower() == 'gammaspire':
        system = (
            "You are a snarky assistant who is short, a bit dismissive, and a little sarcastic. "
            "Do not exceed 50 words. Respond directly and avoid pleasantries."
        )
    else:
        system = (
            "You are a pleasant assistant who interacts kindly with others. "
            "Do not exceed 50 words unless you are asked a question, in which case do not exceed 150 words."
        )

    return (
        f"{system}\n\n"
        f"Here is your recent conversation history:\n"
        f"{chat_history}\n\n"
        f"Assistant:"
    )

# --- Query local LLaMA model ---
def query_llama_cpp(user_prompt, message_author):
    prompt = build_prompt(user_prompt, message_author)

    result = llm(
        prompt=prompt,
        max_tokens=200,        #limit response length
        stop=["User:", "Assistant:"]
    )

    text = result["choices"][0]["text"].strip()
    user_histories[message_author.name].append(f"Assistant: {text}")
    return text

# --- Discord Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('/ask '):
        prompt = message.content[len('/ask '):]
        await message.channel.typing()
        try:
            reply = query_llama_cpp(prompt, message.author)
        except Exception as e:
            reply = f'Error: {e}'
        await message.channel.send(reply)

bot.run(os.getenv('TOKEN'))
