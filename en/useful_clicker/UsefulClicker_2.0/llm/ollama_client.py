"""
ollama_client.py

Client for Ollama LLM via subprocess ('ollama generate').
"""
import os
import subprocess
import logging

log = logging.getLogger("usefulclicker.llm")

class OllamaClient:
    """
    LLM client that calls 'ollama generate' for text and list outputs.
    """
    def __init__(self):
        # Default model for Ollama
        self.model = os.getenv("USEFULCLICKER_OLLAMA_MODEL", "llama3.2:latest")
        log.info(f"Ollama client ready (model={self.model}).")

    def generate_text(self, prompt: str, model: str | None = None, temperature: float | None = None) -> str:
        """
        Generate text using Ollama CLI. Sends prompt as stdin.
        """
        use_model = model or self.model
        cmd = ["ollama", "generate", use_model]
        if temperature is not None:
            cmd.extend(["--temperature", str(temperature)])
        # Call ollama CLI
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            log.info(f"Ollama generate error: {proc.stderr.strip()}")
            raise RuntimeError(f"Ollama generate failed ({proc.returncode})")
        text = proc.stdout.strip()
        log.info(f"Ollama OK ({len(text)} chars).")
        return text

    def generate_list(
        self,
        prompt: str,
        separator: str = "\n",
        model: str | None = None,
        temperature: float | None = None,
    ) -> list[str]:
        """
        Generate a list by splitting the generated text on the separator.
        """
        text = self.generate_text(prompt, model=model, temperature=temperature)
        items = [s.strip() for s in text.split(separator) if s.strip()]
        log.info(f"Ollama split -> {len(items)} items")
        return items