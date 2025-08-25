
# -*- coding: utf-8 -*-
from __future__ import annotations
import sys, os, re, time, math, random, logging, subprocess, importlib, threading, platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import quote_plus

# -------- Logger --------
def _setup_logger() -> logging.Logger:
    log = logging.getLogger("usefulclicker")
    if not log.handlers:
        log.setLevel(logging.INFO)
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
        log.addHandler(h)
    return log

logger = _setup_logger()

# -------- Hotkey bridge (WinAPI) --------
SKIP_EVENT = None
PAUSE_TOGGLE_EVENT = None
try:
    if platform.system().lower() == "windows":
        sys.path.insert(0, os.path.dirname(__file__))
        from hotkeys_win_safe import start_hotkeys, SKIP_EVENT as _SE, PAUSE_TOGGLE_EVENT as _PE
        start_hotkeys()
        SKIP_EVENT = _SE
        PAUSE_TOGGLE_EVENT = _PE
        print("[xml_engine_full_voice] hotkeys_win_safe started", file=sys.stderr)
except Exception as e:
    print(f"[xml_engine_full_voice] hotkeys bridge unavailable: {e}", file=sys.stderr)

# -------- Optional modules --------
try:
    import keyboard
except Exception:
    keyboard = None

try:
    import pyautogui, pyperclip
except Exception:
    pyautogui = None; pyperclip = None

try:
    import pygetwindow as gw
except Exception:
    gw = None

try:
    from lxml import etree as ET
except Exception:
    import xml.etree.ElementTree as ET  # type: ignore

# Voice (optional)
# перед import VoiceDaemon:
try:
    from voice.voice_daemon import VoiceDaemon
except Exception:
    # Fallback: подцепить файл по относительному пути, если нет пакета voice
    import importlib.util, os
    p = os.path.join(os.path.dirname(__file__), "voice_daemon.py")
    if os.path.exists(p):
        spec = importlib.util.spec_from_file_location("voice_daemon", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        VoiceDaemon = getattr(m, "VoiceDaemon", None)
    else:
        VoiceDaemon = None


# -------- Substitution & eval --------
_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:\|([A-Za-z_][A-Za-z0-9_]*))?\}")

def _apply_filter(value: str, filt: Optional[str]) -> str:
    f = (filt or "").strip().lower()
    if f in ("url","urlencode","quote","quote_plus"):
        return quote_plus(str(value))
    return str(value)

def _substitute_vars(value: Optional[str], variables: Dict[str, Any]) -> str:
    if value is None: return ""
    def repl(m):
        var, filt = m.group(1), m.group(2)
        raw = variables.get(var, "")
        return _apply_filter(raw, filt)
    return _VAR_PATTERN.sub(repl, value)

_ALLOWED = {
    "pi": math.pi, "e": math.e, "tau": math.tau,
    "abs": abs, "min": min, "max": max, "round": round,
    "int": int, "float": float,
    "randint": lambda a,b: random.randint(int(a), int(b)),
}

def _safe_eval(expr: str, env: Dict[str, Any]) -> Any:
    expr = (expr or "").replace("&lt;","<").replace("&gt;",">")
    return eval(expr, {"__builtins__": {}}, {**_ALLOWED, **env})

def _smart_cast(s: Any):
    if isinstance(s, (int,float,bool)): return s
    st = str(s).strip().lower()
    if st in ("1","true","yes","on"): return True
    if st in ("0","false","no","off"): return False
    try:
        if "." in st: return float(st)
        return int(st)
    except Exception:
        return s

# -------- Low-level actions --------
def _hotkey(combo: str):
    sent=False
    try:
        if keyboard: keyboard.send('+'.join([p.strip() for p in combo.split('+') if p.strip()])); sent=True
    except Exception: sent=False
    if not sent and pyautogui:
        keys=[p.strip().lower() for p in combo.split('+') if p.strip()]
        if keys: pyautogui.hotkey(*keys)

def _type_text(text: str, mode: str = "type"):
    if not pyautogui: return
    s = str(text)
    if mode.lower() != "copy_paste" or not pyperclip:
        pyautogui.write(s); return
    ok=False
    for attempt in range(5):
        try: pyperclip.copy(s)
        except Exception: time.sleep(0.05); continue
        time.sleep(0.1 + 0.05*attempt)
        try: cur = pyperclip.paste()
        except Exception: cur=None
        if cur == s: ok=True; break
    if ok: pyautogui.hotkey("ctrl","v")
    else:  pyautogui.write(s)

def _click_xy(x: int, y: int, button: str="left"):
    if pyautogui:
        try:
            pyautogui.moveTo(int(x), int(y), duration=0.02)
            pyautogui.click(x=int(x), y=int(y), button=button)
        except Exception as e:
            logger.info(f"click error: {e}")

# -------- Engine --------
class XMLProgram:
    def __init__(self, xml_path: Path, debug: bool=False, log_path: Optional[Path]=None):
        self.xml_path = Path(xml_path)
        self.logger = logger
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, ET.Element] = {}
        self.paused = False
        self.skip_wait = False
        self._last_ctrlspace = False
        self._hotkeys_started = False
        self._extmodule_cache = {}
        self._extclass_cache = {}
        self.voice = None  # VoiceDaemon instance

        # Screen defaults
        try:
            if pyautogui:
                sw, sh = pyautogui.size()
                self.variables["SCREEN_W"] = int(sw)
                self.variables["SCREEN_H"] = int(sh)
        except Exception:
            pass
        self.variables.setdefault("SCREEN_W", 1920)
        self.variables.setdefault("SCREEN_H", 1080)

        self._load_xml()
        self._start_fallback_hotkeys()

    # ---- hotkeys fallback ----
    def _start_fallback_hotkeys(self):
        if self._hotkeys_started: return
        def worker():
            if keyboard is None: return
            try:
                keyboard.add_hotkey("ctrl+space", self._toggle_pause)
                keyboard.add_hotkey("ctrl+n", self._skip_now)
                self.logger.info("Hotkeys armed (fallback): pause=Ctrl+Space, skip=Ctrl+N")
                self._hotkeys_started=True
                keyboard.wait()
            except Exception as e:
                self.logger.info(f"keyboard hotkeys error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _toggle_pause(self):
        self.paused = not self.paused
        self.logger.info(f"PAUSE {'ON' if self.paused else 'OFF'}")

    def _skip_now(self):
        self.skip_wait = True
        self.logger.info("WAIT skip requested")

    def _poll_hotkeys_inline(self):
        global SKIP_EVENT, PAUSE_TOGGLE_EVENT
        try:
            if SKIP_EVENT is not None and SKIP_EVENT.is_set():
                SKIP_EVENT.clear()
                self.skip_wait = True
            if PAUSE_TOGGLE_EVENT is not None and PAUSE_TOGGLE_EVENT.is_set():
                PAUSE_TOGGLE_EVENT.clear()
                self._toggle_pause()
        except Exception:
            pass
        if keyboard is None: return
        try:
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("n"):
                self.skip_wait = True
            pressed = keyboard.is_pressed("ctrl") and keyboard.is_pressed("space")
            if pressed and not self._last_ctrlspace:
                self._toggle_pause(); self._last_ctrlspace=True
            if not pressed and self._last_ctrlspace:
                self._last_ctrlspace=False
        except Exception:
            pass

    def _pause_gate(self):
        while self.paused:
            self._poll_hotkeys_inline()
            time.sleep(0.05)

    def _sleep_ms_interruptible(self, ms:int):
        if ms<=0: return
        end = time.monotonic() + ms/1000.0
        tick = 0.03
        while True:
            self._poll_hotkeys_inline()
            if self.skip_wait:
                self.skip_wait=False
                self.logger.info("WAIT interrupted")
                return
            if self.paused:
                time.sleep(tick); continue
            now = time.monotonic()
            if now >= end: return
            time.sleep(min(tick, end-now))

    # ---- Voice ----
    def _ensure_voice(self):
        if self.voice is not None: return
        # check flags
        flag_xml = str(self.variables.get("VOICE_ENABLED","0")).strip().lower() in ("1","true","yes")
        flag_env = str(os.getenv("USEFULCLICKER_VOICE","0")).strip().lower() in ("1","true","yes")
        if not (flag_xml or flag_env):
            return
        if VoiceDaemon is None:
            self.logger.info("VOICE: VoiceDaemon not available (import failed)."); return
        dev = self.variables.get("VOICE_DEVICE")
        try: dev = int(dev) if (dev is not None and str(dev).strip()!="") else None
        except Exception: dev = None
        try:
            self.voice = VoiceDaemon(model_name="base", device=dev, lang=None).start()
            self.logger.info("VOICE: background voice daemon started.")
        except Exception as e:
            self.logger.info(f"VOICE: failed to start ({e})"); self.voice=None

    def handle_voice_event(self, node: ET.Element):
        self._ensure_voice()
        want = (node.get("type") or "any").lower()
        out = node.get("out") or "VOICE_TEXT"
        wait_ms = int(node.get("wait","0"))
        text, typ = "", ""
        if self.voice is None:
            self.variables[out] = text; self.variables[out+"_type"] = typ
            self._sleep_ms_interruptible(wait_ms)
            self.logger.info(f"VOICE_EVENT -> {out}='{text}' type='{typ}'")
            return

        deadline = time.time() + (wait_ms/1000.0) if wait_ms else None
        # Prefer generic get_event(timeout_ms) if VoiceDaemon exposes it
        if hasattr(self.voice, "get_event"):
            while True:
                self._pause_gate()
                if self.skip_wait:
                    self.skip_wait=False
                    self.logger.info("VOICE_EVENT interrupted by Ctrl+N")
                    break
                evt = self.voice.get_event(timeout_ms=200)
                if evt:
                    et = getattr(evt, "type", "") or ""
                    if want in ("any", et):
                        text = getattr(evt, "text","") or ""
                        typ = et
                        break
                if deadline and time.time()>deadline: break
        else:
            while True:
                self._pause_gate()
                if self.skip_wait:
                    self.skip_wait=False
                    self.logger.info("VOICE_EVENT interrupted by Ctrl+N")
                    break
                evt = None
                if want in ("any","command") and hasattr(self.voice, "get_next_command"):
                    evt = self.voice.get_next_command(timeout_ms=0)
                    if evt: text, typ = evt.text, "command"; break
                if want in ("any","query") and hasattr(self.voice, "get_next_query"):
                    evt = self.voice.get_next_query(timeout_ms=0)
                    if evt: text, typ = evt.text, "query"; break
                if deadline and time.time()>deadline: break
                time.sleep(0.05)

        self.variables[out] = text
        self.variables[out+"_type"] = typ
        self.logger.info(f"VOICE_EVENT -> {out}='{text}' type='{typ}'")

    def handle_voice_poll(self, node: ET.Element):
        self._ensure_voice()
        out_cmd = node.get("out_cmd") or "VOICE_CMD"
        out_query = node.get("out_query") or "VOICE_QUERY"
        cmd, query = "", ""
        if self.voice:
            if hasattr(self.voice, "get_next_command"):
                evt_cmd = self.voice.get_next_command(timeout_ms=0)
                if evt_cmd:
                    cmd = evt_cmd.text
                    if getattr(evt_cmd, "payload", None) and "seconds" in evt_cmd.payload:
                        self.variables[out_cmd+"_seconds"] = evt_cmd.payload["seconds"]
            if hasattr(self.voice, "get_next_query"):
                evt_query = self.voice.get_next_query(timeout_ms=0)
                if evt_query: query = evt_query.text
        self.variables[out_cmd] = cmd
        self.variables[out_query] = query
        self.logger.info(f"VOICE_POLL -> {out_cmd}='{cmd}' {out_query}='{query}'")

    # ---- XML ----
    def _load_xml(self):
        txt = self.xml_path.read_text(encoding="utf-8")
        self.tree = ET.fromstring(txt.encode("utf-8"))
        for f in self.tree.findall(".//func"):
            name = f.get("name")
            if name: self.functions[name]=f
        self.logger.info("XML loaded OK")

    # ---- handlers ----
    def handle_set(self, node: ET.Element):
        for k,v in node.attrib.items():
            if k in ("delay_fixed","delay_ms"): continue
            s = _substitute_vars(v, self.variables)
            try: val = _safe_eval(s, self.variables)
            except Exception: val = s
            self.variables[k]=val
            self.logger.info(f"SET {k} = {val}")

    def handle_wait(self, node: ET.Element):
        ms = int(float(node.get("ms","0")))
        self.logger.info(f"WAIT {ms}ms (pause=Ctrl+Space, skip=Ctrl+N)")
        self._sleep_ms_interruptible(ms)

    def handle_shell(self, node: ET.Element):
        cmd = _substitute_vars(node.get("cmd",""), self.variables)
        self.logger.info(f"SHELL: {cmd}")
        try: subprocess.call(cmd, shell=True)
        except Exception as e: self.logger.info(f"shell error: {e}")

    def handle_hotkey(self, node: ET.Element):
        hk = _substitute_vars(node.get("hotkey",""), self.variables)
        self.logger.info(f"HOTKEY {hk}")
        _hotkey(hk)

    def handle_type(self, node: ET.Element):
        mode = node.get("mode","type")
        text = _substitute_vars(node.get("text",""), self.variables)
        self.logger.info(f"TYPE mode={mode} text='{text[:30]}'")
        _type_text(text, mode=mode)

    def handle_click(self, node: ET.Element):
        btn = node.get("button","left")
        area = node.get("area")
        if area:
            expr = _substitute_vars(area, self.variables)
            parts = [p.strip() for p in expr.split(",")]
            if len(parts)!=4:
                self.logger.info("click area must be 'x1,y1,x2,y2'"); return
            try:
                vals = [int(float(_safe_eval(p, self.variables))) for p in parts]
            except Exception:
                vals = [int(float(p)) for p in parts]
            x1,y1,x2,y2 = vals
            rx = random.randint(min(x1,x2), max(x1,x2))
            ry = random.randint(min(y1,y2), max(y1,y2))
            self.logger.info(f"CLICK area={vals} -> ({rx},{ry})")
            _click_xy(rx, ry, button=btn)
        else:
            xs = _substitute_vars(node.get("x","0"), self.variables)
            ys = _substitute_vars(node.get("y","0"), self.variables)
            try:
                x = int(float(_safe_eval(xs, self.variables)))
                y = int(float(_safe_eval(ys, self.variables)))
            except Exception:
                x = int(float(xs)); y = int(float(ys))
            self.logger.info(f"CLICK ({x},{y})")
            _click_xy(x,y,button=btn)

    def handle_focus(self, node: ET.Element):
        title = node.get("title") or node.get("title_contains") or ""
        retries = int(node.get("retries","20")); interval_ms=int(node.get("interval_ms","200"))
        if not gw:
            self.logger.info("FOCUS skipped: pygetwindow not available"); return
        ok=False
        for _ in range(retries):
            try:
                for w in gw.getAllWindows():
                    if title.lower() in (w.title or "").lower():
                        try: w.minimize(); w.restore()
                        except Exception: pass
                        try: w.activate(); ok=True; break
                        except Exception:
                            try: w.maximize(); w.restore(); w.activate(); ok=True; break
                            except Exception: pass
                if ok: break
                time.sleep(interval_ms/1000.0)
            except Exception:
                time.sleep(interval_ms/1000.0)
        self.logger.info(f"FOCUS title~='{title}' -> {ok}")

    def handle_if(self, node: ET.Element):
        cond_raw = node.get("cond","")
        cond = _substitute_vars(cond_raw, self.variables)
        try: res = bool(eval(cond or "False", {"__builtins__": {}}, {}))
        except Exception as e:
            self.logger.info(f"IF eval error: {e}"); res=False
        children=list(node)
        if res:
            for sub in children:
                if isinstance(getattr(sub, "tag", None), str) and sub.tag.lower()=="else": break
                self._exec_node(sub)
        else:
            hit=False
            for sub in children:
                if isinstance(getattr(sub, "tag", None), str) and sub.tag.lower()=="else":
                    hit=True; continue
                if hit: self._exec_node(sub)

    def handle_repeat(self, node: ET.Element):
        expr = node.get("times","0")
        try: times = int(float(_safe_eval(_substitute_vars(expr, self.variables), self.variables)))
        except Exception: times = 0
        self.logger.info(f"REPEAT times={times}")
        for _ in range(times):
            for ch in list(node): self._exec_node(ch)

    def handle_func(self, node: ET.Element): pass

    def handle_call(self, node: ET.Element):
        name = node.get("name","")
        f = self.functions.get(name)
        if not f:
            self.logger.info(f"CALL missing func {name}"); return
        for k,v in node.attrib.items():
            if k.startswith("arg"): self.variables[k]=_substitute_vars(v, self.variables)
        self.logger.info(f"CALL {name}")
        for ch in list(f): self._exec_node(ch)

    def handle_foreach(self, node: ET.Element):
        list_name = node.get("list","")
        func_name = node.get("do","")
        if func_name not in self.functions:
            self.logger.info(f"FOREACH unknown func: {func_name}"); return
        data = self.variables.get(list_name, [])
        if isinstance(data, str):
            items = [s for s in re.split(r"[\r\n]+", data) if s.strip()]
        else:
            items = list(data)
        if str(node.get("random_shuffle","0")).lower() in ("1","true","yes"):
            random.shuffle(items)
        for idx, item in enumerate(items):
            self.variables["item"] = item
            self.variables["index"] = idx
            self.variables["arg0"] = item
            f = self.functions[func_name]
            for ch in list(f): self._exec_node(ch)
        self.variables.pop("item", None)
        self.variables.pop("index", None)
        self.variables.pop("arg0", None)

    def handle_extnode(self, node: ET.Element):
        mod_name = node.get("module"); cls_name = node.get("class"); method = node.get("method")
        out_var = node.get("output_var")
        if not mod_name or not method:
            self.logger.info("<extnode> requires module and method"); return
        mod = self._extmodule_cache.get(mod_name)
        if mod is None:
            mod = importlib.import_module(mod_name); self._extmodule_cache[mod_name]=mod
        if cls_name:
            key=(mod_name, cls_name)
            inst = self._extclass_cache.get(key)
            if inst is None:
                cls = getattr(mod, cls_name); inst = cls(); self._extclass_cache[key]=inst
            call_target = getattr(inst, method)
        else:
            call_target = getattr(mod, method)
        kw: Dict[str, Any] = {}
        for k,v in node.attrib.items():
            if k in {"module","class","method","output_var"}: continue
            vv = _substitute_vars(v, self.variables)
            if k.endswith("_list") or k in {"disciplines","subtopics"}:
                kw[k] = [p.strip() for p in vv.split(",") if p.strip()]
            else:
                kw[k] = _smart_cast(vv)
        try:
            res = call_target(**kw) if kw else call_target()
        except TypeError:
            res = call_target()
        if out_var: self.variables[out_var] = "" if res is None else res
        self.logger.info(f"EXTNODE {mod_name}.{cls_name+'.' if cls_name else ''}{method} -> {out_var}")

    # ---- dispatcher ----
    def _exec_node(self, node):
        tag = getattr(node, "tag", None)
        if not isinstance(tag, str):
            return  # skip comments/PI
        self._pause_gate()
        tagl = tag.lower()
        if   tagl=="set": self.handle_set(node)
        elif tagl=="wait": self.handle_wait(node)
        elif tagl=="shell": self.handle_shell(node)
        elif tagl=="hotkey": self.handle_hotkey(node)
        elif tagl=="type": self.handle_type(node)
        elif tagl=="click": self.handle_click(node)
        elif tagl=="focus": self.handle_focus(node)
        elif tagl=="if": self.handle_if(node)
        elif tagl=="repeat": self.handle_repeat(node)
        elif tagl=="func": self.handle_func(node)
        elif tagl=="call": self.handle_call(node)
        elif tagl=="foreach": self.handle_foreach(node)
        elif tagl=="extnode": self.handle_extnode(node)
        elif tagl=="voice_event": self.handle_voice_event(node)
        elif tagl=="voice_poll": self.handle_voice_poll(node)
        else:
            for ch in list(node): self._exec_node(ch)

    def run(self):
        self.logger.info("RUN start")
        for node in list(self.tree):
            if not isinstance(getattr(node, "tag", None), str): 
                continue
            if node.tag.lower()=="func": continue
            self._exec_node(node)
        self.logger.info("RUN end")

# Entrypoint
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("xml_path")
    args=ap.parse_args()
    XMLProgram(Path(args.xml_path)).run()
