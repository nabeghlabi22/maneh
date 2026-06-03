import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


# ======================
# CONFIG
# ======================

BOT_TOKEN = "8962279231:AAGUy_bZxxiXTAx6vsx-cMEv1hT0FBbtWLw"
LTC_ADDRESS = "LQ6VgSJo2CA2fPCJQosCBQVqgkoQWivB3U"
MANAGER_USERNAME = "@nabeghlavi_support"


# ======================
# DATA
# ======================

CITIES = [
    "🇬🇪 Тбилиси | თბილისი",
    "🇬🇪 Батуми | ბათუმი",
    "🇬🇪 Рустави | რუსთავი",
    "🇬🇪 Кутаиси | ქუთაისი",
    "🇬🇪 Гори | გორი",
    "🇬🇪 Зестафони | ზესტაფონი",
    "🇬🇪 Каспи | კასპი",
    "🇬🇪 Марнеули | მარნეული",
    "🇬🇪 Поти | ფოთი",
    "🇬🇪 Кобулети | ქობულეთი",
    "🇬🇪 Самтредиа | სამტრედია",
    "🇬🇪 Ланчхути | ლანჩხუთი",
    "🇬🇪 Зугдиди | ზუგდიდი",
    "🇬🇪 Боржоми | ბორჯომი",
    "🇬🇪 Сенаки | სენაკი",
    "🇬🇪 Телави | თელავი",
    "🇬🇪 Озургети | ოზურგети",
    "🇬🇪 Чакви | ჩაქვი",
]


COFFEE_MENU = {
    "c01": {"name": "Meph Crystal SALE 1g(165gel)", "price_ltc": 1.30, "price_gel": 165},
    "c02": {"name": "☕ Crystal Amber Sale 2gr", "price_ltc": 2.30, "price_gel": 300},
    "c03": {"name": "☕ Crystal Amber SALE 1g (240gel)", "price_ltc": 1.9, "price_gel": 240},
    "c04": {"name": "☕ Crystal Amber 0.5g(180gel)", "price_ltc": 1.42, "price_gel": 180},
    "c05": {"name": "🥛 Crystal Amber 0.3g(120gel)", "price_ltc": 0.94, "price_gel": 120},
    "c06": {"name": "🥛 Premium powder ALPHA 1g(250gel)", "price_ltc": 1.97, "price_gel": 250},
    "c07": {"name": "🍫 premium powder ALPHA 0.5g(180gel)", "price_ltc": 1.42, "price_gel": 180},
    "c08": {"name": "🧊 Meph Crystal SALE 1g (165gel)", "price_ltc": 1.30, "price_gel": 165},
    "c09": {"name": "🧊 secret 0.3g(129gel)", "price_ltc": 1.02, "price_gel": 129},
    "c10": {"name": "🧊 secret 1g(200gel)", "price_ltc": 1.57, "price_gel": 200},
    "c11": {"name": "🍦 death 1g", "price_ltc": 2, "price_gel": 255},
    "c12": {"name": "🍵 death 0.3g", "price_ltc": 1, "price_gel": 130},
    "c13": {"name": "🌰 death 0.5g", "price_ltc": 1.5, "price_gel": 190},
    "c14": {"name": "🌰 прикоп Meph Crystal 1g(165gel)", "price_ltc": 1.30, "price_gel": 165},
    "c15": {"name": "☕ корпус Meph Crystal 1g(165gel)", "price_ltc": 1.30, "price_gel": 165},
    "c16": {"name": "🍵 plani 2g ", "price_ltc": 1.2, "price_gel": 150},
}


# ======================
# BOT INIT
# ======================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class OrderStates(StatesGroup):
    city = State()
    coffee = State()
    confirm = State()
    pay = State()


# ======================
# KEYBOARDS
# ======================

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☕ Заказать")],
            [KeyboardButton(text="📋 Меню")],
            [KeyboardButton(text="📞 Оператор")],
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
            InlineKeyboardButton(text="❌ Отмена", callback_data="no"),
        ]
    ])


def pay_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я оплатил", callback_data="paid")],
        [InlineKeyboardButton(text="Отмена", callback_data="no")]
    ])


# ======================
# HELPERS
# ======================

def get_city(text: str):
    for c in CITIES:
        if c == text:
            return c
    return None


def get_coffee(text: str):
    for k, v in COFFEE_MENU.items():
        if v["name"] == text:
            return k, v
    return None, None


# ======================
# HANDLERS
# ======================

@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("👋 Добро пожаловать ☕", reply_markup=main_kb())


@dp.message(F.text == "☕ Заказать")
async def order(m: Message, state: FSMContext):
    await state.set_state(OrderStates.city)
    await m.answer("Выбери город", reply_markup=city_kb())


@dp.message(OrderStates.city)
async def city(m: Message, state: FSMContext):

    if m.text == "Главное меню":
        await state.clear()
        await m.answer("Главное меню", reply_markup=main_kb())
        return

    city = get_city(m.text)
    if not city:
        await m.answer("Выбери город из списка")
        return

    await state.update_data(city=city)
    await state.set_state(OrderStates.coffee)
    await m.answer("Выбери кофе", reply_markup=coffee_kb())


@dp.message(OrderStates.coffee)
async def coffee(m: Message, state: FSMContext):

    if m.text == "Назад":
        await state.set_state(OrderStates.city)
        await m.answer("Назад к городам", reply_markup=city_kb())
        return

    key, item = get_coffee(m.text)
    if not item:
        await m.answer("Выбери кофе из списка")
        return

    await state.update_data(coffee=key)
    data = await state.get_data()
    await state.set_state(OrderStates.confirm)

    await m.answer(
        f"📦 Заказ:\n"
        f"{data['city']}\n"
        f"{item['name']}\n"
        f"{item['price_ltc']} LTC",
        reply_markup=confirm_kb()
    )


@dp.callback_query(F.data == "ok")
async def confirm(c: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    item = COFFEE_MENU[data["coffee"]]

    await state.set_state(OrderStates.pay)

    await c.message.edit_text(
        f"💳 Оплата:\n\n"
        f"{item['price_ltc']} LTC\n\n"
        f"{LTC_ADDRESS}",
        reply_markup=pay_kb()
    )


@dp.callback_query(F.data == "paid")
async def paid(c: CallbackQuery, state: FSMContext):

    await state.clear()

    await c.message.edit_text(
        f"✅ Оплата подтверждена!\n\n"
        f"📦 Свяжитесь с менеджером:\n"
        f"{MANAGER_USERNAME} за товаром"
    )


@dp.callback_query(F.data == "no")
async def cancel(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("❌ Отменено")


# ======================
# RUN
# ======================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())