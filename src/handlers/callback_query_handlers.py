from src import helper_methods
from src.create_bot import bot
from src.handlers import message_handlers
from src.States import MyStates


async def callback_cancel(call):
    await bot.send_message(call.from_user.id, text="Отмена выполнения команды")
    await bot.delete_state(call.from_user.id, call.from_user.id)


async def callback_choice(call):
    data_type = call.data
    await bot.add_data(call.from_user.id, call.from_user.id, data_type=data_type)
    if data_type == "username":
        data_type_name = "Имя пользователя Telegram"
        await bot.add_data(call.from_user.id, call.from_user.id, data_type_name=data_type_name)
        await message_handlers.get_connection_data(call)
    else:
        text = "Введите ваш "
        if data_type == "name":
            data_type_name = "ФИО"
        elif data_type == "phone":
            data_type_name = "мобильный телефон"
        elif data_type == "email":
            data_type_name = "адрес электронной почты"
        text += f"{data_type_name} в PM"
        await bot.add_data(call.from_user.id, call.from_user.id, data_type_name=data_type_name)
        await bot.send_message(call.from_user.id, text=text)
    await bot.set_state(call.from_user.id, MyStates.connection_data, call.from_user.id)


async def callback_affirm(call):
    async with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data_type_name = data["data_type_name"]
        user_status = data["status"]
        contact_to_write = data["pm_profile"]
    if user_status == "to connect":
        action = "connect"
    elif user_status == "to disconnect":
        action = "disconnect"
    if call.data == "continue":
        await helper_methods.write_contact_data(call, action, contact_to_write)
    elif call.data == "edit":
        await bot.send_message(call.from_user.id, text=f"Введите ваш {data_type_name} в PM")
        await bot.set_state(call.from_user.id, MyStates.connection_data, call.from_user.id)


def register_callback_query_handlers():
    bot.register_callback_query_handler(callback=callback_cancel, func=lambda call: call.data in ["cancel"],
                                        state=[MyStates.connection_data_type, MyStates.connection_data])
    bot.register_callback_query_handler(callback=callback_choice,
                                        func=lambda call: call.data in ["name", "phone", "email", "username"],
                                        state=MyStates.connection_data_type)
    bot.register_callback_query_handler(callback=callback_affirm, func=lambda call: call.data in ["continue", "edit"],
                                        state=MyStates.connection_data)

    print("Callback Handlers registered.")
