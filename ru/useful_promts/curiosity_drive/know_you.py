#!/usr/bin/env python3
"""
Получает «факт дня» от модели o3 и
показывает всплывающее окно «Знаете ли вы, что...».
Работает с openai-python >=1.0.
"""
import os
from openai import OpenAI           # ← новый стиль импорта
import tkinter as tk
from tkinter import messagebox

MODEL_NAME = "gpt-4o-mini"              # укажите точное название модели
TEMPERATURE = 0.9

SYSTEM_PROMPT = (
    "Ты — увлечённый популяризатор науки и истории. "
    "Каждый раз выдавай ровно один короткий, но захватывающий факт "
    "из истории или науки (1–2 предложения), начиная фразой "
    "«Знаете ли вы, что ...». Избегай повторов; не добавляй ничего лишнего."
)

# Создаём клиент. Ключ берётся из переменной окружения OPENAI_API_KEY
client = OpenAI()

def fetch_fact() -> str:
    """Запрашивает у модели новый факт."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()

def show_popup(text: str, timeout_ms: int = 10_000) -> None:
    """Показывает текст во всплывающем окне и закрывает его через timeout_ms."""
    root = tk.Tk()
    root.withdraw()
    root.after(timeout_ms, root.destroy)
    messagebox.showinfo("Знаете ли вы, что...", text, parent=root)

if __name__ == "__main__":
    try:
        fact = fetch_fact()
        show_popup(fact)
    except Exception as exc:
        print(f"Ошибка: {exc}")
