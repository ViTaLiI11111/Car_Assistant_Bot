import google.generativeai as genai
import logging
import json
from PIL import Image
import io

from config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

MODEL_NAME = 'gemini-2.5-pro'

genai.configure(api_key=GOOGLE_API_KEY)

PROMPT = """
Ти — досвідчений експерт з оцінки ремонту автомобілів. Твоє завдання — проаналізувати зображення пошкодженого автомобіля та надати попередню оцінку вартості ремонту в українських гривнях (UAH).

Проаналізуй такі аспекти:
1.  Визнач видимі пошкодження (наприклад, вм'ятина на дверях, розбитий бампер, подряпини).
2.  Оціни складність ремонту (легкий, середній, важкий).
3.  Надай орієнтовну вартість ремонту.
4.  Обов'язково без винятків намагайся проаналізувати модель та марку авто але якщо не можливо виявити то пиши що неможливо дізнатись марку авто.

ВАЖЛИВО: Твоя відповідь має бути у форматі JSON. Не додавай жодного іншого тексту, лише JSON.
Формат JSON:
{
  "estimated_cost_min": int,
  "estimated_cost_max": int,
  "damage_description": "Тут короткий опис пошкоджень, які ти бачиш",
  "car_brand": "Напишеш тут модель та марку авто"
  "currency": "UAH",
  "model": "Тут назва твоєї моделі нейронної мережі"
}

Якщо на зображенні не автомобіль або пошкодження не видно, поверни:
{
  "error": "Не вдалося визначити пошкодження на фото."
}
"""


def analyze_car_damage(image_bytes: bytes) -> dict | None:
    """
    :param image_bytes: Зображення у вигляді байтів.
    :return: Словник з результатом аналізу або None у разі помилки.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)

        image = Image.open(io.BytesIO(image_bytes))

        response = model.generate_content([PROMPT, image])

        clean_response = response.text.strip().replace("```json", "").replace("```", "")

        result = json.loads(clean_response)

        if "error" not in result:
            result['model_used'] = MODEL_NAME


        return result

    except json.JSONDecodeError:
        logger.error(f"Помилка декодування JSON від API. Відповідь: {response.text}")
        return {"error": "Модель повернула некоректний формат даних."}
    except Exception as e:

        logger.error(f"Помилка під час аналізу зображення в API Google: {e}")

        return {"error": "Не вдалося зв'язатися з сервісом аналізу зображень."}