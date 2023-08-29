from telebot.asyncio_handler_backends import State, StatesGroup


class MyStates(StatesGroup):
    connection_data_type = State()
    connection_data = State()
