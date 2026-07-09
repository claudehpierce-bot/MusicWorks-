"""Base Claude API caller used by all agents."""
import json
import re
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

_client = None


def format_brief_section(brief: dict | None, fields: list[str]) -> str:
    """Renders the subset of Live Creative Brief fields a given department
    actually consumes (per execution/brief_dependencies.py) as a labeled
    prompt block. Every department reads from the SAME Brief -- this is the
    one shared formatter every agent calls, so no agent ever forms its own
    independent interpretation of a field's meaning (V7 Constitution,
    Amendment I, Principle 1). Returns "" when no brief is available yet,
    so existing callers that don't pass one see no behavior change."""
    if not brief:
        return ""
    from execution.brief_store import FIELD_LABELS

    lines = []
    for field in fields:
        value = (brief.get(field) or "").strip()
        if value:
            lines.append(f"- {FIELD_LABELS.get(field, field)}: {value}")
    if not lines:
        return ""
    return "LIVE CREATIVE BRIEF (the single source of creative truth for this campaign -- follow it, don't reinterpret it):\n" + "\n".join(lines)


def get_client() -> Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise EnvironmentError(
                "\n\nANTHROPIC_API_KEY not found.\n"
                "  1. Copy .env.example to .env\n"
                "  2. Add your Anthropic API key\n"
                "  Get one at: https://console.anthropic.com\n"
            )
        _client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def call_claude(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    brand_context: str = "",
) -> dict:
    """
    Make a Claude API call and return parsed JSON.
    brand_context, when provided, is prepended to the system prompt so every
    agent knows who the artist is before it reads its task instructions.
    """
    client = get_client()
    full_system = f"{brand_context}\n\n{system_prompt}" if brand_context else system_prompt

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=full_system,
        messages=[{"role": "user", "content": user_message}],
    )

    text = response.content[0].text.strip()

    # Primary: try parsing the whole response as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract the first {...} block (Claude sometimes adds a preamble)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last resort: return raw text so the asset is still stored, just not structured
    return {"raw_text": text, "parse_error": True}
