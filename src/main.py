import asyncio
from src.create_bot import bot
from src.PMConnection import PMConnection
from src.handlers import callback_query_handlers, message_handlers


def main():
    callback_query_handlers.register_callback_query_handlers()
    message_handlers.register_message_handlers()
    PMConnection.create_connection()
    print("Bot is running.")
    asyncio.run(bot.infinity_polling())


if __name__ == "__main__":
    main()
