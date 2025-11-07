import os
from enum import Enum as PyEnum
from yandex_cloud_ml_sdk import YCloudML

class LlmModel:
    MODEL_MAP = {
        'yandexgpt': 'yandexgpt',
        'yandexgpt-lite': 'yandexgpt-lite',
         'gpt-oss': 'gpt-oss-120b/latest'
    }

    def __init__(self, model_type, temperature=0.5):
        self.folder_id = os.getenv("FOLDER_ID")
        self.sdk = YCloudML(
        folder_id=self.folder_id,
        auth=os.getenv('YAGPT_TOKEN'),
        )
        
        self.temperature = temperature
        if model_type not in self.MODEL_MAP:
            raise ValueError("некорректная модель")
        model_dir = "gpt://" + self.folder_id + "/" + self.MODEL_MAP[model_type]
        self.model = self.sdk.models.completions(model_dir)

    async def get_answer(self, question):
        operation = self.model.configure(temperature=self.temperature).run_deferred(question)
        result = await operation.wait()
        return result
