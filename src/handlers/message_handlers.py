import time
from src.create_bot import bot
from src.helper_methods import pm_find_user, get_keyboard
from src.States import MyStates


async def start(message):
    text = "Бот привязывает Telegram аккаунт пользователя к PM.\n" \
           "Доступные команды:\n" \
           "\t\t/link_to_pm - привязать Telegram аккаунт к PM\n" \
           "\t\t/unlink_from_pm - отвязать Telegram аккаунт от PM"
    await bot.send_message(message.from_user.id, text=text)


async def pm_start(message):
    text = message.text
    if text == "/link_to_pm":
        status = "to connect"
        text = "Через что привязать Telegram аккаунт к PM ?"
    elif text == "/unlink_from_pm":
        status = "to disconnect"
        text = "Через что отвязать Telegram аккаунт от PM ?"
    await bot.delete_state(message.from_user.id, message.from_user.id)
    await bot.set_state(message.from_user.id, MyStates.connection_data_type, message.from_user.id)
    await bot.send_message(message.from_user.id, text=text, reply_markup=get_keyboard("choice"))
    await bot.add_data(message.from_user.id, message.from_user.id, status=status)


async def get_connection_data(message):
    async with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
        data_type = data["data_type"]
        user_status = data["status"]
    if data_type == "username":
        text = "Вы выбрали для"
        if user_status == "to connect":
            text += " привязки Telegram аккаунта к PM"
        elif user_status == "to disconnect":
            text += " отвязки Telegram аккаунта от PM"
        text += " свое имя пользователя Telegram"
        user_data = message.from_user.username
        await bot.send_message(message.from_user.id, text=text)
        time.sleep(1.5)
    else:
        user_data = message.text
    await pm_find_user(message, data_type, user_data)


def register_message_handlers():
    bot.register_message_handler(callback=start, commands=["start", "help"])
    bot.register_message_handler(callback=pm_start, commands=["link_to_pm", "unlink_from_pm"])
    bot.register_message_handler(callback=get_connection_data, state=MyStates.connection_data)

    print("Message Handlers registered.")
