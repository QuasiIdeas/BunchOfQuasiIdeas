Here's the translated text in English:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
know_you_once.py
~~~~~~~~~~~~~~~~
Fetches a single "fact of the day" from a random subject area 
(chosen from a large list of tags) and shows a pop-up window 
"Did you know that…". Works with openai-python ≥ 1.0. • Each run → new tag → new fact topic. • A nonce token at the end of the prompt reduces the risk of repetitions even with 
  the same tag. """

import os
import random
import secrets
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI          # pip install --upgrade openai>=1.0

# ────────── settings ──────────
MODEL_NAME   = "gpt-4o-mini"      # replace with "o3" when available
TEMPERATURE  = 0.9
TIMEOUT_MS   = 20_000             # auto-close window (ms)

TOPIC_POOL = [
    # natural sciences
    "astronomy", "cosmology", "planetology", "particle physics", "quantum mechanics",
    "optics", "acoustics", "thermodynamics", "materials", "inorganic chemistry",
    "organic chemistry", "biochemistry", "genetics", "microbiology", "immunology",
    "neurology", "botany", "zoology", "ecology", "ethology",
    "evolutionary biology", "medicine", "cardiology", "pharmacy", "psychology",
    "psychiatry", "climatology", "meteorology", "oceanography", "geology",
    "seismology", "volcanology", "mineralogy", "geography", "cartography",
    "hydrology", "hydrodynamics", "astrophysics", "astrophotometry", "radioastronomy",
    # mathematics and logic
    "mathematical analysis", "algebra", "topology", "number theory", "statistics",
    "probability theory", "cryptography", "logic", "game theory", "combinatorics",
    "geometry", "fractals", "computational mathematics",
    # engineering and technology
    "robotics", "artificial intelligence", "machine learning", "quantum computing",
    "nanotechnology", "nuclear energy", "renewable energy", "aeronautics",
    "aviation", "space technology", "autonomous vehicles", "3D printing",
    "materials science", "biotechnology", "genetic engineering", "Internet of Things",
    "cybersecurity", "blockchain", "networking technology", "communication protocols",
    "microelectronics", "optoelectronics", "telecommunications",
    # history and archaeology
    "prehistory", "Mesopotamia", "Sumer", "Ancient China", "Ancient India",
    "Ancient Greece", "Ancient Rome", "medieval Europe", "Byzantine history",
    "The Great Voyages of Discovery", "the Renaissance", "Modern Japanese history",
    "Industrial Revolution", "Cold War", "space race", "modern history",
    "military history", "history of science", "archaeology of the Americas", "Maya", "Incas", "Vikings",
    # culture and humanities
    "linguistics", "semiotics", "ethnography", "anthropology", "mythology",
    "art history", "painting", "sculpture", "classical music", "jazz",
    "cinematography", "photography", "architecture", "design", "ancient philosophy",
    "modern philosophy", "aesthetics", "ethics", "religious studies", "political science",
    "economics", "macroeconomics", "behavioral economics", "sociology",
    "law", "criminology", "history of technology", "history of medicine",
    # applied and miscellaneous
    "sports science", "food technology", "ergonomics", "graphic design",
    "metallurgy", "logistics", "agronomy", "winemaking", "beekeeping",
    "regional studies", "urban studies", "demography", "paleontology", "ornithology",
    "entomology", "herpetology", "ichthyology", "astrobiology",
]

client = OpenAI()                 # takes OPENAI_API_KEY from the environment


# ────────── functions ──────────
def fetch_fact() -> str:
    """Returns one fact from a random subject area + nonce. """
    topic = random.choice(TOPIC_POOL)
    nonce = secrets.token_urlsafe(10)

    prompt = (
        f"Choose one interesting fact from the field of \"{topic}\" and formulate it "
        "exactly in one or two sentences, starting with the phrase "
        "\"Did you know that...\". Do not mention the topic explicitly, do not add sources. \n\n"
        f"<RANDOM_NONCE>{nonce}</RANDOM_NONCE>"
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        temperature=TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def show_popup(text: str):
    """Shows a window with the fact and closes it after TIMEOUT_MS. """
    root = tk.Tk()
    root.withdraw()
    root.after(TIMEOUT_MS, root.destroy)
    messagebox.showinfo("Did you know that... ", text, parent=root)


# ────────── entry point ──────────
if __name__ == "__main__":
    try:
        fact = fetch_fact()
        show_popup(fact)
    except Exception as exc:
        print("Error:", exc)
```

Feel free to ask if you need any more help!

