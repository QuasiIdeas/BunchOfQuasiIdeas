# voice/voice_daemon.py
import queue, threading, time, re
from dataclasses import dataclass
from typing import Optional, Literal, Dict, Any

import numpy as np
import sounddevice as sd

# ---- optional deps ----
try:
    import webrtcvad
except Exception:
    webrtcvad = None

try:
    import whisper  # openai-whisper (local)
except Exception:
    whisper = None

# optional LLM (to condense free-form speech into a short YouTube query)
try:
    from llm.openai_client import LLMClient
except Exception:
    LLMClient = None


EventType = Literal["command", "query"]


@dataclass
class VoiceEvent:
    type: EventType
    text: str          # command name (for commands) OR query string (for queries)
    ts: float
    payload: Optional[Dict[str, Any]] = None  # e.g., {"seconds": 30} for seek


class VoiceDaemon:
    """
    Background daemon: mic -> ASR (Whisper) -> intent -> queues.
      commands: next/prev/pause/resume/seek_fwd/seek_back/scroll_down/scroll_up/fullscreen
      queries : user free speech distilled into a search string
    """

    def __init__(self,
                 model_name: str = "base",
                 sample_rate: int = 16000,
                 device: Optional[int] = None,
                 use_vad: bool = True,
                 lang: Optional[str] = None,         # "ru" / "en" / None (auto)
                 use_llm_for_queries: bool = True):
        self.sample_rate = sample_rate
        self.device = device
        self.use_vad = use_vad and (webrtcvad is not None)
        self.lang = lang
        self.use_llm_for_queries = use_llm_for_queries and (LLMClient is not None)

        self._audio_q: "queue.Queue[bytes]" = queue.Queue()
        self._stop = threading.Event()
        self._listen_thread: Optional[threading.Thread] = None
        self._proc_thread: Optional[threading.Thread] = None

        self.commands: "queue.Queue[VoiceEvent]" = queue.Queue()
        self.queries: "queue.Queue[VoiceEvent]" = queue.Queue()

        self._accum_frames: list[bytes] = []
        self._vad = webrtcvad.Vad(2) if self.use_vad else None
        self._model = whisper.load_model(model_name) if whisper is not None else None
        self._llm = LLMClient() if (self.use_llm_for_queries and LLMClient is not None) else None

        self._stream: Optional[sd.InputStream] = None

    # ----------------- public API -----------------
    def start(self):
        self._stop.clear()
        self._start_stream()
        self._listen_thread = threading.Thread(target=self._listen_audio_loop, daemon=True)
        self._proc_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._listen_thread.start()
        self._proc_thread.start()
        return self

    def stop(self):
        self._stop.set()
        try:
            if self._stream:
                self._stream.stop(); self._stream.close()
        except Exception:
            pass

    def get_next_command(self, timeout_ms: int = 0) -> Optional[VoiceEvent]:
        try:
            return self.commands.get(timeout=timeout_ms/1000.0 if timeout_ms else 0)
        except queue.Empty:
            return None

    def get_next_query(self, timeout_ms: int = 0) -> Optional[VoiceEvent]:
        try:
            return self.queries.get(timeout=timeout_ms/1000.0 if timeout_ms else 0)
        except queue.Empty:
            return None

    # ----------------- audio -----------------
    def _start_stream(self):
        def _cb(indata, frames, time_info, status):
            if status:
                # optionally log status
                pass
            mono = indata[:, 0]
            pcm16 = (mono * 32767).astype(np.int16).tobytes()
            self._audio_q.put(pcm16)

        self._stream = sd.InputStream(samplerate=self.sample_rate, channels=1,
                                      dtype="float32", device=self.device, callback=_cb)
        self._stream.start()

    def _listen_audio_loop(self):
        block_ms = 30
        bytes_per_ms = int(self.sample_rate * 2 / 1000)  # int16
        ring = bytearray()
        speaking = False
        last_voice_ts = time.time()
        max_silence_ms = 700

        while not self._stop.is_set():
            try:
                chunk = self._audio_q.get(timeout=0.1)
            except queue.Empty:
                chunk = None

            if chunk:
                ring.extend(chunk)
                while len(ring) >= bytes_per_ms * block_ms:
                    frame = ring[: bytes_per_ms * block_ms]
                    del ring[: bytes_per_ms * block_ms]

                    if self._vad:
                        is_speech = self._vad.is_speech(frame, self.sample_rate)
                    else:
                        # no VAD: treat as speech; close phrase by silence timeout in _process_loop
                        is_speech = True

                    if is_speech:
                        speaking = True
                        last_voice_ts = time.time()
                        self._accum_frames.append(frame)
                    else:
                        if speaking and (time.time() - last_voice_ts) * 1000 > max_silence_ms:
                            self._flush_phrase()
                            speaking = False
            else:
                if speaking and (time.time() - last_voice_ts) * 1000 > max_silence_ms:
                    self._flush_phrase()
                    speaking = False

    def _process_loop(self):
        # reserved in case you want extra background processing later
        while not self._stop.is_set():
            time.sleep(0.05)

    def _flush_phrase(self):
        if not self._accum_frames:
            return
        audio_bytes = b"".join(self._accum_frames)
        self._accum_frames.clear()
        self._on_phrase(audio_bytes)

    # ----------------- ASR + intent -----------------

    # numeric seconds (both langs)
    _RE_NUM = re.compile(r"(?P<num>\d{1,3})")

    # English & Russian command patterns
    # Order matters: put more specific patterns earlier.
    CMD_RULES = [
        # NEXT
        (r"^\s*(next|skip|play next|go next|следующ(ий|ая)|дальш(е|ий))\b", "next"),
        # PREV
        (r"^\s*(prev(ious)?|back|go back|назад|предыдущ(ий|ая))\b", "prev"),
        # PAUSE / RESUME / PLAY
        (r"\b(pause|стоп|пауза|останови(ть)?)\b", "pause"),
        (r"\b(resume|continue|play|продолж(ай|ить)|воспроизведи)\b", "resume"),
        # FULLSCREEN
        (r"\b(fullscreen|full screen|полноэкран|на весь экран|фуллскрин|f11)\b", "fullscreen"),
        # SCROLL
        (r"(scroll\s*down|scrol(l)? down|вниз|скролл вниз|листай вниз)", "scroll_down"),
        (r"(scroll\s*up|scrol(l)? up|вверх|скролл вверх|листай вверх)", "scroll_up"),
        # SEEK FORWARD / BACKWARD with optional number of seconds
        # ru: "промотай/перемотай вперёд 30 секунд", "вперёд 10", "на 15 сек вперед"
        # en: "seek forward 10 (seconds)", "forward 30", "skip forward 10"
        (r"(промот(ай|ать)|перемот(ай|ать)|перемотка|seek|skip).*(впер(е|ё)д|forward|\+\s*\d+|\b\+?\d+\b)", "seek_fwd"),
        (r"(промот(ай|ать)|перемот(ай|ать)|перемотка|seek|skip).*(назад|back|\-\s*\d+|\b\-?\d+\b)", "seek_back"),
        # Simple "forward 10 sec" / "назад 10 сек"
        (r"\b(forward|впер(е|ё)д)\b", "seek_fwd"),
        (r"\b(back|назад)\b", "seek_back"),
    ]

    def _extract_seconds(self, text: str, default_seconds: int = 10) -> int:
        """
        Extracts a number of seconds from the utterance. If absent, returns default_seconds.
        Supports both "10", "+10", "-10", "10 sec/seconds/сек/секунд/секунды".
        """
        m = self._RE_NUM.search(text)
        if m:
            try:
                n = int(m.group("num"))
                # reasonable clamp
                return max(1, min(n, 600))
            except Exception:
                pass
        return default_seconds

    def _on_phrase(self, audio_bytes: bytes):
        if self._model is None:
            return
        pcm16 = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        try:
            kwargs = dict(fp16=False)
            if self.lang:
                kwargs["language"] = self.lang  # "ru" / "en"; if None -> auto
            result = self._model.transcribe(pcm16, **kwargs)
            text = (result.get("text") or "").strip()
        except Exception:
            text = ""

        if not text:
            return

        evt = self._interpret(text)
        if evt:
            if evt.type == "command":
                self.commands.put(evt)
            else:
                self.queries.put(evt)

    def _interpret(self, text: str) -> Optional[VoiceEvent]:
        low = text.lower()

        # 1) commands (ru + en)
        for pat, name in self.CMD_RULES:
            if re.search(pat, low):
                payload = None
                if name in ("seek_fwd", "seek_back"):
                    seconds = self._extract_seconds(low, default_seconds=10)
                    payload = {"seconds": seconds}
                return VoiceEvent(type="command", text=name, ts=time.time(), payload=payload)

        # 2) otherwise: it's a search query → optionally condense with LLM
        query = text
        if self._llm is not None:
            try:
                resp = self._llm.generate_text(
                    "Сформулируй краткий поисковый запрос для YouTube по смыслу фразы: "
                    f"«{text}». Ответь одной строкой, без кавычек."
                )
                if isinstance(resp, str) and resp.strip():
                    query = resp.strip()
            except Exception:
                pass

        return VoiceEvent(type="query", text=query, ts=time.time())
