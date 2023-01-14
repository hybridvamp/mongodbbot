import json
import os
from io import BytesIO
from telethon import TelegramClient
from pymongo import MongoClient
from tqdm import tqdm

# get the Telegram bot token, API ID and API Hash from environment variables
bot_token = os.environ.get('BOT_TOKEN')
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')

client = TelegramClient('session_name', api_id, api_hash,bot_token=bot_token)

@client.on_message()
async def handler(message):
    if message.text == '/backup':
        # ask for connection string
        await message.reply("Please provide the MongoDB connection string")
        connection_string = await client.wait_for_message(chat_id=message.chat_id)
        mongo_client = MongoClient(connection_string)
        # backup the data from MongoDB
        data = list(mongo_client.db.collection.find())
        # create a bytesIO object to hold the data
        data_file = BytesIO()
        # save the data to the bytesIO object using tqdm
        with tqdm(total=len(data)) as pbar:
            json.dump(data, data_file, default=lambda o: pbar.update())
        data_file.seek(0)
        # send the file to the user
        await message.reply_document(data
