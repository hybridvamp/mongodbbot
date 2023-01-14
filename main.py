import json
import os
from io import BytesIO
from telethon import TelegramClient, events
from telethon.tl.types import KeyboardButton
from pymongo import MongoClient, errors
from tqdm import tqdm

# get the Telegram bot token, API ID and API Hash from environment variables
bot_token = os.environ.get('BOT_TOKEN')
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')

client = TelegramClient(session='session_name', api_id=api_id, api_hash=api_hash)
client.start(bot_token=bot_token)

@client.on(events.NewMessage)
async def handler(message):
    if message.text.startswith('mongodb'):
        try:
            mongo_client = MongoClient(message.text)
            # check the server status
            mongo_client.server_info()
            # send message with buttons
            buttons = [
                [KeyboardButton.inline("Backup"), KeyboardButton.inline("Restore")]
            ]
            await message.reply("Connection successful! Please select an option:")
            await message.reply_markup(buttons=buttons)
        except errors.ServerSelectionTimeoutError as e:
            await message.reply(f"Connection failed: {e}")
        except Exception as e:
            await message.reply(f"An error occurred: {e}")
    elif message.text == '/backup':
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
        await message.reply_document(data_file, filename='backup.json')
    elif message.text == '/restore':
        # send message with restore options
        await message.reply("Please select an option to restore from: \n1. File sent by user \n2. Another MongoDB connection string")
        user_response = await client.wait_for_message(chat_id=message.chat_id)
        if user_response.text == '1':
            # restore from file sent by user
            file_data = await client.download_media(await client.get_messages(message.chat_id, filter=lambda m: m.document and 'backup.json' in m.file.name))
            data = json.loads(file_data.read())
            mongo_client = MongoClient(connection_string)
            # restore the data to MongoDB using tqdm
            with tqdm(total=len(data)) as pbar:
                mongo_client.db.collection.insert_many(data, ordered=False, bypass_document_validation=True, callback=lambda _, inserted: pbar.update(inserted))
            await message.reply("Data restored successfully!")
        elif user_response.text == '2':
            # ask for connection string
            await message.reply("Please provide the MongoDB connection string")
            connection_string = await client.wait_for_message(chat_id=message.chat_id)
            mongo_client = MongoClient(connection_string)
            # restore from another MongoDB connection string
            data = list(mongo_client.db.collection.find())
            # restore the data to MongoDB using tqdm
            with tqdm(total=len(data)) as pbar:
                mongo_client.db.collection.insert_many(data, ordered=False, bypass_document_validation=True, callback=lambda _, inserted: pbar.update(inserted))
            await message.reply("Data restored successfully!")
client.start()
client.run_until_disconnected()