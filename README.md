# Legaluga Law Benchmark

Türk hukuku araştırma araçlarını, **aynı yapay zekâ ajanına araç olarak verildiklerinde** ne
kadar doğru, kaynağa dayalı ve uydurmasız sonuç ürettiklerine göre karşılaştıran açık benchmark.

Ajan modeli, istem, araç bütçesi ve puanlama bütün sistemlerde aynıdır; değişen yalnız ajana
verilen araç kümesidir (MCP sunucusu). Araçsız (kapalı kitap) ve genel web araması baz
çizgileri, bir aracın modele ne kattığını ayırmak için her koşuda yer alır.

Altın cevaplar yalnız **resmî kaynaklardan** gelir: ÖSYM cevap anahtarları, Adalet Bakanlığı
Bedesten servisi (karar ve mevzuat) ve mevzuat.gov.tr. Ayrıntılar ve tarafsızlık önlemleri:
[docs/METODOLOJI.md](docs/METODOLOJI.md).

> **Çıkar çatışması beyanı:** Benchmark, test edilen sistemlerden biri olan Legaluga'nın ekibi
> tarafından hazırlanmıştır. Bu yüzden altın veri hiçbir test edilen sistemden üretilmez, hakem
> kördür, kod/istem/ham çıktılar açıktır ve rakipler kendi koşularını aynı harness ile yapabilir.

## Track'ler

| Track | Ne ölçer | Altın veri | Puan |
|---|---|---|---|
| `exam` | Gerçek sınav soruları (HMGS, hâkim-savcı adaylığı, KPSS hukuk) | ÖSYM cevap anahtarı | Doğru şık |
| `statute` | Yürürlükteki mevzuatı bulma ve doğru aktarma | Bedesten mevzuat (resmî madde metni) | Cevap + madde + aktarım sadakati |
| `case_lookup` | Anlatılan kararı bulma | Bedesten'den tohumlu rastgele örneklem | MRR@3 |
| `citation_check` | Dilekçedeki uydurma/hatalı künyeleri yakalama | Bedesten'de doğrulanmış gerçek ve uydurma künyeler | Atıf başına doğru hüküm |
| `research` | Gerekçeli hukuki araştırma | Resmî kaynağa dayalı rubrik | Kör hakem + otomatik atıf doğrulama |

## Sistemler

`configs/systems.yaml` içinde tanımlıdır: Legaluga MCP, Yargı PRO, Yargı MCP + Mevzuat MCP
(açık kaynak), Legal Data Hunter, genel web araması ve kapalı kitap. MCP sunucusu olan her araç
YAML'a bir giriş eklenerek karşılaştırmaya katılabilir (stdio ya da Streamable HTTP; birden çok
sunucu `composite` ile tek sistem yapılabilir).

## Kurulum

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env    # LBENCH_AGENT_MODEL, LBENCH_JUDGE_MODEL, ANTHROPIC_API_KEY ve sistem belirteçleri
```

Yargı MCP yerelde çalıştırılır; bağımlılık çakışmasını önlemek için ayrı bir sanal ortama kurun:

```bash
python -m venv ~/.venvs/yargi && ~/.venvs/yargi/bin/pip install "yargi-mcp==0.2.2" "fastmcp>=3.4.4,<4" "mcp>=1.24,<2"
echo "YARGI_MCP_COMMAND=$HOME/.venvs/yargi/bin/yargi-mcp" >> .env
```

## Kullanım

```bash
python -m legaluga_bench systems --probe                  # sistemler hazır mı, kaç araç var
python -m legaluga_bench tasks                            # görev setinin özeti
python -m legaluga_bench run --run-name pilot \
    --systems legaluga,acik_kaynak,web_search,closed_book \
    --tracks exam,statute,case_lookup,citation_check,research \
    --limit 50 --today 13.10.2026
python -m legaluga_bench score --run-name pilot          # puanla (hakem + resmî atıf doğrulama)
python -m legaluga_bench report --run-name pilot         # results/pilot/report.md
```

Yardımcı komutlar:

```bash
python -m legaluga_bench toolcall --system acik_kaynak --list                 # bir sistemin araçları
python -m legaluga_bench official article --law 6098 --article 344            # resmî madde metni
python -m legaluga_bench official case --court yargitay --chamber "3. HD" --esas 2010/119 --karar 2010/478
```

Koşular kaldığı yerden devam eder; her sistem/görev için ham kayıtlar (araç çağrıları, süreler,
belirteç kullanımı) `results/<koşu>/runs/<sistem>.jsonl` dosyasına yazılır.

## ÖSYM soruları ve telif

ÖSYM soruları ÖSYM'nin yazılı izni olmadan yayımlanamaz. Bu yüzden sınav soruları repoda
**yoktur**; `data/private/` git dışındadır. Sınav track'i, soruları yerelde yazıya döküp
`python -m legaluga_bench build-exams` ile üretilir. Repoda yalnız sayılar ve kaynak dosya
özetleri bulunur: [data/exams_manifest.json](data/exams_manifest.json).

## Dizin yapısı

```
configs/systems.yaml        test edilen sistemler
data/tasks/                 public görevler (statute, case_lookup, citation_check, research)
data/gold/                  resmî kaynak örneklemleri ve altın veri taslakları
data/private/               (git dışı) ÖSYM soruları, kaynak PDF'ler, önbellek
docs/METODOLOJI.md          yöntem, tarafsızlık önlemleri, sınırlar
legaluga_bench/agent/       ajan döngüsü ve ortak istemler
legaluga_bench/systems/     MCP / web / kapalı kitap sağlayıcıları
legaluga_bench/official/    bağımsız Bedesten istemcisi, altın veri üreticileri
legaluga_bench/scoring/     künye ayrıştırma, track puanlaması, kör hakem, istatistik
legaluga_bench/report/      lider tablosu
tests/                      birim testleri (python -m pytest)
```
