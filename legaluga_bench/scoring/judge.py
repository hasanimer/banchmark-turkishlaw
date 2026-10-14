"""Kör LLM hakemi: açık uçlu araştırma cevaplarını rubriğe göre puanlar.

Körleme: hakeme sistem adı verilmez; cevap metnindeki sistem/araç adları
`[SİSTEM]` ile maskelenir. Hakem modeli bütün sistemler için aynıdır.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import anthropic

# Hakem modeli koda gömülmez; LBENCH_JUDGE_MODEL ortam değişkeni ya da --judge-model bayrağıyla verilir.
JUDGE_MODEL_ENV = "LBENCH_JUDGE_MODEL"

# Cevaplarda sistemi ele verebilecek adlar. Resmî kaynak adları (Bedesten, UYAP,
# mevzuat.gov.tr) maskelenmez; bunlar kaynağın kendisidir.
SYSTEM_NAME_PATTERNS = [
    r"legaluga\w*", r"yarg[ıi]\s*mcp", r"yarg[ıi]\s*pro", r"legal\s*data\s*hunter", r"\bldh\b",
    r"mevzuat\s*mcp", r"\bmcp\b", r"semantik_ictihat_ara", r"karar_ara", r"karar_getir",
    r"kunye_dogrula", r"search_cases_v1", r"get_case_v1", r"web_search",
]
_MASK_RE = re.compile("|".join(SYSTEM_NAME_PATTERNS), re.I)


def blind(text: str) -> str:
    return _MASK_RE.sub("[SİSTEM]", text or "")


JUDGE_SYSTEM = """Sen Türk hukuku alanında deneyimli, tarafsız bir sınav değerlendiricisisin.
Bir hukuki soruya verilmiş cevabı, verilen değerlendirme ölçütlerine (rubrik) göre puanlayacaksın.
- Yalnız cevabın hukuki içeriğini değerlendir; üslubu, uzunluğu ya da hangi araçla üretildiğini dikkate alma.
- Her ölçüt için 0 (karşılanmadı), 0.5 (kısmen) ya da 1 (tam) ver ve kısa gerekçe yaz.
- Cevapta açıkça yanlış bir hukuki iddia varsa 'kritik_hata' alanına yaz.
- Künyelerin gerçekliğini sen denetleme; bu ayrıca otomatik yapılıyor."""

JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "score": {"type": "number", "enum": [0, 0.5, 1]},
                    "reason": {"type": "string"},
                },
                "required": ["index", "score", "reason"],
                "additionalProperties": False,
            },
        },
        "kritik_hata": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["criteria", "kritik_hata"],
    "additionalProperties": False,
}


def render_judge_prompt(question: str, rubric: list[dict[str, Any]], answer: str, reference: str | None) -> str:
    lines = [f"{i}. ({r.get('weight', 1)} puan) {r['point']}" for i, r in enumerate(rubric, 1)]
    ref = f"\n\nReferans cevap (yalnız yol gösterici):\n{reference}" if reference else ""
    return (
        f"Soru:\n{question}\n\nDeğerlendirme ölçütleri:\n" + "\n".join(lines) + ref +
        f"\n\nDeğerlendirilecek cevap:\n<<<\n{blind(answer)}\n>>>"
    )


def weighted_score(rubric: list[dict[str, Any]], criteria: list[dict[str, Any]]) -> float:
    weights = {i: float(r.get("weight", 1)) for i, r in enumerate(rubric, 1)}
    total = sum(weights.values()) or 1.0
    got = sum(weights.get(int(c["index"]), 0.0) * float(c["score"]) for c in criteria)
    return round(got / total, 4)


def external_judge(judgments: dict[tuple[str, str], dict[str, Any]], task_id: str, system_id: str):
    """Harici (ör. ayrı bir hakem oturumunda) verilmiş kararları judge_fn arayüzüyle döndürür."""

    async def judge_fn(question: str, rubric: list[dict[str, Any]], answer: str, reference: str | None) -> dict[str, Any]:
        j = judgments.get((task_id, system_id))
        if j is None:
            return {"error": "harici hakem kararı yok", "score": 0.0, "criteria": [], "kritik_hata": []}
        return {**j, "score": weighted_score(rubric, j.get("criteria", [])), "judge_model": j.get("judge_model", "external")}

    return judge_fn


async def judge_answer(
    client: anthropic.AsyncAnthropic,
    question: str,
    rubric: list[dict[str, Any]],
    answer: str,
    reference: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    model = model or os.environ.get(JUDGE_MODEL_ENV, "")
    if not model:
        raise ValueError(f"Hakem modeli belirtilmedi: {JUDGE_MODEL_ENV} ya da --judge-model")
    response = await client.messages.create(
        model=model,
        max_tokens=8000,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": render_judge_prompt(question, rubric, answer, reference)}],
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
    )
    if response.stop_reason == "refusal":
        return {"error": "hakem reddetti", "score": 0.0, "criteria": [], "kritik_hata": []}
    text = next((b.text for b in response.content if getattr(b, "type", None) == "text"), "{}")
    data = json.loads(text)
    data["score"] = weighted_score(rubric, data.get("criteria", []))
    data["judge_model"] = model
    return data
