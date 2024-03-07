from aiogram.dispatcher.filters.state import State, StatesGroup


class FeedBackState(StatesGroup):
    body = State()


class RegisterUser(StatesGroup):
    phone = State()
    name = State()
    code = State()


class LocationState(StatesGroup):
    location = State()