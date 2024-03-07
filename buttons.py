from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from api_requests import get_branches, get_categories, get_products, get_products_by_category

menu_button = ReplyKeyboardMarkup(resize_keyboard=True,
                                  keyboard=[
                                      [
                                          KeyboardButton(text='🗂 | Asosiy menu')
                                      ]])
order_button = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[
                                       [
                                           KeyboardButton(text='🗂 | Buyurtma berish')
                                       ]])

to_back = ReplyKeyboardMarkup(resize_keyboard=True,
                              one_time_keyboard=True,
                              keyboard=[
                                  [
                                      KeyboardButton(text='⬅️ Orqaga')
                                  ]])


def menu_orders() -> types.ReplyKeyboardMarkup:
    keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboards.add(types.KeyboardButton(text="🏃 Olib ketish"), types.KeyboardButton(text="🚖 Yetkazib berish"))
    keyboards.add(types.KeyboardButton(text=" ⬅️ Orqaga"))
    return keyboards


def get_branch_buttons():
    global to_back
    branches = get_branches()
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    row = []
    for branch in branches['results']:
        btn = types.KeyboardButton(branch['name'])
        row.append(btn)
        if len(row) >= 2 or branch == branches['results'][-1]:
            keyboards.add(*row)  # Qatorni klaviaturaga qo'shamiz
            row = []
    keyboards.add(types.KeyboardButton("⬅️ Orqaga"))
    return keyboards


def get_category_buttons():
    categories = get_categories()
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for category in categories['results']:
        btn = types.KeyboardButton(category['name'])
        row.append(btn)
        if len(row) >= 2 or category == categories['results'][-1]:
            keyboards.add(*row)  # Qatorni klaviaturaga qo'shamiz
            row = []
    keyboards.add(types.KeyboardButton("⬅️ Orqaga"))
    return keyboards


def get_category_product_buttons():
    products = get_products()
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for product in products['results']:
        btn = types.KeyboardButton(product['name'])
        row.append(btn)
        if len(row) >= 2 or product == products['results'][-1]:
            keyboards.add(*row)  # Qatorni klaviaturaga qo'shamiz
            row = []
    keyboards.add(types.KeyboardButton("⬅️ Orqaga"))
    return keyboards


# Kategoriya nomi bo'yicha mahsulotlarni olish va ushbu mahsulotlarni buttonlar sifatida qaytaruvchi funksiya
def get_products_buttons(category_name):
    categories = get_categories()
    category_id = None
    for category in categories['results']:
        if category['name'] == category_name:
            category_id = category['id']
            break

    if category_id is None:
        return None

    products = get_products_by_category(category_id)
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    if products:
        for product in products['results']:
            btn = KeyboardButton(product['name'])
            row.append(btn)
            if len(row) >= 2 or product == products['results'][-1]:
                keyboards.add(*row)  # Qatorni klaviaturaga qo'shamiz
                row = []
    keyboards.add(KeyboardButton("⬅️ Orqaga"))
    return keyboards
