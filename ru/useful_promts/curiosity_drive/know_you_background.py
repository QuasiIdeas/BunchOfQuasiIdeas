#!/usr/bin/env pythonw
"""
know_you_background.py
Периодически (через случайные интервалы) запрашивает у OpenAI новый факт
и показывает его во всплывающем окне. Запускать через pythonw.exe, чтобы
не открывалось консольное окно.
"""
import os
import random
import time
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox

# =====  настройки  =====
MODEL_NAME        = "gpt-4o-mini"      # поменяйте на o3, когда будет доступ
TEMPERATURE       = 0.9
MIN_DELAY_MIN     = 30                 # минимум минут между фактами
MAX_DELAY_MIN     = 120                # максимум минут между фактами
SYSTEM_PROMPT = (
    "Ты — увлечённый популяризатор науки и истории. "
    "Каждый раз выдавай ровно один короткий, но захватывающий факт "
    "из истории или науки (1–2 предложения), начиная фразой "
    "«Знаете ли вы, что ...». Избегай повторов; не добавляй ничего лишнего."
)

client = OpenAI()                      # ключ берётся из OPENAI_API_KEY

def fetch_fact() -> str:
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        temperature=TEMPERATURE,
    )
    return resp.choices[0].message.content.strip()

def show_popup(text: str, timeout_ms: int = 10_000):
    root = tk.Tk()
    root.withdraw()
    root.after(timeout_ms, root.destroy)
    messagebox.showinfo("Знаете ли вы, что...", text, parent=root)

def main():
    while True:
        try:
            fact = fetch_fact()
            show_popup(fact)
        except Exception as e:
            # На случай временной сетевой ошибки выводим в консоль-лог
            print("Ошибка получения факта:", e, flush=True)
        # Случайная пауза перед следующим фактом
        delay = random.uniform(MIN_DELAY_MIN, MAX_DELAY_MIN) * 60
        time.sleep(delay)

if __name__ == "__main__":
    main()
