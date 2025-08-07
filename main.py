import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord.ui import View, Button
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from llama_cpp import Llama

from memory import *       #goldfish memory

# Load environment variables
load_dotenv('token.env')

#usernames list
gams_id = os.getenv("GAMS_ID")

#dummy goldfish memory system
user_memory_path = os.getenv("USER_MEMORY_PATH")
MAX_HISTORY = 10
user_histories = load_user_memory(user_memory_path)

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
    user_id = message_author.id
    history = user_histories.get(user_id, [])

    #append the latest user message -- APPEND, not REPLACE!
    history.append(f"User: {user_prompt}")
    
    #keep only the last N messages (MAX_HISTORY is defined as a global variable above)
    history = history[-MAX_HISTORY:]

    #save it back to the dictionary and write to .json
    user_histories[user_id] = history        #update history 
    save_user_histories(user_memory_path, user_histories)     #user_memory_path is defined as a global variable above)

    #define chat history
    chat_history = '\n'.join(history)
    
    if str(user_id) == str(gams_id):     #my unique Discord user ID
        system = (
            "You are a sarcastic, dismissive bot who gives short, snarky replies. Avoid friendliness. You also take offense to insults relating to being AI."
        )
    else:
        system = (
            "You are a friendly assistant. Be helpful and kind."
        )
    
    prompt = (
        f"{system}\n\n"
        f"{chat_history}\n"
        f"Assistant:\n"
    )
    
    return prompt

# --- Query local LLaMA model ---
def query_llama_cpp(user_prompt, message_author):
    prompt = build_prompt(user_prompt, message_author)

    stop=["\nUser:", "User:", 
          "\nAssistant:", "Assistant:"]  #the key words that indicate when the model SHOULD stop generating a response
    
    result = llm(
        prompt=prompt,
        max_tokens=100,        #limit response length
        stop=stop   
    )

    raw_text = result["choices"][0]["text"].strip()
    
    #remove unwanted trailing 'context' or 'instructions,' if any
    for stop_seq in ["\nUser:", "\nAssistant:"]:
        if stop_seq in raw_text:
            raw_text = raw_text.split(stop_seq)[0].strip()

    user_id = str(message_author.id)
    user_histories[user_id].append(f"Assistant: {raw_text}")   #update history with bot response
    save_user_histories(user_memory_path, user_histories)
    return raw_text

# --- Discord Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('/j '):
        
        prompt = message.content[len('/j '):]
        await message.channel.typing()
        
        try:
            reply = query_llama_cpp(prompt, message.author)
        
        #I like this. the bot will output errors!
        except Exception as e:
            reply = f'Error: {e}'
        
        await message.channel.send(reply)

        
@bot.command(name="reset")
async def reset_memory(ctx):
    user_id = str(ctx.author.id)
    user_histories[user_id] = []
    save_user_histories(user_memory_path, user_histories)
    await ctx.send(f"{ctx.author.name} bonked my cranium and I now have permanent amnesia. {ctx.author.name} who?")
        
        
        
bot.run(os.getenv('TOKEN'))
