#try to open .json 'memory' file which is user-specific

#need option for user to delete their 'memory' from the bot...or opt out of the memory storage

#if user not found, create new 'memory' {} for that user

#maybe a 'star knowledge' .json?

#maybe some 'basic' memory as well, such as the date and local time, etc.

#brain/user_memory.json, brain/basic_memory.json, brain/star_memory.json

#if not found, just create some sort of 'goldfish memory' which stores the user's last
#five messages

import json
import os

user_memory = '/brain/user_memory.json'
basic_memory = '/brain/basic_memory.json'
star_memory = '/brain/star_memory.json'

def load_user_memory(user_memory_path):
    #load user "history" file or start empty
    if os.path.exists(user_memory_path):
        
        #if the file exists but is empty...initialize it
        if os.path.getsize(user_memory_path) == 0:
           
            with open(user_memory_path, 'w') as f:
                json.dump({}, f)
            return {}

        with open(user_memory_path, "r") as f:
            user_histories = json.load(f)
    else:
        user_histories = {}
        print('*_memory.json not found in $/brain/. Defaulting to permanent amnesia for all users.')
    
    return user_histories

def save_user_histories(user_memory_path, user_histories):
    with open(user_memory_path, "w") as f:
        json.dump(user_histories, f, indent=2)