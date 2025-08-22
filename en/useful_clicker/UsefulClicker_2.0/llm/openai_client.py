# llm/openai_client.py
import os
from openai import OpenAI

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str) -> str:
        # GPT-5 Thinking по вашей установке; при необходимости поменяй на доступную модель
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    def generate_list(self, prompt: str, separator: str = "\n"):
        text = self.generate_text(prompt)
        # Разрезаем по переданному сепаратору (ожидаем \n)
        items = [s.strip() for s in text.split(separator) if s.strip()]
        return items
