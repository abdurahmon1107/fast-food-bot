import io

from aiogram import types, executor, Bot, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from api_requests import create_user, check_user, feedback, get_branches, get_categories, get_products
from utils import send_verification_code
from aiogram.types.web_app_info import WebAppInfo
import random
import environ
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from buttons import (menu_button, to_back, get_branch_buttons, get_category_buttons,
                     get_products_by_category, get_products_buttons, menu_orders)
from states import FeedBackState, RegisterUser, LocationState

env = environ.Env()
env.read_env(".env")

bot = Bot(token=env.str("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    print("Bot started")


def distance_between_points(point1, point2) -> float:
    """point1 and point2 are tuples of (x, y) coordinates
        return the distance between the two points in float
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


def menu_keyboards() -> types.ReplyKeyboardMarkup:
    keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboards.add(types.KeyboardButton(text="🛍 Buyurtma berish"))
    keyboards.add(types.KeyboardButton(text="✍️ Talab va Takliflar"), types.KeyboardButton(text="🏘 Barcha filiallar"))
    keyboards.add(types.KeyboardButton(text="ℹ️ Biz haqimizda"), types.KeyboardButton(text="📋 Mening buyurtmalarim"))
    keyboards.add(types.KeyboardButton(text="⚙️ Sozlamalar"))
    keyboards.add(types.KeyboardButton(text=" Eng yaqin filialni aniqlash"))
    return keyboards


keyboards = menu_keyboards()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    chat_id = message.chat.id

    if check_user(str(chat_id)):
        return await message.answer("""
                                    Buyurtma berishni boshlash uchun 🛍 Buyurtma berish tugmasini bosing \n\n
Shuningdek, aksiyalarni ko'rishingiz va bizning filiallar bilan tanishishingiz mumkin""",
                                    reply_markup=keyboards, )
    reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply.add(types.KeyboardButton(text='Telefon raqamni yuborish', request_contact=True))
    await message.answer("Iltimos telefon raqamingizni kiriting:", reply_markup=reply)
    await RegisterUser.phone.set()


@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=RegisterUser.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await message.answer("FISH kiriting:")
    await RegisterUser.next()


@dp.message_handler(state=RegisterUser.name)
async def get_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    code = random.randint(1000, 9999)
    await state.update_data(code=code)
    await message.answer(f"Kod: {code}")
    phone = (await state.get_data()).get('phone')
    send_verification_code(phone=phone, code=code)
    await message.answer("Telefon raqamingizga kod yuborildi. Iltimos kodni kiriting:")
    await RegisterUser.next()


@dp.message_handler(state=RegisterUser.code)
async def get_code(message: types.Message, state: FSMContext):
    code = message.text
    data = await state.get_data()
    if int(code) == data.get('code'):
        phone = data.get('phone')
        if not phone.startswith("+"):
            phone = "+" + phone
        a = create_user(data.get('name'), phone, message.chat.id)
        if a.status_code == 400:
            await message.answer("Ma'lumot xato kiritildi")
            await state.finish()
            return
        token = a.json().get('token')
        await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz!", reply_markup=menu_keyboards())
        await state.finish()
    else:
        await message.answer("Kod xato!")
        await state.finish()


@dp.message_handler(Text("✍️ Talab va Takliflar"))
async def feedback1(message: types.Message):
    await message.answer("Izoh qoldiring. Sizning fikringiz biz uchun muhim.", reply_markup=to_back)
    await FeedBackState.body.set()


@dp.message_handler(state=FeedBackState.body)
async def set_skills(message: types.Message, state: FSMContext):
    if feedback(message.from_user.id, message.text):
        await message.answer("✅Izoh jo'natildi", reply_markup=keyboards)
    else:
        await message.answer("Siz ro'yhatdan otmagansz", reply_markup=keyboards)

    await state.finish()


@dp.message_handler(Text("🏘 Barcha filiallar"))
async def get_branch(message: types.Message):
    keyboard = get_branch_buttons()
    await message.reply("Salom! Mening fast food botimizga xush kelibsiz. Iltimos, filialni tanlang:",
                        reply_markup=keyboard)


def is_valid_branch_name(name):
    branches = get_branches()
    return any(branch['name'] == name for branch in branches['results'])


@dp.message_handler(lambda message: is_valid_branch_name(message.text))
async def branch_info(message: types.Message):
    branches = get_branches()
    keyboards = get_category_buttons()
    selected_branch = next((branch for branch in branches['results'] if branch['name'] == message.text), None)

    if selected_branch:

        text = f"📍 Filial: {selected_branch['name']}\n\n"
        text += f"🗺 Manzil: {selected_branch['address']}\n\n"
        text += f"🏢 Orientir: {selected_branch['destination']}\n\n"
        text += f"☎️ Telefon raqami: {selected_branch['contact']}\n\n"
        text += f"🕙 Ish vaqti: {selected_branch['from_time']}-{selected_branch['to_time']}\n\n"

        await message.answer(text)
        await message.answer_location(latitude=selected_branch['latitude'], longitude=selected_branch['longitude'], reply_markup=keyboards)

    else:
        await message.answer("Bunday filial topilmadi.", reply_markup=get_branch_buttons())


@dp.message_handler(Text("Eng yaqin filialni aniqlash"))
async def get_close_distance(message: types.Message):
    map_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    map_keyboard.add(types.KeyboardButton(text="🗺 Geolokatsiyamni yuborish", request_location=True))
    map_keyboard.add(types.KeyboardButton(text="⬅️ Orqaga"))
    await message.answer("Iltimos, geolokatsiyangizni yuboring:", reply_markup=map_keyboard)
    await LocationState.location.set()


@dp.message_handler(content_types=types.ContentTypes.LOCATION, state=LocationState.location)
async def get_close_branch(message: types.Message, state: FSMContext):
    branches = get_branches()
    user_location = (message.location.latitude, message.location.longitude)
    distances = []

    for branch in branches['results']:
        branch_location = (branch['latitude'], branch['longitude'])
        distance = distance_between_points(user_location, branch_location)
        distances.append(distance)
    min_distance = min(distances)
    min_index = distances.index(min_distance)
    selected_branch = branches['results'][min_index]

    text = f"📍 Filial: {selected_branch['name']}\n\n"
    text += f"🗺 Manzil: {selected_branch['address']}\n\n"
    text += f"🏢 Orientir: {selected_branch['destination']}\n\n"
    text += f"☎️ Telefon raqami: {selected_branch['contact']}\n\n"
    text += f"🕙 Ish vaqti: {selected_branch['from_time']}-{selected_branch['to_time']}\n\n"

    await message.answer(text)
    await message.answer_location(latitude=selected_branch['latitude'], longitude=selected_branch['longitude'])
    await state.finish()


@dp.message_handler(Text("⬅️ Orqaga"))
async def get_branch(message: types.Message):
    await message.answer("Buyurtma berishingiZ mumkin",
                         reply_markup=menu_keyboards())


@dp.message_handler(Text("🛍 Buyurtma berish"))
async def get_branch(message: types.Message):
    chat_id = message.chat.id
    await message.answer("Interaktiv menu orqali buyurtma bering: ",
                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Interaktiv menu",
                                                                                      web_app=WebAppInfo(
                                                                                          url=f"https://food-delivery-react-test.netlify.app/?{chat_id}"))))


# # Buyurtma uchun Handler
# @dp.message_handler(Text("🛍 Buyurtma berish"))
# async def get_branch(message: types.Message):
#     keyboard = menu_orders()
#     await message.reply("Salom! Mening fast food botimizga xush kelibsiz. Iltimos, filialni tanlang:",
#                         reply_markup=keyboard)

# olib ketish uchun handler
@dp.message_handler(Text("🏃 Olib ketish"))
async def get_branch(message: types.Message):
    keyboard = get_branch_buttons()
    await message.reply("O'zingizga qulay bolgan filialni tanlang: ",
                        reply_markup=keyboard)
# yetkazib berish uchun handler
@dp.message_handler(Text("🚖 Yetkazib berish"))
async def get_branch(message: types.Message):
    keyboard = get_category_buttons()
    await message.reply("Kategoriyalardan birini tanlang: ",
                        reply_markup=keyboard)

# Kategoriya uchun :
def is_valid_category_name(name):
    categories = get_categories()
    return any(category['name'] == name for category in categories['results'])


@dp.message_handler(lambda message: is_valid_category_name(message.text))
async def branch_info(message: types.Message):
    category = get_categories()
    selected_branch = next((branch for branch in category['results'] if branch['name'] == message.text), None)
    if selected_branch:
        text = f"📍 Filial: {selected_branch['name']}\n\n"
        text += f"🗺 Manzil: {selected_branch['id']}\n\n"

        await message.answer(text, reply_markup=get_products_buttons(message.text))
    else:
        await message.answer("hech narsa")


def is_valid_product_name(name):
    products = get_products()
    return any(product['name'] == name for product in products['results'])


# rasmni yuklab olish uchun funksiya
import aiohttp


async def download_photo(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
    return None


# mahsulot detailini chiqarish uchun
@dp.message_handler(lambda message: is_valid_product_name(message.text))
async def product_selected(message: types.Message):
    product_info = get_products()
    selected_branch = next((branch for branch in product_info['results'] if branch['name'] == message.text), None)
    if selected_branch:
        text = f"Mahsulot nomi: {selected_branch['name']}\n"
        text += f"Narxi: {selected_branch['price']} so'm\n"

        photo_url = selected_branch['image']
        photo_data = await download_photo(photo_url)
        await message.answer(text)
        # await message.answer_photo(photo=InputFile(io.BytesIO(photo_data), filename="product"), caption=text, reply_markup=get_products_buttons(message.text))
    else:
        await message.answer("Bunday mahsulot topilmadi.", reply_markup=get_category_buttons())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
