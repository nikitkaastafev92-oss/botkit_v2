import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

# Загрузка конфига
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

BOT_TOKEN = config['bot_token']
PRODUCTS = config['products']

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    builder = InlineKeyboardBuilder()
    for key, prod in PRODUCTS.items():
        builder.button(text=prod['name'], callback_data=f"buy_{key}")
    builder.adjust(1)
    await message.answer("🛒 Выберите товар:", reply_markup=builder.as_markup())

# Обработка выбора товара
@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def process_product(callback: types.CallbackQuery):
    product_id = callback.data[4:]
    if product_id not in PRODUCTS:
        await callback.answer("Товар не найден.")
        return

    prod = PRODUCTS[product_id]
    text = f"📄 <b>{prod['name']}</b>\n\n{prod['description']}\n\n💰 Цена: {prod['price']} ₽"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить (СБП)", callback_data=f"pay_{product_id}")
    builder.button(text="⬅ Назад", callback_data="back")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# Обработка оплаты (заглушка — в реальности интеграция с СБП)
@dp.callback_query(lambda c: c.data.startswith("pay_"))
async def process_payment(callback: types.CallbackQuery):
    product_id = callback.data[4:]
    prod = PRODUCTS[product_id]

    # Имитация "успешной оплаты"
    await callback.answer("✅ Оплата принята! Готовим ваш товар...")

    if prod['type'] == 'file':
        file_path = prod['content']
        if os.path.exists(file_path):
            await callback.message.answer_document(types.FSInputFile(file_path))
        else:
            await callback.message.answer("❌ Файл не найден на сервере.")
    elif prod['type'] == 'link':
        await callback.message.answer(f"🔗 Ваша ссылка:\n{prod['content']}")

# Назад в меню
@dp.callback_query(lambda c: c.data == "back")
async def go_back(callback: types.CallbackQuery):
    await send_welcome(callback.message)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())