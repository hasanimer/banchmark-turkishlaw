"""Bütün sistemlerde birebir aynı kullanılan istemler.

Sistem istemi, hangi aracın hangi şirkete ait olduğunu söylemez; ajan yalnız
kendisine verilen araçları görür. Her track cevabın sonunda tek bir JSON bloğu
ister; puanlama bu bloğu okur.
"""

from __future__ import annotations

from ..schema import Task

SYSTEM_PROMPT = """Sen Türk hukukunda araştırma yapan titiz bir hukuk asistanısın.
Bugünün tarihi: {today}.

İlkeler:
- Sana araç verildiyse, cevabını resmî kaynaklara (mevzuat metni, mahkeme kararı) dayandırmak için araçları kullan. Araç yoksa kendi bilginle cevap ver.
- Asla karar künyesi, madde numarası ya da alıntı uydurma. Doğrulayamadığın bir kaynağı gösterme; emin değilsen bunu açıkça söyle.
- Mevzuatın güncel (yürürlükteki) hâlini esas al; soru belirli bir tarihi soruyorsa o tarihteki hâli esas al.
- Kısa ve net ol. Cevabının en sonunda, istenen alanlarla tek bir ```json kod bloğu ver; bloktan sonra başka metin yazma."""


TRACK_INSTRUCTIONS: dict[str, str] = {
    "exam": """Aşağıdaki çoktan seçmeli soruyu cevapla. Yalnız bir şık doğrudur.
Son JSON bloğu:
```json
{{"choice": "A|B|C|D|E", "dayanak": ["ör. TBK m.344"], "gerekce": "en çok 3 cümle"}}
```""",
    "statute": """Aşağıdaki mevzuat sorusunu cevapla. Madde metnine dayanıyorsan ilgili kısmı aynen aktar.
Son JSON bloğu:
```json
{{"answer": "kısa cevap", "law_no": "kanun numarası", "article": "madde (ör. 344 veya 344/1)", "quoted_text": "maddenin ilgili kısmı, aynen", "citations": [{{"type": "mevzuat", "law_no": "...", "article": "..."}}]}}
```""",
    "case_lookup": """Aşağıda anlatılan mahkeme kararını bul. En olası en çok 3 kararı olasılık sırasıyla ver.
Son JSON bloğu:
```json
{{"decisions": [{{"court": "Yargıtay|Danıştay|Anayasa Mahkemesi|BAM|...", "chamber": "ör. 3. Hukuk Dairesi", "esas": "YYYY/N", "karar": "YYYY/N", "date": "GG.AA.YYYY", "basvuru_no": "AYM için YYYY/N, yoksa null"}}], "note": "kısa açıklama"}}
```""",
    "citation_check": """Aşağıdaki karar atıflarının her birini denetle: böyle bir karar gerçekten var mı, künye bilgileri (daire, esas, karar, tarih) doğru mu?
Her atıf için hüküm ver: "var" (künye doğru), "tarih_hatali" (karar var ama tarih yanlış), "yok" (böyle bir karar yok ya da künye hatalı), "belirsiz" (doğrulayamadım).
Son JSON bloğu:
```json
{{"items": [{{"index": 1, "verdict": "var|tarih_hatali|yok|belirsiz", "correct_date": "GG.AA.YYYY veya null", "note": "kısa"}}]}}
```""",
    "research": """Aşağıdaki hukuki soruyu araştırarak cevapla. Dayandığın mevzuatı ve kararları künyesiyle göster.
Son JSON bloğu:
```json
{{"answer": "gerekçeli cevap", "citations": [{{"type": "mevzuat", "law_no": "...", "article": "..."}}, {{"type": "karar", "court": "...", "chamber": "...", "esas": "YYYY/N", "karar": "YYYY/N", "date": "GG.AA.YYYY"}}]}}
```""",
}


SERVER_INSTRUCTIONS_BLOCK = """

Araç sunucusunun kendi talimatları (sunucu tarafından sağlanmıştır; MCP istemcilerinin yaptığı gibi aynen iletilir):
<sunucu_talimatlari>
{instructions}
</sunucu_talimatlari>"""


def render_system_prompt(today: str, server_instructions: str = "") -> str:
    prompt = SYSTEM_PROMPT.format(today=today)
    if server_instructions.strip():
        prompt += SERVER_INSTRUCTIONS_BLOCK.format(instructions=server_instructions.strip())
    return prompt


def render_task_prompt(task: Task) -> str:
    instr = TRACK_INSTRUCTIONS[task.track].format()
    body = task.prompt.strip()
    if task.track == "exam" and task.options:
        opts = "\n".join(f"{k}) {v}" for k, v in sorted(task.options.items()))
        body = f"{body}\n\n{opts}"
    return f"{instr}\n\n---\n{body}"
