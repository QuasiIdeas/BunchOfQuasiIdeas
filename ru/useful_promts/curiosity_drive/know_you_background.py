#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
know_you_background.py  —  фоновый «факт-бот»

• Периодически (случайный интервал) запрашивает новый факт у OpenAI
  и показывает окно «Знаете ли вы, что...».
• К каждому запросу добавляется случайный NONCE, чтобы модель генерировала
  действительно новый факт даже при одинаковом контексте.
"""

import os
import random
import secrets
import time
import tkinter as tk
from tkinter import messagebox

from openai import OpenAI         # pip install --upgrade openai>=1.0


# ────────── настройки ──────────
MODEL_NAME      = "gpt-4o-mini"   # замените на "o3", если доступен
TEMPERATURE     = 0.9
MIN_DELAY_MIN   = 0              # минимум минут между фактами
MAX_DELAY_MIN   = 10              # максимум минут между фактами

BASE_PROMPT = (
    "Ты — увлечённый популяризатор науки и истории. "
    "Каждый раз выдавай ровно один короткий, но захватывающий факт "
    "из истории или науки (1–2 предложения), начиная фразой "
    "«Знаете ли вы, что ...». Избегай повторов; не добавляй ничего лишнего.\n\n"
    "### Системная пометка (для модели):\n"
    "После маркера <RANDOM_NONCE> расположен случайный набор символов, "
    "который НУЖНО ПОЛНОСТЬЮ ИГНОРИРОВАТЬ; он вводится лишь для того, "
    "чтобы каждый запрос имел уникальный токен.\n"
)

client = OpenAI()  # ключ берётся из переменной окружения OPENAI_API_KEY


# ────────── функции ──────────
def fetch_fact() -> str:
    """Запрашивает новый факт, добавляя случайный nonce к промпту."""
    nonce = secrets.token_urlsafe(10)  # короткая крипто-соль
    prompt = BASE_PROMPT + f"<RANDOM_NONCE>{nonce}</RANDOM_NONCE>"

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        temperature=TEMPERATURE,
    )
    return resp.choices[0].message.content.strip()


def show_popup(text: str) -> None:
    """Показывает окно и ждёт, пока пользователь не нажмёт OK."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Знаете ли вы, что...", text, parent=root)
    root.destroy()


def main() -> None:
    while True:
        try:
            fact = fetch_fact()
            show_popup(fact)
        except Exception as exc:
            # при желании пишите в файл-лог, а не в несуществующую консоль
            print(f"[fact-bot] Ошибка: {exc}", flush=True)

        delay_sec = random.uniform(MIN_DELAY_MIN, MAX_DELAY_MIN) * 60
        time.sleep(delay_sec)


# ────────── точка входа ──────────
if __name__ == "__main__":
    main()
