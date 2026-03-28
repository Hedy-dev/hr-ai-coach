import json
from gigachat import GigaChat

class HRAnalyzer:
    def __init__(self, api_key: str):
        self.client = GigaChat(
            credentials=api_key, 
            scope="GIGACHAT_API_PERS", 
            verify_ssl_certs=False
        )

    def analyze(self, question, hr_answers, student_answer):
        # Собираем ответы экспертов
        hr_context = "\n".join([f"ЭКСПЕРТ {i+1}: {a}" for i, a in enumerate(hr_answers)])
        
        # Системный промпт с требованием вернуть строгий JSON
        prompt = f"""Ты — экспертный HR-аналитик. Твоя задача — сравнить ответ Студента с базой ответов HR-директоров.
        
        ВОПРОС: {question}
        
        БАЗА ОТВЕТОВ HR (Контекст):
        {hr_context}
        
        ОТВЕТ СТУДЕНТА:
        {student_answer}
        
        ИНСТРУКЦИЯ ПО ОТВЕТУ:
        Сгенерируй ответ СТРОГО в формате JSON без markdown разметки (без ```json ... ```). Используй следующую структуру:
        {{
            "clusters": [
                {{
                    "name": "Название группы мнений 1",
                    "percentage": "Примерный %",
                    "description": "Краткое описание мнения этой группы"
                }},
                {{
                    "name": "Название группы мнений 2",
                    "percentage": "Примерный %",
                    "description": "Краткое описание мнения этой группы"
                }}
            ],
            "student_match": "К какой группе ближе студент и почему",
            "critique": "Чего конкретно не хватает в ответе студента (с опорой на базу)",
            "gold_standard": "Сформулируй идеальный ответ, объединив лучшие фишки из базы"
        }}
        Никакого дополнительного текста до или после JSON быть не должно.
        """

        try:
            response = self.client.chat(prompt)
            content = response.choices[0].message.content
            
            # Очищаем ответ от случайной Markdown-разметки (если GigaChat все же её добавит)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Парсим JSON в Python словарь
            parsed_data = json.loads(content)
            
            # Возвращаем в нужном для app.py формате
            return {"status": "success", "data": parsed_data}
            
        except json.JSONDecodeError:
            return {
                "status": "error", 
                "message": "Ошибка: Нейросеть нарушила формат и вернула невалидный JSON. Попробуйте нажать кнопку еще раз."
            }
        except Exception as e:
            return {"status": "error", "message": f"Ошибка при обращении к GigaChat: {str(e)}"}
