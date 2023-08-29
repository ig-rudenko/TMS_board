import openai


class Translator:
    system_settings = (
        "Ты переводчик на разные языки, отвечаешь только переводом, без лишних слов."
    )

    def __init__(self, text: str):
        self._text = text

    def to_eng(self) -> str:
        return self._translate(self._text, "английский")

    def _translate(self, message: str, language: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self.system_settings,
            },
            {
                "role": "user",
                "content": f"Переведи данный текст на {language}:\n{message}",
            },
        ]

        # Делаем запрос и получаем результат
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )

        print(response)
        # Ответ от ChatGPT
        chat_gpt_answer: str = response["choices"][-1]["message"]["content"]

        # Возвращаем текст ответа
        return chat_gpt_answer
