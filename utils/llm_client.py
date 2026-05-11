import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def call_llm(
    system_prompt: str,
    messages: list,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1500,
    expect_json: bool = False,
) -> str:
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=max_tokens,
    )

    text = response.choices[0].message.content.strip()

    if expect_json:
        text = _clean_json(text)

    return text


def _clean_json(text: str) -> str:
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def parse_json_response(text: str) -> dict | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[LLM Client] JSON parse error: {e}")
        print(f"[LLM Client] Raw text: {text[:300]}")
        return None