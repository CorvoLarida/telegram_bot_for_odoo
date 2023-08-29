from dotenv import load_dotenv
import telebot.async_telebot
from telebot.asyncio_storage.memory_storage import StateMemoryStorage
import os
from telebot import asyncio_filters

load_dotenv()
api_key = os.getenv("TELEGRAM_BOT_API_KEY")
bot = telebot.async_telebot.AsyncTeleBot(api_key, state_storage=StateMemoryStorage())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
print("Bot instance created.")
