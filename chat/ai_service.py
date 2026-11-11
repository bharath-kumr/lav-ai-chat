"""Gemini via plain REST (standard library only - no pydantic / compiled packages)."""

import asyncio
import datetime
import json
import urllib.error
import urllib.request

from django.conf import settings

LAV_SYSTEM_PROMPT = """You are Lav, a friendly AI dev companion built by Bharath, a Python/Django
full-stack developer. Your personality:

- Warm, casual, encouraging - talk like a helpful friend, not a corporate assistant.
- Especially good at explaining code, decoding error messages/tracebacks, and helping with
  Python/Django/JavaScript questions - but you can chat about anything.
- When a question is vague or missing key details (especially debugging), ask ONE short
  clarifying question (1-2 sentences) before giving a full answer.
- When the user pastes an error/traceback, identify the error type, the likely cause, and a
  concrete fix - don't just restate the error.
- Keep replies concise by default. Expand only when asked.
- Light humor is fine, but not during serious debugging help.
- Put code inside fenced code blocks.
"""

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def build_contents(messages, new_message):
    contents = []
    for m in messages:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})
    while contents and contents[0]["role"] != "user":  # Gemini must start with a user turn
        contents.pop(0)
    contents.append({"role": "user", "parts": [{"text": new_message}]})
    return contents


def _stream_blocking(contents, put):
    """Runs in a worker thread. Calls put(text) for every streamed piece."""
    base = getattr(settings, "GEMINI_BASE_URL", BASE_URL)
    url = f"{base}/models/{settings.GEMINI_MODEL}:streamGenerateContent?alt=sse"

    today = datetime.date.today().strftime("%A, %d %B %Y")
    system_text = (
        f"{LAV_SYSTEM_PROMPT}\nToday's date is {today}. "
        "For anything recent, use search results and never assume it is 2025."
    )
    payload = {"system_instruction": {"parts": [{"text": system_text}]}, "contents": contents}
    if getattr(settings, "GEMINI_SEARCH", True):
        payload["tools"] = [{"google_search": {}}]  # live Google Search for current info
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": settings.GEMINI_API_KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            for raw in resp:
                line = raw.decode("utf-8", "ignore").strip()
                if not line.startswith("data:"):
                    continue
                try:
                    data = json.loads(line[5:].strip())
                except ValueError:
                    continue
                for cand in data.get("candidates", []):
                    for part in cand.get("content", {}).get("parts", []):
                        if part.get("text"):
                            put(part["text"])
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode()).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        raise RuntimeError(f"Gemini API error {e.code}: {msg or e.reason}")


async def stream_lav_response(history_messages, new_message):
    """Async generator yielding text chunks from Gemini."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file and restart.")

    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()
    contents = build_contents(history_messages, new_message)

    def worker():
        try:
            _stream_blocking(contents, lambda t: loop.call_soon_threadsafe(queue.put_nowait, ("chunk", t)))
            loop.call_soon_threadsafe(queue.put_nowait, ("end", None))
        except Exception as exc:
            loop.call_soon_threadsafe(queue.put_nowait, ("error", exc))

    loop.run_in_executor(None, worker)

    while True:
        kind, value = await queue.get()
        if kind == "chunk":
            yield value
        elif kind == "error":
            raise value
        else:
            return