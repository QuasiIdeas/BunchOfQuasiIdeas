#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
know_you_background.py
──────────────────────
Фоновый «факт-бот» со статистикой «знаю / не знаю / ignored»
и указанием темы факта в журнале.

• Случайный интервал 0-5 мин.
• Кнопки «Знаю» / «Теперь знаю»; по тайм-ауту 20 с факт считается IGNORED.
• Лог-файл показывает: STATUS [ТЕМА]: факт  |  ratio=…
• В статистику (fact_stats.json) идут только KNOWN/NEW.
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

# ────────── параметры ──────────
MODEL_NAME:     Final[str] = "gpt-4o-mini"
TEMPERATURE:    Final[float] = 0.9
MIN_DELAY_MIN:  Final[int]   = 0
MAX_DELAY_MIN:  Final[int]   = 1
TIMEOUT_MS:     Final[int]   = 30_000           # 30 с

# ─── НОВОЕ: выбираем уровень ───
#   "school"   — школьник / популярный уровень
#   "undergrad"— старшие курсы бакалавриата
#   "grad"     — магистрат / аспирант
#   "expert"   — продвинутый (вплоть до специализированных терминов)
LEVEL = "undergrad"

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
def fetch_fact() -> tuple[str, str]:
    """Возвращает (факт, тема) с учётом LEVEL."""
    topic  = random.choice(TOPIC_POOL)
    nonce  = secrets.token_urlsafe(10)

    PROMPT_TEMPLATES = {
        "school": (
            "Сформулируй один увлекательный научно-исторический факт"
            f" из области «{topic}» понятным языком средней школы. "
            "Начни строго фразой «Знаете ли вы, что ...». Не добавляй источников."
        ),
        "undergrad": (
            "Сформулируй один удивительный факт из области «{topic}», "
            "который было бы интересно обсудить на последних курсах бакалавриата "
            "(advanced undergraduate). Используй термины, но избегай узкоспец. "
            "Начни строго с «Знаете ли вы, что ...». Без источников."
        ),
        "grad": (
            "Сформулируй один нетривиальный факт уровня магистратуры "
            f"по теме «{topic}». Допустима специализированная терминология, "
            "но без формул. Начало: «Знаете ли вы, что ...». Без ссылок."
        ),
        "expert": (
            "Приведи один глубокий, малоизвестный факт экспертного уровня по "
            f"теме «{topic}», допустимы узкоспециализированные термины "
            "и ссылочные обозначения (но не вставляй референсы). "
            "Начни строго с «Знаете ли вы, что ...»."
        ),
    }

    base_prompt = PROMPT_TEMPLATES.get(LEVEL, PROMPT_TEMPLATES["school"])
    prompt = f"{base_prompt}\n\n<RANDOM_NONCE>{nonce}</RANDOM_NONCE>"

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        temperature=TEMPERATURE,
    )
    fact = resp.choices[0].message.content.strip()
    return fact, topic

def show_popup(text: str) -> str:
    """
    Окно с кнопками.
    Возвращает 'KNOWN', 'NEW' или 'IGNORED'.
    """
    status = {"val": "IGNORED"}          # дефолт

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    win = tk.Toplevel(root)
    win.title("Знаете ли вы, что…")
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

    win.after(TIMEOUT_MS, win.destroy)          # тайм-аут → IGNORED
    win.protocol("WM_DELETE_WINDOW", win.destroy)

    root.wait_window(win)
    root.destroy()
    return status["val"]


def process_fact(fact: str, topic: str, status: str) -> None:
    """Обновляет статистику (если нужно) и пишет запись в лог."""
    if status in ("KNOWN", "NEW"):
        stats["total"] += 1
        if status == "KNOWN":
            stats["known"] += 1
        save_stats()
        ratio = stats["known"] / stats["total"]
        logging.info(f"{status} [{topic}]: {fact}  |  ratio={ratio: 0.2%} "
                     f"({stats['known']}/{stats['total']})")
    else:  # IGNORED
        logging.info(f"IGNORED [{topic}]: {fact}")


# ────────── основной цикл ──────────
def main() -> None:
    logging.info("──── bot started ────")
    while True:
        try:
            fact, topic = fetch_fact()
            status      = show_popup(fact)
            process_fact(fact, topic, status)
        except Exception as exc:
            logging.exception(f"ERROR: {exc}")

        time.sleep(random.uniform(MIN_DELAY_MIN, MAX_DELAY_MIN) * 60)


if __name__ == "__main__":
    main()
