from gigachat import GigaChat

class HRAnalyzer:
    def __init__(self, api_key: str):
        self.client = GigaChat(
            credentials=api_key, 
            scope="GIGACHAT_API_PERS", 
            verify_ssl_certs=False
        )

    def analyze(self, question, hr_answers, student_answer):
        # Собираем ответы экспертов в один блок текста
        hr_context = "\n".join([f"ЭКСПЕРТ {i+1}: {a}" for i, a in enumerate(hr_answers)])
        
        # Системный промпт для жесткой структуры
        prompt = f"""Ты — экспертный HR-аналитик. Твоя задача — сравнить ответ Студента с базой ответов HR-директоров.
        
        ВОПРОС: {question}
        
        БАЗА ОТВЕТОВ HR (Контекст):
        {hr_context}
        
        ОТВЕТ СТУДЕНТА:
        {student_answer}
        
        ИНСТРУКЦИЯ ПО ОТВЕТУ:
        1. **Кластеризация мнений**: Раздели ответы HR на 2-3 группы (например: "Сторонники краткости" и "Любители подробностей"). 
        2. **Статистика**: Укажи, к какой группе ближе студент и какой % экспертов думают так же.
        3. **Критика**: Чего конкретно не хватает в ответе студента (с опорой на базу).
        4. **Золотой стандарт**: Сформулируй идеальный ответ, объединив лучшие фишки из базы.
        
        Используй Markdown для оформления (заголовки, жирный текст)."""

        try:
            # Настройки модели для стабильности
            response = self.client.chat(prompt)
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка при обращении к GigaChat: {str(e)}"