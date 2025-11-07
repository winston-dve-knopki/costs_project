import asyncio
from src.llm_classificator.model import LlmModel
from src.api.api import read_transactions
from src.bot_utils import create_transaction_table
import os
import logging

logging.basicConfig(level=logging.INFO)

classification_prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'classification_prompt.txt')

async def get_examples():
    result_lst = await read_transactions(limit=1000)
    category_list = set([el['category'] for el in result_lst])
    transaction_table = create_transaction_table(result_lst[:100])
    return transaction_table, category_list

def formulate_prompt(transaction, examples, category_list):
    with open(classification_prompt_path, 'r') as f:
        result = f.read()
    prompt = result.format(examples=examples, category_list=category_list, transaction=transaction)
    return prompt

async def classify_cost(transaction):
    examples, category_list = await get_examples()
    model = LlmModel(model_type='yandexgpt-lite')
    prompt = await formulate_prompt(transaction, examples, category_list)
    try:
        result = await model.get_answer(prompt).strip().lower()
        if result not in category_list:
            return None
        else:
            return result
    except Exception as e:
        logging.error(f"{e}", exc_info=True)

async def main():
    transaction = {
        "amount": 500,
        "description": 'бенза',
        "raw_text": '500 бенза',
        "transaction_type": 'expense'
    }

    result = await classify_cost(transaction)
    print(result)

asyncio.run(main())
