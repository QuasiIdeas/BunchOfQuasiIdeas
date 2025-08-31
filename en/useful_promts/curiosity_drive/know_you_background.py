#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
know_you_background.py
──────────────────────
Background "fact-bot" with statistics "know / don't know / ignored"
and indication of the fact's topic in the log. • Random interval 0-5 mins. • Buttons "Know" / "Now I know"; after a timeout of 20 seconds, the fact is considered IGNORED. • The log file shows: STATUS [TOPIC]: fact  |  ratio=…
• Only KNOWN/NEW stats go into (fact_stats.json). """
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

# ────────── parameters ──────────
MODEL_NAME:     Final[str] = "gpt-4o-mini"
TEMPERATURE:    Final[float] = 0.9
MIN_DELAY_MIN:  Final[int]   = 0
MAX_DELAY_MIN:  Final[int]   = 1
TIMEOUT_MS:     Final[int]   = 30_000           # 30 seconds

# ─── NEW: select level ───
#   "school"   - high school / popular level
#   "undergrad" - senior undergraduate courses
#   "grad"      - master's student / postgraduate
#   "expert"    - advanced (including specialized terms)
LEVEL = "undergrad"

TOPIC_POOL: Final[list[str]] = [
    # — natural sciences —
    "astronomy", "cosmology", "planetology", "quantum mechanics",
    "particle physics", "optics", "acoustics", "thermodynamics", "materials science",
    "organic chemistry", "inorganic chemistry", "biochemistry", "genetics",
    "microbiology", "immunology", "neurology", "plant biology",
    "zoology", "ecology", "ethology", "evolutionary biology", "paleontology",
    "medicine", "cardiology", "pharmacology", "psychology", "psychiatry",
    "climatology", "meteorology", "oceanography", "geology", "seismology",
    "volcanology", "mineralogy",
    # — mathematics and logic —
    "mathematical analysis", "algebra", "topology", "number theory",
    "statistics", "probability theory", "cryptography", "logic",
    "game theory", "combinatorics", "fractals", "computational mathematics",
    # — engineering and technology —
    "robotics", "artificial intelligence", "machine learning",
    "quantum computing", "nanotechnology", "nuclear power",
    "renewable energy", "aeronautics", "space technology",
    "autonomous vehicles", "3D printing", "biotechnology", "genetic engineering",
    "Internet of Things", "cybersecurity", "blockchain", "network technology",
    "microelectronics", "optoelectronics", "telecommunications",
    # — history and archaeology —
    "prehistory", "Mesopotamia", "Sumer", "Ancient China",
    "Ancient India", "Ancient Greece", "Ancient Rome", "medieval Europe",
    "Byzantium", "the Renaissance", "the Great Geographic Discoveries",
    "the Industrial Revolution", "the Cold War", "the Space Race",
    "modern history", "military history", "the history of science",
    # — culture and humanities —
    "linguistics", "semiotics", "ethnography", "anthropology", "mythology",
    "art history", "painting", "sculpture", "classical music",
    "jazz", "cinematography", "photography", "architecture", "design",
    "ancient philosophy", "modern philosophy", "ethics", "aesthetics",
    "religious studies", "political science", "economics", "behavioral economics",
    "sociology", "jurisprudence", "criminology",
    # — applied and miscellaneous —
    "sports science", "food technology", "ergonomics",
    "urban studies", "demography", "ornithology", "entomology",
    "ichthyology", "astrobiology", "agronomy", "winemaking",
    "beekeeping", "logistics", "metallurgy",
]

# ────────── log and statistics ──────────
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

# ────────── functions ──────────
def fetch_fact() -> tuple[str, str]:
    """Returns (fact, topic) considering LEVEL."""
    topic = random.choice(TOPIC_POOL)
    nonce = secrets.token_urlsafe(10)

    PROMPT_TEMPLATES = {
        "school": (
            "Formulate one engaging scientific-historical fact"
            f" from the area of '{topic}' in a language suitable for middle school. "
            "Start strictly with the phrase 'Did you know that...'. Do not add sources. "
        ),
        "undergrad": (
            "Formulate one amazing fact from the area of '{topic}', "
            "that would be interesting to discuss in senior undergraduate courses "
            "(advanced undergraduate). Use terms, but avoid niche specifics. "
            "Start strictly with 'Did you know that...'. Without sources. "
        ),
        "grad": (
            "Formulate one non-trivial fact at the master's level "
            f"on the topic ' {topic} '. Specialized terminology is allowed, "
            "but with no formulas. Start: 'Did you know that...'. Without references. "
        ),
        "expert": (
            "Provide one deep, little-known fact at the expert level on "
            f"the topic '{topic}', specialized terms are allowed "
            "and citation designations (but do not insert references). "
            "Start strictly with 'Did you know that...'. "
        ),
    }

    base_prompt = PROMPT_TEMPLATES.get(LEVEL, PROMPT_TEMPLATES["school"])
    prompt = f"{base_prompt}\n\n<RANDOM_NONCE>{nonce}</RANDOM_NONCE>"

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        temperature=TEMPERATURE,
    )
    fact = resp. choices[0]. message. content. strip()
    return fact, topic

def show_popup(text: str) -> str:
    """
    A window with buttons. Returns 'KNOWN', 'NEW', or 'IGNORED'. """
    status = {"val": "IGNORED"}          # default

    root = tk. Tk()
    root. withdraw()
    root. attributes("-topmost", True)

    win = tk. Toplevel(root)
    win. title("Did you know that...")  # Translated title
    win. attributes("-topmost", True)
    win. resizable(False, False)

    tk. Label(win, text=text, wraplength=420,
             justify="left", padx=10, pady=10). pack()

    btn_frame = tk. Frame(win, pady=8)
    btn_frame. pack()

    def finish(val: str):
        status["val"] = val
        win. destroy()

    tk. Button(btn_frame, text="I know",        width=12,
              command=lambda: finish("KNOWN")). pack(side="left",  padx=5)
    tk. Button(btn_frame, text="Now I know", width=12,
              command=lambda: finish("NEW")). pack(side="right", padx=5)

    win. after(TIMEOUT_MS, win. destroy)          # timeout → IGNORED
    win. protocol("WM_DELETE_WINDOW", win. destroy)

    root. wait_window(win)
    root. destroy()
    return status["val"]


def process_fact(fact: str, topic: str, status: str) -> None:
    """Updates the statistics (if needed) and writes a log entry."""
    if status in ("KNOWN", "NEW"):
        stats["total"] += 1
        if status == "KNOWN":
            stats["known"] += 1
        save_stats()
        ratio = stats["known"] / stats["total"]
        logging. info(f"{status} [{topic}]: {fact}  |  ratio={ratio: 0.2%} "
                     f"({stats['known']}/{stats['total']})")
    else:  # IGNORED
        logging. info(f"IGNORED [{topic}]: {fact}")


# ────────── main loop ──────────
def main() -> None:
    logging. info("──── bot started ────")
    while True:
        try:
            fact, topic = fetch_fact()
            status      = show_popup(fact)
            process_fact(fact, topic, status)
        except Exception as exc:
            logging. exception(f"ERROR: {exc}")

        time. sleep(random. uniform(MIN_DELAY_MIN, MAX_DELAY_MIN) * 60)


if __name__ == "__main__":
    main()
