#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
know_you_background.py
──────────────────────
Фоновый «факт-бот» со статистикой «знаю / не знаю» и меткой IGNORED.

• Каждые 0–5 мин запрашивает у OpenAI факт и показывает окно.
• Кнопки:
      ▸ «Знаю»        → факт учитывается как KNOWN
      ▸ «Теперь знаю» → факт учитывается как NEW
  Если за 20 сек пользователь ничего не нажал (или закрыл окно) — факт
  помечается IGNORED и не попадает в статистику.
• Лог `fact_bot.log` — строки `KNOWN | NEW | IGNORED` и актуальный ratio.
• Статистика хранится в `fact_stats.json` (ключи total/known).
"""
from __future__ import annotations

import json
import logging
import random
import secrets
import time
from pathlib import Path
from typing import Final

import tkinter as tk
from openai import OpenAI          # pip install --upgrade openai>=1.0

# ────────── базовые настройки ──────────
MODEL_NAME:     Final[str] = "gpt-4o-mini"
TEMPERATURE:    Final[float] = 0.9
MIN_DELAY_MIN:  Final[int]   = 0
MAX_DELAY_MIN:  Final[int]   = 1
TIMEOUT_MS:     Final[int]   = 20_000         # 20 с

TOPIC_POOL: Final[list[str]] = [
    # — естественные науки —
    "астрономия", "космология", "планетология", "квантовая механика",
    "физика частиц", "оптика", "акустика", "термодинамика", "материаловедение",
    "органическая химия", "неорганическая химия", "биохимия", "генетика",
    "микробиология", "иммунология", "неврология", "биология растений",
    "зоология", "экология", "этология", "эволюционная биология", "палеонтология",
    "медицина", "кардиология", "фармакология", "психология", "психиатрия",
    "климатология", "метеорология", "океанология", "геология", "сейсмология",
    "вулканология", "минералогия",
    # — математика и логика —
    "математический анализ", "алгебра", "топология", "теория чисел",
    "статистика", "теория вероятностей", "криптография", "логика",
    "теория игр", "комбинаторика", "фракталы", "вычислительная математика",
    # — инженерия и технологии —
    "робототехника", "искусственный интеллект", "машинное обучение",
    "квантовые вычисления", "нанотехнологии", "ядерная энергетика",
    "возобновляемая энергетика", "аэронавтика", "космические технологии",
    "автономные автомобили", "3D-печать", "биотехнологии", "генная инженерия",
    "интернет вещей", "кибербезопасность", "блокчейн", "сетевые технологии",
    "микроэлектроника", "оптоэлектроника", "телекоммуникации",
    # — история и археология —
    "первобытная история", "Месопотамия", "Шумер", "Древний Китай",
    "Древняя Индия", "Античная Греция", "Древний Рим", "средневековая Европа",
    "Византия", "эпоха Возрождения", "Великие географические открытия",
    "Индустриальная революция", "холодная война", "космическая гонка",
    "современная история", "военная история", "история науки",
    # — культура и гуманитарные —
    "лингвистика", "семиотика", "этнография", "антропология", "мифология",
    "искусствоведение", "живопись", "скульптура", "классическая музыка",
    "джаз", "кинематограф", "фотография", "архитектура", "дизайн",
    "античная философия", "современная философия", "этика", "эстетика",
    "религиоведение", "политология", "экономика", "поведенческая экономика",
    "социология", "правоведение", "криминология",
    # — прикладное и разное —
    "спортивная наука", "пищевые технологии", "эргономика",
    "урбанистика", "демография", "орнитология", "энтомология",
    "ихтиология", "астробиология", "агрономия", "виноделие",
    "пчеловодство", "логистика", "металлургия",
]
# ────────── лог и статистика ──────────
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_PATH   = SCRIPT_DIR / "fact_bot.log"
STATS_PATH = SCRIPT_DIR / "fact_stats.json"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    encoding="utf-8",
)

stats = {"total": 0, "known": 0}
if STATS_PATH.exists():
    try:
        stats.update(json.loads(STATS_PATH.read_text(encoding="utf-8")))
    except Exception:
        pass

def save_stats() -> None:
    try:
        STATS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    except Exception as exc:
        logging.error(f"Cannot write stats file: {exc}")

# ────────── OpenAI ──────────
client = OpenAI()

# ────────── функции ──────────
def fetch_fact() -> str:
    topic  = random.choice(TOPIC_POOL)
    nonce  = secrets.token_urlsafe(10)
    prompt = (
        f"Выбери один интересный факт из области «{topic}» и сформулируй его "
        "точно в одном-двух предложениях, начиная фразой "
        "«Знаете ли вы, что ...». Не упоминай тему явно, не добавляй источников.\n\n"
        f"<RANDOM_NONCE>{nonce}</RANDOM_NONCE>"
    )
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        temperature=TEMPERATURE,
    )
    return resp.choices[0].message.content.strip()


def show_popup(text: str) -> str:
    """
    Показывает окно с кнопками.
    Возвращает строку статуса: 'KNOWN', 'NEW', 'IGNORED'.
    """
    status = {"val": "IGNORED"}          # значение по-умолчанию

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    win = tk.Toplevel(root)
    win.title("Знаете ли вы, что...")
    win.attributes("-topmost", True)
    win.resizable(False, False)

    tk.Label(win, text=text, wraplength=420,
             justify="left", padx=10, pady=10).pack()

    btn_frame = tk.Frame(win, pady=8)
    btn_frame.pack()

    def finish(val: str):
        status["val"] = val
        win.destroy()

    tk.Button(btn_frame, text="Знаю",        width=12,
              command=lambda: finish("KNOWN")).pack(side="left",  padx=5)
    tk.Button(btn_frame, text="Теперь знаю", width=12,
              command=lambda: finish("NEW")).pack(side="right", padx=5)

    # timeout → IGNORED
    win.after(TIMEOUT_MS, win.destroy)
    # закрытие крестиком тоже считается IGNORED
    win.protocol("WM_DELETE_WINDOW", win.destroy)

    root.wait_window(win)
    root.destroy()
    return status["val"]


def process_fact(fact: str, status: str) -> None:
    """Обновляет статистику (если KNOWN/NEW) и пишет лог."""
    if status in ("KNOWN", "NEW"):
        stats["total"] += 1
        if status == "KNOWN":
            stats["known"] += 1
        save_stats()
        ratio = stats["known"] / stats["total"]
        logging.info(f"{status}: {fact}  |  ratio={ratio:.2%} "
                     f"({stats['known']}/{stats['total']})")
    else:                                    # IGNORED
        logging.info(f"IGNORED: {fact}")


# ────────── основной цикл ──────────
def main() -> None:
    logging.info("──── bot started ────")
    while True:
        try:
            fact   = fetch_fact()
            status = show_popup(fact)        # 'KNOWN'/'NEW'/'IGNORED'
            process_fact(fact, status)
        except Exception as exc:
            logging.exception(f"ERROR: {exc}")

        time.sleep(random.uniform(MIN_DELAY_MIN, MAX_DELAY_MIN) * 60)


if __name__ == "__main__":
    main()
