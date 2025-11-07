import os
import time
from yandex_cloud_ml_sdk import YCloudML
import asyncio


sdk = YCloudML(
        auth=os.getenv('YAGPT_TOKEN'),
    )

print(os.getenv('YAGPT_TOKEN'))

model = sdk.models.completions("yandexgpt")
print(322)
async def get_res(model, question):
    operation = model.configure(temperature=0.5).run_deferred(question)
    print(228)
    result = operation.wait()
    print(2281)
    return result
async def main():
    a = await get_res(model, "какая ты модель?")
    print(2282)
    print(a)

# Запуск
asyncio.run(main())
