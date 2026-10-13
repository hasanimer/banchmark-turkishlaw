"""Ajanın son mesajındaki JSON bloğunu sağlam biçimde ayrıştırır."""

from __future__ import annotations

import json
import re
from typing import Any

_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S | re.I)
_CHOICE_PATTERNS = [
    re.compile(r'"choice"\s*:\s*"([A-E])"', re.I),
    re.compile(r"(?:doğru\s+(?:cevap|şık|seçenek)|cevap|yanıt)\s*(?:is|:|=|olarak)?\s*\(?\**([A-E])\)?\b", re.I),
    re.compile(r"^\s*\**([A-E])\)\s", re.M),
]


def _balanced_objects(text: str) -> list[str]:
    """Metindeki dengeli en dış {...} parçalarını sırayla döndürür."""
    out, depth, start, in_str, esc = [], 0, -1, False, False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"' and depth > 0:
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start >= 0:
                out.append(text[start : i + 1])
    return out


def extract_json(text: str) -> dict[str, Any] | None:
    candidates = [m.group(1) for m in _FENCE_RE.finditer(text or "")]
    candidates += _balanced_objects(text or "")
    for raw in reversed(candidates):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


def normalize_choice(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    m = re.search(r"\b([A-Ea-e])\b", value.strip()) or re.match(r"^\s*([A-Ea-e])", value.strip())
    return m.group(1).upper() if m else None


def parse_final_json(text: str, track: str) -> dict[str, Any]:
    data = extract_json(text) or {}
    parsed: dict[str, Any] = {"json_ok": bool(data), **data}
    if track == "exam":
        choice = normalize_choice(data.get("choice")) if data else None
        if choice is None:
            for pat in _CHOICE_PATTERNS:
                found = pat.findall(text or "")
                if found:
                    choice = found[-1].upper()
                    break
        parsed["choice"] = choice
    return parsed
