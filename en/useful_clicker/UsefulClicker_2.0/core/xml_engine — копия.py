
from __future__ import annotations
import os, sys, time, random, subprocess, re
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from lxml import etree as ET
except Exception:
    import xml.etree.ElementTree as ET

from core.logger import setup_logger
from core.safe_eval import SafeEval
from input.mouse_keyboard import click_xy, click_area, type_text, hotkey, keysequence, screenshot_pil
from core.image_hash import phash_hex_simple, hamming_distance_hex, rect_candidates_from_edges, cv_to_pil, pil_to_cv
from core.ocr import find_text_box
try:
    import pygetwindow as gw
except Exception:
    gw = None

def _rand_delay(delay_ms: Optional[int]) -> float: return (delay_ms or 0)/1000.0 * random.random()
def _fixed_delay(delay_fixed: Optional[int]) -> float: return (delay_fixed or 0)/1000.0
def _substitute_vars(value: str, variables: Dict[str, Any]) -> str:
    def repl(m): return str(variables.get(m.group(1), ""))
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, value)

class XMLProgram:
    def __init__(self, xml_path: Path, debug: bool = False, log_path: Optional[Path] = None):
        self.xml_path = Path(xml_path); self.debug = debug
        self.logger = setup_logger(log_path)
        self.variables: Dict[str, Any] = {}; self.functions: Dict[str, ET.Element] = {}
        self.debug_window = None; self.xml_text = ""
        self._load_xml()

    def _load_xml(self):
        text = Path(self.xml_path).read_text(encoding="utf-8")
        root_dir = self.xml_path.parent
        includes = re.findall(r"<include>\s*(.*?)\s*</include>", text, flags=re.I)
        combined=[text]
        for inc in includes:
            inc_path = (root_dir / inc.strip()).resolve()
            if inc_path.exists():
                self.logger.info(f"Including: {inc_path}")
                combined.append(inc_path.read_text(encoding="utf-8"))
        self.xml_text = "\n".join(combined)
        self.tree = ET.fromstring(self.xml_text.encode("utf-8")) if hasattr(ET, "fromstring") else ET.parse(str(self.xml_path)).getroot()
        for func in self.tree.findall(".//func"):
            name = func.get("name")
            if name: self.functions[name] = func
        if self.debug:
            try:
                from gui.debugger import DebugWindow
                self.debug_window = DebugWindow(); self.debug_window.set_code(self.xml_text)
            except Exception:
                self.debug_window = None

    def _delays(self, node: ET.Element):
        df=node.get("delay_fixed"); dm=node.get("delay_ms")
        if df: time.sleep(_fixed_delay(int(df)))
        if dm: time.sleep(_rand_delay(int(dm)))

    def _highlight_node(self, node: ET.Element):
        if not self.debug_window: return
        if not isinstance(getattr(node, 'tag', None), str): return
        from gui.debugger import DebugWindow  # will no-op if missing
        tag = node.tag; attribs = " ".join(f'{k}="{v}"' for k,v in node.attrib.items())
        snippet = f"<{tag}" + (f" {attribs}" if attribs else "")
        start = self.xml_text.find(snippet); end = start + len(snippet)
        if start >= 0:
            self.debug_window.highlight_range(start, end); self.debug_window.pulse()

    def _set_var(self, name: str, value: Any):
        self.logger.info(f"SET {name} = {value}"); self.variables[name] = value

    # Handlers
    def handle_set(self, node: ET.Element):
        for k,v in list(node.attrib.items()):
            if k in ("delay_fixed","delay_ms"): continue
            expr = _substitute_vars(v, self.variables)
            try: val = SafeEval(self.variables).eval(expr)
            except Exception: val = expr
            self._set_var(k, val)
        self._delays(node)

    def handle_check(self, node: ET.Element):
        tol = float(node.get("tol")) if node.get("tol") else None
        for k,v in list(node.attrib.items()):
            if k in ("delay_fixed","delay_ms","tol","comment"): continue
            expected_raw = _substitute_vars(v, self.variables); actual = self.variables.get(k)
            if tol is not None:
                try:
                    exp = float(SafeEval(self.variables).eval(expected_raw)); act = float(actual)
                    ok = abs(exp - act) <= tol
                except Exception: ok = False
            else:
                ok = str(actual) == expected_raw
            self.logger.info(f"CHECK {k}: actual={actual} expected={expected_raw} tol={tol} -> {ok}")
            if not ok: raise AssertionError(f"Check failed for {k}: actual={actual}, expected={expected_raw}")
        self._delays(node)

    def handle_type(self, node: ET.Element):
        mode = node.get("mode","type"); text = _substitute_vars(node.get("text",""), self.variables)
        self.logger.info(f"TYPE mode={mode} text='{text[:40]}...'"); type_text(text, mode=mode); self._delays(node)

    def handle_click(self, node: ET.Element):
        button = node.get("button","left"); area = node.get("area")
        if area:
            parts = [int(p.strip()) for p in area.split(",")]; 
            if len(parts)!=4: raise ValueError("area must be 'x1,y1,x2,y2'")
            click_area(tuple(parts), button=button)
        else:
            x = int(node.get("x")); y = int(node.get("y")); click_xy(x,y,button=button)
        self._delays(node)

    def handle_hotkey(self, node: ET.Element):
        combo = node.get("hotkey"); seq = node.get("keysequence"); d_ms = int(node.get("delay_ms") or "0") or None
        if combo: self.logger.info(f"HOTKEY {combo}"); hotkey(combo, delay_ms=d_ms)
        elif seq: self.logger.info(f"KEYSEQUENCE '{seq}'"); keysequence(seq, delay_ms=d_ms)
        else: raise ValueError("hotkey requires 'hotkey' or 'keysequence'")
        df = node.get("delay_fixed"); 
        if df: time.sleep(int(df)/1000.0)

    def handle_shell(self, node: ET.Element):
        cmd = node.get("cmd") or node.text or ""; shell_type = node.get("shell_type","cmd")
        bg = node.get("bg","0") == "1"; output_var = node.get("output_var"); output_format = node.get("output_format","text"); separator = node.get("separator"," ")
        if not cmd.strip(): return
        self.logger.info(f"SHELL type={shell_type} bg={bg} cmd={cmd}")
        startupinfo=None
        if bg and os.name=="nt":
            startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if shell_type == "powershell": full_cmd = ["powershell","-NoProfile","-Command", cmd]
        elif shell_type == "bash": full_cmd = ["bash","-lc", cmd]
        else: full_cmd = cmd
        if bg:
            if isinstance(full_cmd, list):
                subprocess.Popen(full_cmd, stdout=subprocess.PIPE if output_var else None, stderr=subprocess.PIPE if output_var else None, text=True, startupinfo=startupinfo)
            else:
                subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE if output_var else None, stderr=subprocess.PIPE if output_var else None, text=True, startupinfo=startupinfo)
            if output_var: self._set_var(output_var, "")
        else:
            if isinstance(full_cmd, list):
                proc = subprocess.run(full_cmd, capture_output=bool(output_var), text=True, startupinfo=startupinfo)
            else:
                proc = subprocess.run(full_cmd, shell=True, capture_output=bool(output_var), text=True, startupinfo=startupinfo)
            if output_var:
                out = proc.stdout or ""
                if output_format=="list": val=[s for s in out.strip().split(separator) if s]
                else: val=out
                self._set_var(output_var, val)
        self._delays(node)

    def handle_focus(self, node: ET.Element):
        title = node.get("title") or node.get("title_contains") or ""
        retries = int(node.get("retries","20")); interval_ms = int(node.get("interval_ms","200"))
        if not gw:
            self.logger.info("FOCUS skipped: pygetwindow not available"); return
        ok=False
        for _ in range(retries):
            wins = gw.getAllWindows()
            for w in wins:
                try:
                    if title.lower() in (w.title or "").lower():
                        try: w.minimize(); w.restore()
                        except Exception: pass
                        try: w.activate(); ok=True; break
                        except Exception:
                            try: w.maximize(); w.restore(); w.activate(); ok=True; break
                            except Exception: pass
                except Exception: continue
            if ok: break
            time.sleep(interval_ms/1000.0)
        self.logger.info(f"FOCUS title~='{title}' -> {ok}")
        self._delays(node)

    def handle_clickimg(self, node: ET.Element):
        """
        <clickimg hash="0xDEADBEEF..." button="left"/>
        Алгоритм:
          1) получаем кандидаты через preprocess.detect_words() (он же сохраняет screenshot.png),
          2) для каждого прямоугольника обрезаем ROI из screenshot.png,
          3) считаем хеш через hash_image.hash_image(roi),
          4) при точном совпадении кликаем в центр прямоугольника.
        """
        target_hash = (node.get("hash") or node.get("target_hash") or "").strip()
        if not target_hash:
            self.logger.info("CLICKIMG: no 'hash' provided")
            self._delays(node)
            return

        # Импорты ваших модулей
        try:
            from gui.preprocess import detect_words
            from gui.hash_image import hash_image
            import cv2
        except Exception as e:
            self.logger.info(f"CLICKIMG import error: {e}")
            self._delays(node)
            return

        # 1) кандидаты + скрин
        try:
            rects = detect_words()  # ДОЛЖЕН сохранить 'screenshot.png' в текущей директории
        except Exception as e:
            self.logger.info(f"CLICKIMG detect_words() failed: {e}")
            self._delays(node)
            return

        img = cv2.imread("screenshot.png")
        if img is None:
            # fallback: свежий скрин, если по какой-то причине файл не появился
            try:
                from gui.screenshot import take_screenshot  # простой шима на pyautogui
                img = take_screenshot()
            except Exception as e:
                self.logger.info(f"CLICKIMG: no screenshot available: {e}")
                self._delays(node)
                return

        button = node.get("button", "left")
        matched = False

        for (x, y, w, h) in rects:
            x2 = x + max(1, w)
            y2 = y + max(1, h)
            roi = img[y:y2, x:x2]
            if roi.size == 0:
                continue

            try:
                roi_hash = str(hash_image(roi)).strip()
            except Exception as e:
                self.logger.info(f"CLICKIMG hash error: {e}")
                continue

            # Сравниваем СТРОГО (как в вашей GUI/хеш-логике)
            if roi_hash.lower() == target_hash.lower():
                cx = x + w // 2
                cy = y + h // 2
                self.logger.info(f"CLICKIMG match -> rect={(x,y,w,h)}, click={button}")
                from input.mouse_keyboard import click_xy
                click_xy(cx, cy, button=button)
                matched = True
                break

        if not matched:
            self.logger.info("CLICKIMG: no exact hash match among detected regions")

        self._delays(node)


    def handle_clicktext(self, node: ET.Element):
        query = node.get("text",""); lang = node.get("lang","eng")
        cs = node.get("case_sensitive","0") == "1"; partial = node.get("partial","0") == "1"
        area = node.get("area"); a_tuple=None
        if area:
            parts = [int(p.strip()) for p in area.split(",")]
            if len(parts)==4: a_tuple=tuple(parts)
        shot = screenshot_pil()
        box = find_text_box(shot, query, lang=lang, case_sensitive=cs, partial=partial, area=a_tuple)
        if box:
            x,y,w,h = box; cx = x + w//2; cy = y + h//2
            self.logger.info(f"CLICKTEXT '{query}' -> {(x,y,w,h)}")
            click_xy(cx, cy, button=node.get("button","left"))
        else:
            self.logger.info(f"CLICKTEXT not found: '{query}'")
        self._delays(node)

    def handle_func(self, node: ET.Element): pass
    def handle_call(self, node: ET.Element):
        name = node.get("name")
        if not name or name not in self.functions: raise ValueError(f"Unknown function: {name}")
        for idx,(k,v) in enumerate(node.attrib.items()):
            if k.startswith("arg"): self.variables[f"arg{idx}"] = v
        self.logger.info(f"CALL {name}"); func=self.functions[name]
        for child in list(func): self._exec_node(child)
        self._delays(node)

    def handle_wait(self, node: ET.Element):
        ms = int(node.get("ms","0")); self.logger.info(f"WAIT {ms}ms"); time.sleep(ms/1000.0)

    def _exec_node(self, node: ET.Element):
        if self.debug_window: self._highlight_node(node)
        tag = node.tag if isinstance(getattr(node, 'tag', None), str) else ""
        tag = tag.lower()
        if tag == "set": self.handle_set(node)
        elif tag == "check": self.handle_check(node)
        elif tag == "type": self.handle_type(node)
        elif tag == "click": self.handle_click(node)
        elif tag == "hotkey": self.handle_hotkey(node)
        elif tag == "shell": self.handle_shell(node)
        elif tag == "func": self.handle_func(node)
        elif tag == "call": self.handle_call(node)
        elif tag == "wait": self.handle_wait(node)
        elif tag == "focus": self.handle_focus(node)
        elif tag == "clickimg": self.handle_clickimg(node)
        elif tag == "clicktext": self.handle_clicktext(node)
        else:
            if tag in ("llmcall","foreach","gen","if","else","math","code","py_call"):
                self.logger.info(f"[STUB not implemented in Stage 2] <{tag}>")
            elif tag == "": pass
            else: raise ValueError(f"Unsupported tag: <{node.tag}>")

    def run(self):
        for node in list(self.tree):
            tag = node.tag if isinstance(getattr(node, 'tag', None), str) else ""
            if tag.lower()=="func": continue
            if tag=="": continue
            self._exec_node(node)
