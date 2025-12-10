# bot_main.py
import os
import logging
import asyncio
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from chainalysis_client import chainalysis_check

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", None)

if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN in environment or .env file")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def looks_like_address(addr: str):
    a = addr.strip()
    if a.startswith("0x") and len(a) == 42:
        return "ETH"
    if len(a) >= 26 and len(a) <= 35:
        return "BTC"
    return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Используй /check <адрес> чтобы проверить адрес на санкции (Chainalysis).")

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Нужно: /check <адрес>")
        return
    address = args[1].strip()
    coin = looks_like_address(address)
    if not coin:
        await message.answer("Не похоже на ETH/BTC адрес. Проверьте формат.")
        return

    await message.answer("Выполняю быстрый санкционный чек (Chainalysis)...")
    res = chainalysis_check(address)
    if res.get("error"):
        await message.answer(f"Ошибка при обращении к Chainalysis: {res['error']}")
        return

    # пример обработки ответа (адаптируйте под реальную структуру)
    if res.get("sanctioned") is True:
        await message.answer(f"⚠️ Адрес {address} найден в санкционных/черных списках. Риск: HIGH.")
    else:
        await message.answer(f"✅ Адрес {address} не найден в санкционных списках (быстрая проверка).")

    # предложение платной глубокой проверки (инвойс через Stars)
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Купить глубокую проверку (Stars)", callback_data=f"buy_deep|{address}")
    )
    await message.answer("Хотите глубокий отчёт?", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data and c.data.startswith("buy_deep"))
async def buy_deep(callback: types.CallbackQuery):
    _, address = callback.data.split("|", 1)
    title = "Глубокая AML проверка"
    description = f"Глубокий отчёт по адресу {address}"
    payload = f"deep_check:{address}"
    prices = [types.LabeledPrice(label="Deep AML report", amount=100)]  # 100 XTR (пример)
    await bot.send_invoice(callback.from_user.id, title=title, description=description,
                           payload=payload, provider_token=PROVIDER_TOKEN,
                           currency="XTR", prices=prices)
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(types.MessageSuccessfulPayment)
async def got_payment(message: types.Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("deep_check:"):
        address = payload.split(":", 1)[1]
        await message.answer("Платёж получен — запускаю глубокую проверку...")
        deep_res = chainalysis_check(address)  # на практике: отдельный платный эндпойнт
        await message.answer(f"Результат глубокого отчёта:\n`{deep_res}`")
    else:
        await message.answer("Платёж получен.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

