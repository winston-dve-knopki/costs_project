import asyncio
import logging
import os
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import typing as tp
from datetime import datetime, timezone


BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    # Добавлена проверка, чтобы бот не падал при запуске без токена
    raise ValueError("Необходимо установить переменную окружения BOT_TOKEN")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --- Вспомогательные функции и классы ---

class ParseError(ValueError):
    """Наш собственный класс исключения, чтобы ловить только ошибки парсинга."""
    pass

def parse_expense_message(text: str) -> tp.Dict[str, tp.Any]:
    """
    Парсит сообщение о расходе.
    В случае ошибки, выбрасывает исключение ParseError.
    Возвращает: {'amount': int, 'description': str, 'transaction_dttm': datetime | None}
    """
    parts = text.strip().split()
    if len(parts) > 3 or len(parts) < 2:
        raise ParseError(f"Ожидалось 2 или 3 слова, а вы прислали {len(parts)}.")

    amount_str = parts[0]
    try:
        if amount_str.lower().endswith('к'):
            amount = float(amount_str[:-1].replace(',', '.')) * 1000
        else:
            amount = float(amount_str.replace(',', '.'))
    except ValueError:
        raise ParseError(f"Не удалось распознать сумму '{amount_str}'. Ожидалось число (например, 500) или число с 'к' (например, 1.5к).")

    description = parts[1]

    transaction_date = None
    if len(parts) == 3:
        try:
            transaction_date = datetime.strptime(parts[2], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except ValueError:
            raise ParseError(f"Неверный формат даты '{parts[2]}'. Ожидался формат ГГГГ-ММ-ДД.")
    
    return {
        'amount': int(amount),
        'description': description,
        'transaction_dttm': transaction_date
    }


@dp.message(CommandStart())
async def handle_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Я бот для учета твоих расходов. Отправь мне сообщение в формате:\n\n"
        f"`СУММА Описание [ДАТА в формате ГГГГ-ММ-ДД]`\n\n"
        f"Примеры:\n`500 Такси`\n`1.5к Продукты 2025-10-18`",
        parse_mode="Markdown"
    )


@dp.message(F.text)
async def handle_expense_message(message: Message):
    # u_login = message.from_user.username
    try:
        text = message.text
        parsed_data = parse_expense_message(text)
    except ParseError as e:
        await message.answer(f"😕 Ошибка в формате сообщения:\n{e}")
        return


    transaction_dttm = parsed_data.get('transaction_dttm') or datetime.now(timezone.utc)


    transaction_to_create = {
        "amount": parsed_data["amount"],
        "description": parsed_data["description"],
        "category": None,
        "raw_text": text,
        "transaction_dttm": transaction_dttm.isoformat()
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/transaction", 
                json=transaction_to_create
            )
            # Проверяем, что API ответил успешно (коды 2xx)
            response.raise_for_status()

    except httpx.HTTPStatusError as e:
        # Если API вернул ошибку (4xx, 5xx)
        error_details = e.response.json().get("detail", e.response.text)
        await message.answer(f"❌ Ошибка при сохранении!\nСервер ответил: {error_details}")
        logging.error(f"API Error: {e.response.status_code} - {error_details}")
        return

    except httpx.RequestError as e:
        # Если не удалось подключиться к API
        await message.answer("❌ Не могу связаться с сервером. Попробуйте позже.")
        logging.error(f"Request Error: {e}")
        return

    await message.answer("✅ Расход записан!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
