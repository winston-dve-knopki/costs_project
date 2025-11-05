import re
import typing as tp
from datetime import datetime
from prettytable import PrettyTable
from datetime import date
import functools
import httpx
from aiogram.types import Message
import logging

logging.basicConfig(level=logging.INFO)

MONTHS = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
        'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }


def handle_api_errors(func):
    """
    Декоратор для обработки стандартных ошибок при работе с API.
    Ловит ошибки подключения и HTTP-статусов, отправляя пользователю сообщение.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        message: Message = kwargs.get('message')
        if not message:
            for arg in args:
                if isinstance(arg, Message):
                    message = arg
                    break
        
        if not message:
            logging.error("Декоратор handle_api_errors не смог найти объект Message.")
            return await func(*args, **kwargs)

        try:
            return await func(*args, **kwargs)
        
        except httpx.HTTPStatusError as e:
            error_details = e.response.json().get("detail", e.response.text)
            await message.answer(f"❌ Ошибка при обращении к серверу!\nОтвет: {error_details}")
            logging.error(f"API Error: {e.response.status_code} - {error_details}")
        
        except httpx.RequestError as e:
            await message.answer("❌ Не могу связаться с сервером. Пожалуйста, попробуйте позже.")
            logging.error(f"Request Error: {e}")

    return wrapper


def parse_expense_message(text: str) -> tp.Dict[str, tp.Any]:
    """
    Парсит сообщение о расходе.
    В случае ошибки, выбрасывает исключение ParseError.
    Возвращает: {'amount': int, 'description': str, 'transaction_dttm': datetime | None}
    """
    #  структура всегда цена - описание - возможно дата
    price_pattern = re.compile(r'\b([+\-])?(\d+\.?\d*)\s*([кk])?\b', re.IGNORECASE)
    match = price_pattern.search(text)
    if not match:
        raise ValueError("No price was given")

    sign, number_str, suffix_k = match.groups()
    transaction_type = 'income' if sign == '+' else 'expense'
    price = int(number_str)
    if suffix_k:
        price *= 1000
    
    remaining_string = re.sub(price_pattern, '', text, count=1)
    text = re.sub(r'\s+', ' ', remaining_string).strip()

    months_pattern_part = '|'.join(MONTHS.keys())

    date_pattern = re.compile(
        r'\b(\d{1,2})(?:\s+(' + months_pattern_part + r')|\.(\d{1,2}))\b',
        re.IGNORECASE
    )
    
    match = date_pattern.search(text)
    if match:
        day_str, month_name, month_num_str = match.groups()
        
        day = int(day_str)
        month = 0
    
        if month_name:
            month = MONTHS[month_name.lower()]
        elif month_num_str:
            month = int(month_num_str)
            
        if month:
            year = datetime.now().year
            try:
                date = datetime(year, month, day).date()
            except ValueError:
                raise ValueError("Ты пытался указать дату, но формат невалидный")
        else:
            date = None
    else:
        date = None

    remaining_string = re.sub(date_pattern, '', text, count=1)
    text = re.sub(r'\s+', ' ', remaining_string).strip()

    description = text

    return {
        'amount': price,
        'description': description,
        'transaction_dttm': date,
        'transaction_type': transaction_type
    }

def create_transaction_table(transactions):
    if not transactions:
        return "У вас пока нет ни одной записи."
    table = PrettyTable()
    print(transactions)
    table.field_names = ["ID", "Тип", "Сумма", "Описание", "Дата"]

    table.align["Сумма"] = "r"
    table.align["Описание"] = "l"

    for tr in transactions:
        type_emoji = "🔴" if tr['transaction_type'] == 'expense' else "🟢"

        formatted_date = tr['transaction_dttm'].strftime('%d.%m.%Y') if tr.get('date') else "---"
        formatted_amount = f"{int(tr['amount'])}"
        
        table.add_row([
            tr['transaction_id'],
            type_emoji,
            formatted_amount,
            tr['description'],
            formatted_date
        ])

    return f"<code>{table.get_string()}</code>"
