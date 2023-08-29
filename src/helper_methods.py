import xmlrpc
from xmlrpc import client
from telebot import types
from src.create_bot import bot
from src.PMConnection import PMConnection


def get_keyboard(keyboard_type: str):
    def get_key(text, callback_data):
        return types.InlineKeyboardButton(text=text, callback_data=callback_data)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    all_keys = []
    if keyboard_type == "choice":
        all_keys.append(get_key("ФИО", "name"))
        all_keys.append(get_key("Телефон", "phone"))
        all_keys.append(get_key("Электронная почта", "email"))
        all_keys.append(get_key("Имя пользователя Telegram", "username"))
    elif keyboard_type == "affirm":
        all_keys.append(get_key("Продолжить", "continue"))
        all_keys.append(get_key("Исправить", "edit"))
    elif keyboard_type == "affirm_final":
        all_keys.append(get_key("Продолжить", "continue"))
    else:
        pass
    all_keys.append(get_key("Отменить", "cancel"))
    for key in all_keys:
        keyboard.add(key)
    return keyboard


async def pm_find_user(message, data_type, user_data):
    if not await PMConnection.db_has_bot():
        await bot.delete_state(message.from_user.id, message.from_user.id)
        await bot.send_message(message.from_user.id,
                               "Ошибка. Бот не имеет доступа к PM.")
        return "Wrong credentials"
    else:
        await bot.send_message(message.from_user.id, "Поиск профиля в PM...")

        if data_type == "name":
            search_domain = [["name", "ilike", user_data]]
        elif data_type == "phone":
            search_domain = ["|", "|", ["phone_sanitized", "=", user_data],
                             ["phone", "=", user_data],
                             ["mobile", "=", user_data]]
        elif data_type == "email":
            search_domain = [["email", "=", user_data]]
        elif data_type == "username":
            search_domain = [["telegram_username", "=", user_data]]
        else:
            await bot.delete_state(message.from_user.id, message.from_user.id)
            bot.send_message(message.from_user.id, "Вы не выбрали способ регистрации в PM.")
            return "No search data"
        contact_to_write = await PMConnection.get_contacts_to_write(search_domain)

        if isinstance(contact_to_write, xmlrpc.client.Fault):
            await bot.delete_state(message.from_user.id, message.from_user.id)
            await bot.send_message(message.from_user.id, "Ошибка. Обратитесь к администратору PM для настройки бота.")
            raise contact_to_write
        else:
            if not contact_to_write:
                await bot.delete_state(message.from_user.id, message.from_user.id)
                await bot.send_message(message.from_user.id, "Ошибка. Поиск не дал результатов.")
                return "Nothing Found"
            if len(contact_to_write) > 1:
                await bot.delete_state(message.from_user.id, message.from_user.id)
                text = "Ошибка. Найдено более 1 человека, подходящих под критерии поиска:\n"
                for _, contact in enumerate(contact_to_write):
                    text += f"      {contact.get('name')}\n"
                await bot.send_message(message.from_user.id, text=text)
                return "Too many people found"

            async with bot.retrieve_data(message.from_user.id, message.from_user.id) as data:
                user_status = data["status"]
                data_type = data["data_type"]
            is_connected = not not contact_to_write[0].get("telegram_chat_id")
            await bot.add_data(message.from_user.id, message.from_user.id, pm_profile=contact_to_write[0].get("id"))
            text = f"Найден ваш профиль в PM:\n         {contact_to_write[0].get('name')}.\n" \
                   f"Статус: {'Привязан' if is_connected else 'Отвязан'}\n"

            if (user_status == "to connect" and is_connected) or (user_status == "to disconnect" and not is_connected):
                await bot.delete_state(message.from_user.id, message.from_user.id)
                await bot.send_message(message.from_user.id, text=text)
                return "Already"
            else:
                text += f"Продолжить {'привязку' if user_status == 'to connect' else 'отвязку'} ?"
                await bot.send_message(message.from_user.id, text=text,
                                       reply_markup=get_keyboard(
                                           "affirm_final" if data_type == "username" else "affirm"))
            del search_domain
            del text
            del contact_to_write


async def write_contact_data(message, action, contact_to_write):
    await bot.delete_state(message.from_user.id, message.from_user.id)
    if action == "connect":
        data = message.from_user.id
        final_text = "Telegram аккаунт успешно привязан к PM."
    elif action == "disconnect":
        data = False
        final_text = "Telegram аккаунт успешно отвязан от PM."
    await bot.send_message(message.from_user.id, text="Пожалуйста подождите...")

    written = await PMConnection.write_to_contact(contact_to_write, write_data={"telegram_chat_id": data})
    del data
    if isinstance(written, xmlrpc.client.Fault):
        await bot.delete_state(message.from_user.id, message.from_user.id)
        await bot.send_message(message.from_user.id, "Ошибка. Обратитесь к администратору PM для настройки бота.")
        raise written
    else:
        if written:
            await bot.send_message(message.from_user.id, text=final_text)
            return "Success"
        else:
            await bot.send_message(message.from_user.id, "Ошибка.")
            return "Fail"
