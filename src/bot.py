import asyncio
import logging
import os
import httpx
import re
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
import typing as tp
from datetime import datetime, timezone
from src.bot_utils import parse_expense_message, create_transaction_table, handle_api_errors

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    # Добавлена проверка, чтобы бот не падал при запуске без токена
    raise ValueError("Необходимо установить переменную окружения BOT_TOKEN")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Вспомогательные функции и классы ---

class ParseError(ValueError):
    """Наш собственный класс исключения, чтобы ловить только ошибки парсинга."""
    pass

@dp.message(CommandStart())
async def handle_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я бот для учета твоих расходов. Отправь мне сообщение в формате:\n\n"
        f"`СУММА Описание [ДАТА в формате ДД.ММ]`\n\n"
        f"Примеры:\n`500 Такси`\n`1.5к Продукты 2025-10-18`",
        parse_mode="Markdown"
    )


@dp.message(Command("history"))
@handle_api_errors
async def lookup_transactions(message: types.Message, command: CommandObject):
    if command.args is None:
        limit = 10
    else:
        limit = int(command.args)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/transactions?limit={limit}"
        )
    response.raise_for_status()
    print(response.json())
    transaction_table = create_transaction_table(response.json())
    await message.answer(transaction_table, parse_mode="HTML")


@dp.message(Command("remove"))
@handle_api_errors
async def remove_transactions(message: types.Message, command: CommandObject):
    if command.args is None:
        raise ParseError("Не были переданы транзакции для удаления")
    else:
        try:
            ids_to_delete = [int(el) for el in command.args.split()]
        except Exception as e:
            raise ParseError("ID переданы в неверном формате")
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_URL}/transactions?ids_to_delete={ids_to_delete}"
        )
    response.raise_for_status()

    await message.answer("Транзакции удалены")


@dp.message(F.text)
@handle_api_errors
async def handle_expense_message(message: Message):
    # u_login = message.from_user.username
    try:
        text = message.text
        parsed_data = parse_expense_message(text)
    except ParseError as e:
        await message.answer(f"Ошибка в формате сообщения:\n{e}")
        return

    transaction_dttm = parsed_data.get('transaction_dttm') or datetime.now(timezone.utc)
    transaction_to_create = {
        "amount": parsed_data["amount"],
        "description": parsed_data["description"],
        "category": None,
        "raw_text": text,
        "transaction_type": parsed_data["transaction_type"],
        "transaction_dttm": transaction_dttm.isoformat()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/transaction", 
            json=transaction_to_create
        )
        # Проверяем, что API ответил успешно (коды 2xx)
        response.raise_for_status()

    await message.answer("Расход записан!")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
