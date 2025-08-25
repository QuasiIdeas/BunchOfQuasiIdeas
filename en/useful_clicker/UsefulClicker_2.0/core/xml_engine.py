# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import time
import math
import random
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import quote_plus
import importlib
from typing import Dict, Any, Optional
import threading
import time
try:
    import keyboard  # hotkey listener for pause
except Exception:
    keyboard = None
try:
    from voice.voice_daemon import VoiceDaemon
except Exception:
    VoiceDaemon = None

# ---------- XML backend ----------
try:
    from lxml import etree as ET  # предпочтительно
except Exception:  # запасной вариант
    import xml.etree.ElementTree as ET  # type: ignore

# ---------- Ввод/клики ----------
try:
    import pyautogui
    import pyperclip
except Exception:
    pyautogui = None
    pyperclip = None

# ---------- Опциональный фокус окна ----------
try:
    import pygetwindow as gw
except Exception:
    gw = None


# ==========================
# Логгер
# ==========================
def _setup_logger() -> logging.Logger:
    log = logging.getLogger("usefulclicker")
    if not log.handlers:
        log.setLevel(logging.INFO)
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
        log.addHandler(h)
    return log


# ==========================
# Утилиты/подстановки
# ==========================
def _parse_bool(s: str) -> bool:
    return str(s).strip().lower() in ("1", "true", "yes", "y", "on")

def _maybe_int(v: str):
    try:
        return int(v)
    except Exception:
        return v

def _maybe_float(v: str):
    try:
        return float(v)
    except Exception:
        return v

def _smart_cast(s: str):
    # пробуем целое → float → строка
    v = _maybe_int(s)
    if isinstance(v, str):
        v2 = _maybe_float(v)
        return v2
    return v

def _parse_csv_list(s: str) -> list[str]:
    # "Physics, Biology , CS" -> ["Physics", "Biology", "CS"]
    return [p.strip() for p in str(s).split(",") if str(p).strip()]

def _rand_delay(ms: Optional[int]) -> float:
    return (ms or 0) / 1000.0 * random.random()


def _fixed_delay(ms: Optional[int]) -> float:
    return (ms or 0) / 1000.0


def _apply_filter(value: str, filt: str) -> str:
    """Фильтры в подстановках: ${var|url}"""
    f = (filt or "").strip().lower()
    if f in ("url", "urlencode", "quote", "quote_plus"):
        return quote_plus(str(value))
    return str(value)


_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:\|([A-Za-z_][A-Za-z0-9_]*))?\}")

def _substitute_vars(value: str, variables: Dict[str, Any]) -> str:
    if value is None:
        return ""

    def repl(m):
        var = m.group(1)
        filt = m.group(2)
        raw = variables.get(var, "")
        return _apply_filter(raw, filt)

    return _VAR_PATTERN.sub(repl, value)



# ==========================
# Safe eval для <set>/<check>
# ==========================
_ALLOWED_MATH = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "True": True,
    "False": False,
    # рандом для сценариев
    "randint": lambda a, b: random.randint(int(a), int(b)),
    "uniform": lambda a, b: random.uniform(float(a), float(b)),
    # урл-кодер, если хочется использовать в <set>
    "urlquote": lambda s: quote_plus(str(s)),
}

def _safe_eval(expr: str, vars_: Dict[str, Any]) -> Any:
    env = dict(_ALLOWED_MATH)
    env.update(vars_)
    return eval(expr, {"__builtins__": {}}, env)


def _sleep_delays(node: ET.Element):
    df = node.get("delay_fixed")
    dm = node.get("delay_ms")
    if df:
        time.sleep(_fixed_delay(int(df)))
    if dm:
        time.sleep(_rand_delay(int(dm)))


# ==========================
# Низкоуровневые действия
# ==========================

def _safe_point(x: int, y: int, margin: int = 5) -> tuple[int, int]:
    """Сдвигает координаты из опасной зоны (углы/края) внутрь экрана."""
    if not pyautogui:
        return x, y
    try:
        sw, sh = pyautogui.size()
    except Exception:
        sw, sh = 1920, 1080
    x = max(margin, min(int(x), sw - margin))
    y = max(margin, min(int(y), sh - margin))
    return x, y

def _move_then_click(x: int, y: int, button: str = "left", retries: int = 2, allow_corner: bool = False):
    """Переместить курсор в безопасную точку и кликнуть. Перепробовать при FailSafe."""
    if not pyautogui:
        return
    try:
        if not allow_corner:
            x, y = _safe_point(x, y, margin=5)
        pyautogui.moveTo(x, y, duration=0.02)
        pyautogui.click(x=x, y=y, button=button)
    except Exception as e:
        # Перехватим FailSafe и попробуем ещё раз из центра
        import traceback
        if isinstance(e, getattr(pyautogui, "FailSafeException", Exception)) or "FailSafe" in str(e):
            for _ in range(retries):
                try:
                    if not allow_corner:
                        # уведём мышь в центр и повторим
                        sw, sh = pyautogui.size()
                        pyautogui.moveTo(sw//2, sh//2, duration=0.05)
                        x2, y2 = _safe_point(x, y, margin=8)
                        pyautogui.moveTo(x2, y2, duration=0.03)
                    pyautogui.click(x=x2 if not allow_corner else x, y=y2 if not allow_corner else y, button=button)
                    return
                except Exception:
                    time.sleep(0.05)
            # если не вышло — пробрасываем дальше
        raise

def _hotkey(combo: str, delay_ms: Optional[int] = None):
    # 1) keyboard.send (сканкоды, надёжнее для шорткатов)
    try:
        import keyboard as kb
        kb.send('+'.join([p.strip() for p in combo.split('+') if p.strip()]))
        if delay_ms: time.sleep(delay_ms/1000.0)
        return
    except Exception:
        pass
    # 2) fallback на pyautogui
    if not pyautogui:
        return
    keys = [p.strip().lower() for p in combo.split('+') if p.strip()]
    if not keys:
        return
    pyautogui.hotkey(*keys)
    if delay_ms:
        time.sleep(delay_ms / 1000.0)



def _keysequence(seq: str, delay_ms: Optional[int] = None):
    if not pyautogui:
        return
    if delay_ms:
        for ch in seq:
            pyautogui.write(ch)
            time.sleep(delay_ms / 1000.0)
    else:
        pyautogui.write(seq)


def _type_text(text: str, mode: str = "type"):
    """Надёжное копирование: ретраи буфера, фоллбэк на печать."""
    if not pyautogui:
        return
    s = str(text)

    if mode.lower() != "copy_paste" or not pyperclip:
        pyautogui.write(s)
        return

    ok = False
    for attempt in range(5):
        try:
            pyperclip.copy(s)
        except Exception:
            time.sleep(0.1)
            continue

        time.sleep(0.15 + 0.05 * attempt)

        try:
            cur = pyperclip.paste()
        except Exception:
            cur = None

        if cur == s:
            ok = True
            break

    if ok:
        pyautogui.hotkey("ctrl", "v")
    else:
        pyautogui.write(s)


def _click_xy(x: int, y: int, button: str = "left", allow_corner: bool = False):
    if not pyautogui:
       return
    _move_then_click(x, y, button=button, allow_corner=allow_corner)

def _click_area(area_tuple, button: str = "left"):
    if not pyautogui:
        return
    x1, y1, x2, y2 = area_tuple
    rx = random.randint(min(x1, x2), max(x1, x2))
    ry = random.randint(min(y1, y2), max(y1, y2))
    _move_then_click(rx, ry, button=button)


# ==========================
# LLM fallback (если нет llm/openai_client.py)
# ==========================
_NUMBER_PREFIX = re.compile(r"""^\s*(?:\d+[\)\.\-:]|[\-\•\*])\s*""", re.X)

def _cleanup_list_item(s: str) -> str:
    s = s.strip()
    s = _NUMBER_PREFIX.sub("", s)
    s = s.strip(" \t\"'“”‘’")
    return s

def _llm_generate_list(prompt: str, separator: str = "\n", logger: logging.Logger = _setup_logger()) -> list[str]:
    try:
        from llm.openai_client import LLMClient  # если есть
        client = LLMClient()
        raw_items = client.generate_list(prompt, separator=separator)
    except Exception as e:
        logger.info(f"Exception: {e}")
        raw_items = [
            "Fourplay — 101 Eastbound",
            "Bob James — Westchester Lady",
            "Grover Washington Jr. — Winelight",
            "Kenny G — Songbird",
            "Earl Klugh — Midnight in San Juan",
            "Lee Ritenour — Night Rhythms",
            "David Sanborn — Chicago Song",
            "Spyro Gyra — Morning Dance",
            "Chris Botti — Venice",
            "George Benson — Breezin'",
            "Pieces of a Dream — Warm Weather",
            "Acoustic Alchemy — Mr. Chow",
            "Norman Brown — After The Storm",
            "Rick Braun — Notorious",
            "Paul Hardcastle — Rainforest",
            "Candy Dulfer — Lily Was Here",
            "Sade — Smooth Operator (jazz cover)",
            "Marcus Miller — Panther",
            "Najee — Sweet Love",
            "The Rippingtons — Curves Ahead",
        ]

    out: list[str] = []
    for it in raw_items:
        if it is None:
            continue
        s = str(it)
        if "\n" in s and len(raw_items) == 1:
            parts = s.split(separator or "\n")
        else:
            parts = [s]
        for p in parts:
            p = _cleanup_list_item(p)
            if p:
                out.append(p)
    return out

def _llm_generate_text(prompt: str, logger) -> str:
    try:
        from llm.openai_client import LLMClient
        client = LLMClient()
        return client.generate_text(prompt)
    except Exception as e:
        logger.info(f"Exception: {e}")

        return "\n".join(_llm_generate_list(prompt))


# ==========================
# Основной класс XMLProgram
# ==========================
class XMLProgram:
    def __init__(self, xml_path: Path, debug: bool = False, log_path: Optional[Path] = None):
        self.xml_path = Path(xml_path)
        self.debug = debug
        self.logger = _setup_logger()
        self._extnode_cache = {}   # {(module, class): instance}
        self._extmodule_cache = {} # {module: module_object}
        self.voice = None
        self.skip_wait = False
        self.paused = False
        self._start_pause_listener()  # запустим слушатель пробела
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, ET.Element] = {}
        self.xml_text: str = ""
        self._load_xml()

        # Экран для удобных сценариев
        try:
            if pyautogui:
                sw, sh = pyautogui.size()
                self.variables["SCREEN_W"] = int(sw)
                self.variables["SCREEN_H"] = int(sh)
        except Exception:
            pass
        self.variables.setdefault("SCREEN_W", 1920)
        self.variables.setdefault("SCREEN_H", 1080)

    def _ensure_voice(self):
        """Стартует голосовой демон при первом запросе, если включён VOICE_ENABLED/ENV."""
        if self.voice is not None:
            return

        # можно включать через переменную в XML, флаг окружения или дефолт
        flag_xml = str(self.variables.get("VOICE_ENABLED", "0")).strip().lower() in ("1", "true", "yes")
        flag_env = str(os.getenv("USEFULCLICKER_VOICE", "0")).strip().lower() in ("1", "true", "yes")
        if not (flag_xml or flag_env):
            return

        if VoiceDaemon is None:
            self.logger.info("VOICE: VoiceDaemon not available (import failed).")
            return

        # можно прочитать желаемый индекс микрофона из переменной VOICE_DEVICE (если задашь его через <set>)
        dev = self.variables.get("VOICE_DEVICE")
        try:
            dev = int(dev) if dev is not None and str(dev).strip() != "" else None
        except Exception:
            dev = None

        try:
            self.voice = VoiceDaemon(model_name="base", device=dev, lang=None).start()
            self.logger.info("VOICE: background voice daemon started.")
        except Exception as e:
            self.logger.info(f"VOICE: failed to start ({e})")
            self.voice = None
              
    def _sleep_ms_interruptible(self, total_ms: int):
        """Sleep total_ms ms, respecting pause and skip-wait hotkey."""
        if total_ms <= 0:
            return
        end_ts = time.time() + total_ms / 1000.0
        step = 0.05
        while True:
            # прерывание ожидания по Ctrl+N
            if self.skip_wait:
                self.skip_wait = False
                break

            # уважаем паузу
            self._pause_gate()

            now = time.time()
            if now >= end_ts:
                break
            remain = end_ts - now
            time.sleep(step if remain > step else remain)


    # ---------- Загрузка XML + <include> ----------
    def _load_xml(self):
        text = self.xml_path.read_text(encoding="utf-8")

        root_dir = self.xml_path.parent
        include_pat = re.compile(r"<include>\s*(.*?)\s*</include>", flags=re.I)
        includes = include_pat.findall(text)
        combined = [text]
        for inc in includes:
            inc_path = (root_dir / inc.strip()).resolve()
            if inc_path.exists():
                self.logger.info(f"Including: {inc_path}")
                combined.append(inc_path.read_text(encoding="utf-8"))
        self.xml_text = "\n".join(combined)

        self.tree = ET.fromstring(self.xml_text.encode("utf-8"))

        for func in self.tree.findall(".//func"):
            name = func.get("name")
            if name:
                self.functions[name] = func

    # ---------- Общие задержки ----------
    def _delays(self, node: ET.Element):
        #_sleep_delays(node)
        df = node.get("delay_fixed")
        dm = node.get("delay_ms")

        # фиксированная задержка — целиком
        if df:
            try:
                self._sleep_ms_interruptible(int(df))
            except Exception:
                pass

        # случайная задержка — до указанного максимума
        if dm:
            try:
                import random
                jitter = random.uniform(0, int(dm) / 1000.0)
                self._sleep_ms_interruptible(int(jitter * 1000))
            except Exception:
                pass

    def _skip_wait_now(self):
        self.skip_wait = True
        self.logger.info("WAIT skipped by Ctrl+N")
    
    def _start_pause_listener(self):
        """Запускает поток, который вешает хоткей 'space' для паузы/резюма."""
    
        def _worker():
            if keyboard is None:
                self.logger.info("PAUSE: keyboard module not available; pause hotkey disabled.")
                return
            try:
                keyboard.add_hotkey("ctrl+space", self._toggle_pause)
                keyboard.add_hotkey("ctrl+n", self._skip_wait_now)
                self.logger.info("PAUSE: press <ctrl + Space> to toggle pause/resume.")
                self.logger.info("NEXT: press <ctrl + N> to next search.")
                keyboard.wait()  # держим слушатель живым
            except Exception as e:
                self.logger.info(f"PAUSE listener error: {e}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _toggle_pause(self):
        self.paused = not self.paused
        self.logger.info(f"PAUSE {'ON' if self.paused else 'OFF'}")

    def _pause_gate(self):
        """Если включена пауза — ждём, пока её не снимут. Вызывать перед исполнением любой ноды/действия."""
        while getattr(self, "paused", False):
            time.sleep(0.05)


    # ---------- Обработчики тегов ----------
    def handle_set(self, node: ET.Element):
        for k, v in list(node.attrib.items()):
            if k in ("delay_fixed", "delay_ms"):
                continue
            expr = _substitute_vars(v, self.variables)
            try:
                val = _safe_eval(expr, self.variables)
            except Exception:
                val = expr
            self.logger.info(f"SET {k} = {val}")
            self.variables[k] = val
        self._delays(node)
        
    def handle_if(self, node: ET.Element):
        cond_raw = node.get("cond", "")
        try:
            cond_expanded = _substitute_vars(cond_raw, self.variables)
        except Exception:
            cond_expanded = cond_raw

        try:
            res = bool(eval((cond_expanded.strip() or "False"), {"__builtins__": {}}, {}))
            self.logger.info(f"IF cond='{cond_expanded}' -> {res}")
        except Exception as e:
            self.logger.info(f"IF eval error: cond='{cond_expanded}' ({e}) -> False")
            res = False

        in_else = False
        for child in list(node):
            tag = getattr(child, "tag", None)
            # пропускаем комментарии/PI/текст
            if not isinstance(tag, str):
                continue
            tagl = tag.lower()
            if tagl == "else":
                in_else = True
                continue
            # выполняем нужную ветку
            if (res and not in_else) or ((not res) and in_else):
                self._exec_node(child)



    def handle_check(self, node: ET.Element):
        tol = float(node.get("tol")) if node.get("tol") else None
        for k, v in list(node.attrib.items()):
            if k in ("delay_fixed", "delay_ms", "tol", "comment"):
                continue
            expected_raw = _substitute_vars(v, self.variables)
            actual = self.variables.get(k)
            ok = False
            if tol is not None:
                try:
                    exp = float(_safe_eval(expected_raw, self.variables))
                    act = float(actual)
                    ok = abs(exp - act) <= tol
                except Exception:
                    ok = False
            else:
                ok = str(actual) == expected_raw
            self.logger.info(f"CHECK {k}: actual={actual} expected={expected_raw} tol={tol} -> {ok}")
            if not ok:
                raise AssertionError(f"Check failed for {k}: actual={actual}, expected={expected_raw}")
        self._delays(node)

    def handle_type(self, node: ET.Element):
        mode = node.get("mode", "type")
        text = _substitute_vars(node.get("text", ""), self.variables)
        self.logger.info(f"TYPE mode={mode} text='{text[:60]}'")
        _type_text(text, mode=mode)
        self._delays(node)

    def handle_click(self, node: ET.Element):
        button = node.get("button", "left")
        allow_corner = str(node.get("allow_corner","0")).strip().lower() in ("1","true","yes")
        area = node.get("area")
        if area:
            # Подстановка переменных и безопасная оценка выражений в каждом числе
            area_eval = _substitute_vars(area, self.variables)
            parts = []
            for p in area_eval.split(","):
                p = p.strip()
                if not p:
                    continue
                try:
                    v = _safe_eval(p, self.variables)
                except Exception:
                    v = p  # fallback
                parts.append(int(float(v)))
            if len(parts) != 4:
                raise ValueError("area must be 'x1,y1,x2,y2' after substitution")
            self.logger.info(f"CLICK area={parts} button={button}")
            _click_area(tuple(parts), button=button)
        else:
            # Подстановка и оценка для x/y тоже полезна (можно писать x="${CX}" и т.п.)
            x_raw = _substitute_vars(node.get("x"), self.variables)
            y_raw = _substitute_vars(node.get("y"), self.variables)
            try:
                x = int(float(_safe_eval(x_raw, self.variables)))
                y = int(float(_safe_eval(y_raw, self.variables)))
            except Exception:
                x = int(float(x_raw))
                y = int(float(y_raw))
            self.logger.info(f"CLICK x={x} y={y} button={button}")
            _click_xy(x, y, button=button, allow_corner=allow_corner)
        self._delays(node)


    def handle_voice_event(self, node: ET.Element):
        """
        <voice_event wait="30000" type="any|command|query" out="VOICE_TEXT"/>
        Ждёт до wait мс событие от голосового демона и сохраняет текст и тип.
        """
        # обеспечить запуск демона к моменту первого вызова
        self._ensure_voice()

        want = (node.get("type") or "any").lower()
        out = node.get("out") or "VOICE_TEXT"
        wait_ms = int(node.get("wait", "0"))

        text = ""
        typ = ""

        if self.voice is None:
            # демон не поднялся — вернём пусто
            self.variables[out] = text
            self.variables[out + "_type"] = typ
            self._delays(node)
            return

        # попытка совместимости: если у объекта есть get_event -> используем его
        if hasattr(self.voice, "get_event"):
            # старый контроллер
            deadline = time.time() + (wait_ms / 1000.0) if wait_ms else None
            while True:
                self._pause_gate()
                evt = self.voice.get_event(timeout_ms=200)
                if evt:
                    if want in ("any", getattr(evt, "type", "")):
                        text = getattr(evt, "text", "") or ""
                        typ = getattr(evt, "type", "") or ""
                        break
                if deadline and time.time() > deadline:
                    break
        else:
            # VoiceDaemon с get_next_command / get_next_query
            deadline = time.time() + (wait_ms / 1000.0) if wait_ms else None
            while True:
                self._pause_gate()
                evt = None
                if want in ("any", "command"):
                    evt = self.voice.get_next_command(timeout_ms=0)
                    if evt and (want in ("any", "command")):
                        text, typ = evt.text, "command"
                        break
                if want in ("any", "query"):
                    evt = self.voice.get_next_query(timeout_ms=0)
                    if evt and (want in ("any", "query")):
                        text, typ = evt.text, "query"
                        break
                if deadline and time.time() > deadline:
                    break
                time.sleep(0.05)

        self.variables[out] = text
        self.variables[out + "_type"] = typ
        self.logger.info(f"VOICE_EVENT -> {out}='{text}' type='{typ}'")
        self._delays(node)

    def handle_hotkey(self, node: ET.Element):
        combo = node.get("hotkey")
        seq = node.get("keysequence")
        d = node.get("delay_ms")
        d_ms = int(d) if d else None
        if combo:
            self.logger.info(f"HOTKEY {combo}")
            _hotkey(combo, delay_ms=d_ms)
        elif seq:
            self.logger.info(f"KEYSEQUENCE '{seq}'")
            _keysequence(seq, delay_ms=d_ms)
        self._delays(node)

    def _decode_escapes(self, s: str) -> str:
        # переводит "\n", "\t", "\x.." и пр. в реальные символы
        return s.encode("utf-8").decode("unicode_escape")

    def handle_shell(self, node: ET.Element):
        """
        <shell shell_type="cmd|powershell|bash"
               bg="0|1"
               showConsole="0|1"
               output_var="VAR"
               output_format="text|list"
               separator="\\n"
               cmd="echo hi ${NAME}"/>
        Или текстом:
        <shell> echo hello ${NAME} </shell>
        """
        shell_type = (node.get("shell_type") or "cmd").lower()
        bg = str(node.get("bg", "0")).strip().lower() in ("1","true","yes")
        show_console = str(node.get("showConsole", "0")).strip().lower() in ("1","true","yes")

        # separator для разбиения stdout, если output_format="list"
        sep_raw = node.get("separator") or "\n"
        separator = self._decode_escapes(sep_raw)

        out_var = node.get("output_var")
        out_fmt = (node.get("output_format") or "text").lower()

        # исходная команда может быть в атрибуте cmd или в тексте ноды
        cmd_raw = node.get("cmd")
        if cmd_raw is None:
            cmd_raw = node.text or ""

        # ПОДСТАНОВКА переменных во всех атрибутах/тексте
        cmd_expanded = _substitute_vars(cmd_raw, self.variables)

        # ЛОГ — уже с подставленными значениями
        self.logger.info(f"SHELL type={shell_type} bg={bg} cmd={cmd_expanded}")

        # Формируем реальную команду под платформу/оболочку
        if shell_type in ("cmd", "cmd.exe", "windows", "win"):
            exe = "cmd"
            args = [exe, "/c", cmd_expanded]
            creationflags = 0 if show_console else 0x08000000  # CREATE_NO_WINDOW
        elif shell_type in ("powershell", "pwsh"):
            exe = "powershell"
            args = [exe, "-NoProfile", "-Command", cmd_expanded]
            creationflags = 0 if show_console else 0x08000000
        elif shell_type in ("bash", "sh"):
            exe = "bash"
            args = [exe, "-lc", cmd_expanded]
            creationflags = 0
        else:
            # по умолчанию пробуем системную оболочку
            exe = "cmd" if os.name == "nt" else "bash"
            args = [exe, "/c" if os.name == "nt" else "-lc", cmd_expanded]
            creationflags = 0 if show_console or os.name != "nt" else 0x08000000

        try:
            if bg and not out_var:
                # Фоновый запуск без захвата вывода
                subprocess.Popen(args, creationflags=creationflags)
            else:
                # С захватом вывода (или синхронно)
                cp = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    creationflags=creationflags,
                    check=False,
                )
                stdout = (cp.stdout or "").strip()
                stderr = (cp.stderr or "").strip()
                if stderr:
                    self.logger.info(f"SHELL stderr: {stderr}")

                if out_var is not None:
                    if out_fmt == "list":
                        self.variables[out_var] = [s for s in stdout.split(separator) if s.strip()]
                    else:
                        self.variables[out_var] = stdout

        except Exception as e:
            self.logger.info(f"SHELL error: {e}")

        # задержки после ноды (с учётом паузы/skip-wait, если у тебя реализовано)
        self._delays(node)


    def handle_focus(self, node: ET.Element):
        title = node.get("title") or node.get("title_contains") or ""
        retries = int(node.get("retries", "20"))
        interval_ms = int(node.get("interval_ms", "200"))
        if not gw:
            self.logger.info("FOCUS skipped: pygetwindow not available")
            self._delays(node); return
        ok = False
        for _ in range(retries):
            try:
                for w in gw.getAllWindows():
                    if title.lower() in (w.title or "").lower():
                        try:
                            w.minimize(); w.restore()
                        except Exception:
                            pass
                        try:
                            w.activate(); ok = True; break
                        except Exception:
                            try:
                                w.maximize(); w.restore(); w.activate(); ok = True; break
                            except Exception:
                                pass
                if ok: break
                time.sleep(interval_ms / 1000.0)
            except Exception:
                time.sleep(interval_ms / 1000.0)
        self.logger.info(f"FOCUS title~='{title}' -> {ok}")
        self._delays(node)

    # --------- <llmcall> ----------
    def handle_llmcall(self, node: ET.Element):
        """
        <llmcall output_var="tunes_list"
                 output_format="list"
                 separator="\n"
                 prompt="..."/>
        """
        out_var = node.get("output_var")
        if not out_var:
            return
        out_fmt = (node.get("output_format") or "text").lower()
        sep = node.get("separator") or "\n"
        sep = sep.encode("utf-8").decode("unicode_escape")
        prompt = node.get("prompt") or (node.text or "")
        prompt = _substitute_vars(prompt, self.variables)

        if out_fmt == "list":
            items = _llm_generate_list(prompt, separator=sep, logger=self.logger)
            clean = []
            for s in items:
                t = _cleanup_list_item(str(s))
                if t:
                    clean.append(t)
            self.variables[out_var] = clean
        else:
            text = _llm_generate_text(prompt, self.logger)
            self.variables[out_var] = text
        self.logger.info(f"LLMCALL -> {out_var} (format={out_fmt})")
        self._delays(node)

    # --------- <foreach> ----------
    def handle_foreach(self, node: ET.Element):
        """
        <foreach list="tunes_list" do="SearchYoutube" var="item"/>
        Устанавливает также index и arg0 (= текущий элемент).
        """
        list_attr = node.get("list") or ""
        func_name = node.get("do") or ""
        var_name = node.get("var") or "item"
        if not func_name:
            return

        if list_attr in self.variables:
            data = self.variables[list_attr]
        else:
            raw = _substitute_vars(list_attr, self.variables)
            data = [s for s in re.split(r"[\r\n]+", raw) if s.strip()]

        if isinstance(data, str):
            items = [s for s in re.split(r"[\r\n]+", data) if s.strip()]
        else:
            items = list(data)
            
        # --- новая опция ---
        shuffle = node.attrib.get("random_shuffle", "0")
        if shuffle in ("1", "true", "yes"):
            random.shuffle(items)

        if func_name not in self.functions:
            raise ValueError(f"Unknown function in foreach: {func_name}")

        for idx, val in enumerate(items):
            self._pause_gate()
            self.variables[var_name] = val
            self.variables["index"] = idx
            self.variables["arg0"] = val
            func = self.functions[func_name]
            for child in list(func):
                self._pause_gate()
                self._exec_node(child)

        self._delays(node)

    def handle_func(self, node: ET.Element):
        pass

    def handle_call(self, node: ET.Element):
        """
        <call name="FuncName" arg0="value" arg1="${var}" />
        Все argN записываются в переменные перед исполнением функции.
        """
        name = node.get("name")
        if not name or name not in self.functions:
            raise ValueError(f"Unknown function: {name}")

        for k, v in node.attrib.items():
            if k.startswith("arg"):
                self.variables[k] = _substitute_vars(v, self.variables)

        self.logger.info(f"CALL {name}")
        func = self.functions[name]
        for child in list(func):
            self._exec_node(child)
        self._delays(node)

    # --------- <repeat> ----------
    def handle_repeat(self, node: ET.Element):
        """
        <repeat times="randint(3,7)">
            ...любые теги...
        </repeat>
        """
        expr = node.get("times") or node.get("count") or "0"
        try:
            n = int(_safe_eval(_substitute_vars(expr, self.variables), self.variables))
        except Exception:
            n = 0
        n = max(0, n)
        self.logger.info(f"REPEAT times={n}")
        for _ in range(n):
            for child in list(node):
                self._pause_gate()
                self._exec_node(child)
        self._delays(node)

    def handle_wait(self, node: ET.Element):
        ms = int(node.get("ms", "0"))
        self.logger.info(f"WAIT {ms}ms")
        self._sleep_ms_interruptible(ms)

    def handle_voice_poll(self, node: ET.Element):
        self._ensure_voice()
        out_cmd = node.get("out_cmd") or "VOICE_CMD"
        out_query = node.get("out_query") or "VOICE_QUERY"

        cmd, query = "", ""

        if self.voice:
            evt_cmd = self.voice.get_next_command(timeout_ms=0)
            if evt_cmd:
                cmd = evt_cmd.text
                if evt_cmd.payload and "seconds" in evt_cmd.payload:
                    self.variables[out_cmd + "_seconds"] = evt_cmd.payload["seconds"]

            evt_query = self.voice.get_next_query(timeout_ms=0)
            if evt_query:
                query = evt_query.text

        self.variables[out_cmd] = cmd
        self.variables[out_query] = query
        self.logger.info(f"VOICE_POLL -> {out_cmd}='{cmd}' {out_query}='{query}'")
        self._delays(node)


    # в начале файла (если нужно)
    from typing import Any, Dict

    def handle_extnode(self, node):
        mod_name = node.get("module")
        cls_name = node.get("class")
        method   = node.get("method")
        out_var  = node.get("output_var")

        if not mod_name or not method:
            raise RuntimeError("<extnode> requires module and method")

        # 1) Импортируем модуль (с кэшем, если уже добавил self._extmodule_cache)
        import importlib
        if not hasattr(self, "_extmodule_cache"):
            self._extmodule_cache = {}
        mod = self._extmodule_cache.get(mod_name)
        if mod is None:
            mod = importlib.import_module(mod_name)
            self._extmodule_cache[mod_name] = mod

        # 2) Готовим цель вызова (класс или модульная функция)
        if cls_name:
            if not hasattr(self, "_extnode_cache"):
                self._extnode_cache = {}
            key = (mod_name, cls_name)
            inst = self._extnode_cache.get(key)
            if inst is None:
                cls = getattr(mod, cls_name)
                inst = cls()  # при необходимости передай параметры в конструктор
                self._extnode_cache[key] = inst
            call_target = getattr(inst, method)
        else:
            call_target = getattr(mod, method)

        # 3) Собираем kwargs (БЕЗ _eval_expr!)
        kw: Dict[str, Any] = {}
        for k, v in node.attrib.items():
            if k in {"module", "class", "method", "output_var",
                     "delay_fixed", "delay_ms", "func", "output_format", "separator"}:
                continue
            vv = _substitute_vars(v, self.variables)  # подстановка ${...}
            if k in ("disciplines", "subtopics") or k.lower().endswith("_list"):
                kw[k] = _parse_csv_list(vv)
            else:
                kw[k] = _smart_cast(vv)

        # 4) Вызов ТАК: **kw (а не kwargs!)
        res = call_target(**kw)

        # 5) Сохранить результат в переменную (если нужно)
        if out_var:
            self.variables[out_var] = "" if res is None else res

        self._delays(node)



    # ---------- Диспетчер ----------
    def _exec_node(self, node: ET.Element):
        
        self._pause_gate()
    
        tag = node.tag if isinstance(getattr(node, "tag", None), str) else ""
        tagl = tag.lower()

        if tagl == "set":
            self.handle_set(node)
        elif tagl == "if":
            self.handle_if(node)
            return
        elif tagl == "voice_poll":
            self.handle_voice_poll(node)
        elif tagl == "check":
            self.handle_check(node)
        elif tagl == "type":
            self.handle_type(node)
        elif tagl == "click":
            self.handle_click(node)
        elif tagl == "hotkey":
            self.handle_hotkey(node)
        elif tagl == "shell":
            self.handle_shell(node)
        elif tagl == "focus":
            self.handle_focus(node)
        elif tagl == "llmcall":
            self.handle_llmcall(node)
        elif tagl == "foreach":
            self.handle_foreach(node)
        elif tagl == "func":
            self.handle_func(node)
        elif tagl == "call":
            self.handle_call(node)
        elif tagl == "repeat":
            self.handle_repeat(node)
        elif tagl == "wait":
            self.handle_wait(node)
        elif tagl == "extnode":
            self.handle_extnode(node)
        elif tagl == "voice_event":
            self.handle_voice_event(node)
        else:
            # игнор неизвестных на этом этапе
            pass

    # ---------- Запуск ----------
    def run(self):
        for node in list(self.tree):
            tag = node.tag if isinstance(getattr(node, "tag", None), str) else ""
            if tag.lower() == "func":
                continue
            if tag == "":
                continue
            self._exec_node(node)
