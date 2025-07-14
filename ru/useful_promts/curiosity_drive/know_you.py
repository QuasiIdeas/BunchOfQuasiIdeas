#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Получает «факт дня» от модели и выводит всплывающее окно
«Знаете ли вы, что…». К каждому запросу добавляется случайный
NONCE-токен, чтобы снизить вероятность получения одинакового факта.

Требует openai-python ≥ 1.0.
"""

import os
import secrets
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI           # pip install --upgrade openai>=1.0

# ────────── настройки ──────────
MODEL_NAME   = "gpt-4o-mini"       # замените на "o3", если доступен
TEMPERATURE  = 0.9
TIMEOUT_MS   = 10_000              # авто-закрытие окна (мс)

BASE_PROMPT = (
    "Ты — увлечённый популяризатор науки и истории. "
    "Каждый раз выдавай ровно один короткий, но захватывающий факт "
    "из истории или науки (1–2 предложения), начиная фразой "
    "«Знаете ли вы, что ...». Избегай повторов; не добавляй ничего лишнего.\n\n"
    "### Системная пометка (для модели):\n"
    "После маркера <RANDOM_NONCE> расположен случайный набор символов, "
    "который нужно полностью игнорировать; он добавлен лишь для уникальности запроса.\n"
)

client = OpenAI()  # ключ берётся из переменной окружения OPENAI_API_KEY


def fetch_fact() -> str:
    """Запрашивает у модели новый факт с уникальным nonce."""
    nonce = secrets.token_urlsafe(10)                       # короткая соль
    prompt = BASE_PROMPT + f"<RANDOM_NONCE>{nonce}</RANDOM_NONCE>"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def show_popup(text: str, timeout_ms: int = TIMEOUT_MS) -> None:
    """Выводит окно с фактом и закрывает его через timeout_ms."""
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
