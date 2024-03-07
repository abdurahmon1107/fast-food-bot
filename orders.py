# from aiogram import types, executor, Bot, Dispatcher
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher import FSMContext
# from api_requests import create_user, check_user, feedback, get_branches, get_products
# from utils import send_verification_code
# import random
# import os
# import environ
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
#
# from buttons import menu_button, to_back, get_branch_buttons, get_product_buttons, order_button
# from states import FeedBackState, RegisterUser, LocationState
#
# env = environ.Env()
# env.read_env("../.env")
#
# bot = Bot(token=env.str("BOT_TOKEN"))
# dp = Dispatcher(bot, storage=MemoryStorage())
#
#
# async def on_startup(dp):
#     print("Bot started")
#
#
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: types.Message):
#     await message.answer("""
#                                     Buyurtma berishni boshlash uchun 🛍 Buyurtma berish tugmasini bosing \n\n
# Shuningdek, aksiyalarni ko'rishingiz va bizning filiallar bilan tanishishingiz mumkin""",
#                                     reply_markup=order_button, )
#
# @dp.message_handler(Text("🗂 | Buyurtma berish"))
# async def get_branch(message: types.Message):
#     keyboard = get_product_buttons()
#     await message.reply("Salom! Mening fast food botimizga xush kelibsiz. Iltimos, filialni tanlang:",
#                         reply_markup=keyboard)
#
#
# def is_valid_branch_name(category):
#     branches = get_products()
#     return any(branch['category'] == category for branch in branches['results'])
#
#
# @dp.message_handler(lambda message: is_valid_branch_name(message.text))
# async def branch_info(message: types.Message):
#     branches = get_products()
#     selected_branch = next((branch for branch in branches['results'] if branch['category'] == message.text), None)
#
#     if selected_branch:
#
#         text = f"📍 Filial: {selected_branch['name']}\n\n"
#         text += f"🗺 Manzil: {selected_branch['price']}\n\n"
#
#         await message.answer_photo(photo=selected_branch['image'], caption=text)
#
#     else:
#         await message.answer("Bunday categoriya topilmadi.", reply_markup=get_product_buttons())
#
#
#
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp, on_startup=on_startup)
#
#
#
