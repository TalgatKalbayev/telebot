import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, date
import json
import os

TOKEN = "8608217511:AAHRLD_ouyiZVdjbHB5ZtZMQT5HcAS5PyNI"
CHAT_ID = 752586577
START_DATE = date(2026, 4, 4)
START_AMOUNT = 940
STEP = 10
REMIND_TIME = "16:40"
DATA_FILE = "data.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# 📊 Загрузка данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"debt": 0}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


# 💾 Сохранение данных
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# 💰 Расчет суммы дня
def calculate_amount():
    today = date.today()
    days = (today - START_DATE).days
    return START_AMOUNT + days * STEP


# 📩 Клавиатура
def get_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатил", callback_data="paid")],
        [InlineKeyboardButton(text="❌ Не оплатил", callback_data="not_paid")]
    ])
    return kb


# 🔁 Обработка кнопок
@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    data = load_data()
    amount = calculate_amount()

    if callback.data == "paid":
        data["debt"] -= amount
        text = f"✅ Принято! Долг теперь: {data['debt']} тг"
    elif callback.data == "not_paid":
        data["debt"] += amount
        text = f"❌ Добавлено в долг. Долг теперь: {data['debt']} тг"
    else:
        return

    save_data(data)
    await callback.message.answer(text)
    await callback.answer()


# ⏰ Напоминание (отправляет ровно один раз в день)
async def reminder():
    sent_today = None
    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        if now.strftime("%H:%M") == REMIND_TIME and sent_today != today_str:
            amount = calculate_amount()
            data = load_data()
            text = (
                f"💰 Сегодня нужно внести: {amount} тг\n"
                f"📊 Текущий долг: {data['debt']} тг\n\n"
                f"Ты оплатил?"
            )
            await bot.send_message(
                chat_id=CHAT_ID,
                text=text,
                reply_markup=get_keyboard()
            )
            sent_today = today_str
            await asyncio.sleep(60)

        await asyncio.sleep(1)


async def main():
    asyncio.create_task(reminder())
    await dp.start_polling(bot)


asyncio.run(main())
