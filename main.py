import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ======================
# CONFIG
# ======================

BOT_TOKEN = "8962279231:AAGUy_bZxxiXTAx6vsx-cMEv1hT0FBbtWLw"
LTC_ADDRESS = "LQ6VgSJo2CA2fPCJQosCBQVqgkoQWivB3U"
MANAGER_USERNAME = "@nabeghlavi_support"
ADMIN_ID = 8740650587

# ======================
# DATA
# ======================

users = set()
reviews = []

CITIES = [
    "🇬🇪 Тбилиси | თბილისი",
    "🇬🇪 Батуми | ბათუმი",
    "🇬🇪 Рустави | რუსთავი",
    "🇬🇪 Кутаиси | ქუთაისი",
    "🇬🇪 Телави | თელავი",
]

COFFEE_MENU = {
    "c01": {"name": "Meph Crystal SALE 1g(250gel)", "price_ltc": 2, "price_gel": 250},
    "c02": {"name": "☕ Crystal Amber Sale 2gr", "price_ltc": 3, "price_gel": 360},
    "c03": {"name": "☕ Crystal Amber SALE 1g (240gel)", "price_ltc": 1.9, "price_gel": 240},
    "c04": {"name": "☕ Crystal Amber 0.5g(180gel)", "price_ltc": 1.42, "price_gel": 180},
    "c05": {"name": "🥛 Crystal Amber 0.3g(120gel)", "price_ltc": 0.94, "price_gel": 120},
    "c06": {"name": "🥛 Premium powder ALPHA 1g(250gel)", "price_ltc": 1.97, "price_gel": 250},
    "c07": {"name": "🍫 premium powder ALPHA 0.5g(180gel)", "price_ltc": 1.42, "price_gel": 180},
    "c08": {"name": "🧊 Meph Crystal SALE 1g (220gel)", "price_ltc": 1.80, "price_gel": 220},
    "c09": {"name": "🧊 secret 0.3g(150gel)", "price_ltc": 1.25, "price_gel": 150},
    "c10": {"name": "🧊 secret 1g(200gel)", "price_ltc": 1.57, "price_gel": 200},
    "c11": {"name": "🍦 death 1g", "price_ltc": 2, "price_gel": 255},
    "c12": {"name": "🍵 death 0.3g", "price_ltc": 1.42, "price_gel": 170},
    "c13": {"name": "🌰 death 0.5g", "price_ltc": 1.5, "price_gel": 190},
    "c14": {"name": "🌰 прикоп Meph Crystal 1g(165gel)", "price_ltc": 1.30, "price_gel": 165},
    "c15": {"name": "☕ корпус Meph Crystal 1g(165gel)", "price_ltc": 1.30, "price_gel": 165},
    "c16": {"name": "🍵 plani 2g ", "price_ltc": 1.67, "price_gel": 200},
}

# ======================
# INIT
# ======================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ======================
# STATES
# ======================

class OrderStates(StatesGroup):
    city = State()
    coffee = State()
    confirm = State()
    pay = State()

    review_text = State()
    review_stars = State()

# ======================
# KEYBOARDS
# ======================

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☕ Заказать")],
            [KeyboardButton(text="⭐ Reviews")],
            [KeyboardButton(text="📞 Оператор")]
        ],
        resize_keyboard=True
    )

def city_kb():
    rows = []
    for i in range(0, len(CITIES), 2):
        row = [KeyboardButton(text=CITIES[i])]
        if i + 1 < len(CITIES):
            row.append(KeyboardButton(text=CITIES[i + 1]))
        rows.append(row)

    rows.append([KeyboardButton(text="Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def coffee_kb():
    items = list(COFFEE_MENU.values())
    rows = []
    for i in range(0, len(items), 2):
        row = [KeyboardButton(text=items[i]["name"])]
        if i + 1 < len(items):
            row.append(KeyboardButton(text=items[i + 1]["name"]))
        rows.append(row)

    rows.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="ok"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="no")
        ]
    ])

def pay_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я оплатил", callback_data="paid")]
    ])

# ======================
# START
# ======================

@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    users.add(m.from_user.id)
    await m.answer("👋 Добро пожаловать", reply_markup=main_kb())

# ======================
# SEND (FIXED)
# ======================

@dp.message(Command("send"))
async def send_all(m: Message):
    if m.from_user.id != ADMIN_ID:
        return await m.answer("❌ Нет доступа")

    text = m.text.replace("/send", "").strip()
    if not text:
        return await m.answer("❗ /send текст")

    sent = 0
    for u in list(users):
        try:
            await bot.send_message(u, text)
            sent += 1
        except:
            pass

    await m.answer(f"✅ Отправлено: {sent}")

# ======================
# OPERATOR (FIXED)
# ======================

@dp.message(F.text == "📞 Оператор")
async def operator(m: Message):
    await m.answer(f"📞 {MANAGER_USERNAME}")

# ======================
# REVIEWS (FIXED)
# ======================

@dp.message(F.text == "⭐ Reviews")
async def reviews_menu(m: Message):
    if not reviews:
        return await m.answer("😔 Нет отзывов")

    idx = 0
    r = reviews[idx]

    avg = round(sum(x["stars"] for x in reviews) / len(reviews), 2)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"rev_prev_{idx}"),
            InlineKeyboardButton(text="➡️", callback_data=f"rev_next_{idx}")
        ]
    ])

    await m.answer(
        f"⭐ Средняя: {avg}\n\n{'⭐'*r['stars']}\n{r['text']}",
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("rev_"))
async def reviews_nav(c: CallbackQuery):
    await c.answer()

    if not reviews:
        return

    parts = c.data.split("_")
    action = parts[1]
    idx = int(parts[2])

    if action == "next":
        idx = (idx + 1) % len(reviews)
    else:
        idx = (idx - 1) % len(reviews)

    r = reviews[idx]
    avg = round(sum(x["stars"] for x in reviews) / len(reviews), 2)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"rev_prev_{idx}"),
            InlineKeyboardButton(text="➡️", callback_data=f"rev_next_{idx}")
        ]
    ])

    await c.message.edit_text(
        f"⭐ Средняя: {avg}\n\n{'⭐'*r['stars']}\n{r['text']}",
        reply_markup=kb
    )

# ======================
# ORDER FLOW (FIXED SAFE)
# ======================

@dp.message(F.text == "☕ Заказать")
async def order(m: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.city)
    await m.answer("Выбери город", reply_markup=city_kb())

@dp.message(OrderStates.city)
async def city(m: Message, state: FSMContext):
    if m.text == "Главное меню":
        await state.clear()
        return await m.answer("Меню", reply_markup=main_kb())

    if m.text not in CITIES:
        return await m.answer("Выбери город")

    await state.update_data(city=m.text)
    await state.set_state(OrderStates.coffee)
    await m.answer("Выбери товар", reply_markup=coffee_kb())

@dp.message(OrderStates.coffee)
async def coffee(m: Message, state: FSMContext):
    if m.text == "Назад":
        await state.set_state(OrderStates.city)
        return await m.answer("Назад", reply_markup=city_kb())

    for k, v in COFFEE_MENU.items():
        if v["name"] == m.text:
            await state.update_data(coffee=v["name"])
            await state.set_state(OrderStates.confirm)

            data = await state.get_data()

            return await m.answer(
                f"📍 {data.get('city')}\n☕ {v['name']}\n💰 {v['price_ltc']} LTC",
                reply_markup=confirm_kb()
            )

    await m.answer("Выбери товар")

# ======================
# CALLBACKS (FIXED)
# ======================

@dp.callback_query(F.data == "ok")
async def ok(c: CallbackQuery, state: FSMContext):
    await c.answer()

    data = await state.get_data()

    await c.message.answer(
        f"✅ Заказ подтверждён\n\n📍 {data.get('city')}\n☕ {data.get('coffee')}\n\n💳 {LTC_ADDRESS}",
        reply_markup=pay_kb()
    )

    await state.set_state(OrderStates.pay)

@dp.callback_query(F.data == "no")
async def no(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await state.clear()
    await c.message.answer("❌ Отменено", reply_markup=main_kb())

@dp.callback_query(F.data == "paid")
async def paid(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await state.clear()
    await c.message.answer("💰 Оплата получена напишите админу @nabeghlavi_support. для нового заказа пропишите /start")

# ======================
# /51 FIXED (WORKS 100%)
# ======================

@dp.message(F.text == "/51")
async def r_start(m: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderStates.review_text)
    await m.answer("✍️ Напиши отзыв")

@dp.message(OrderStates.review_text)
async def r_text(m: Message, state: FSMContext):
    await state.update_data(text=m.text)
    await state.set_state(OrderStates.review_stars)
    await m.answer("⭐ Оценка 1-5")

@dp.message(OrderStates.review_stars)
async def r_stars(m: Message, state: FSMContext):
    try:
        stars = int(m.text)

        if stars < 1 or stars > 5:
            return await m.answer("❗ 1-5")

        data = await state.get_data()

        reviews.append({
            "text": data["text"],
            "stars": stars
        })

        await state.clear()
        await m.answer("✅ Отзыв добавлен")

    except:
        await m.answer("❗ 1-5")

# ======================
# RUN
# ======================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
