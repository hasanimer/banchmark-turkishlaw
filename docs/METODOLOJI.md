# Legaluga Law Benchmark — Metodoloji

Bu belge benchmark'ın neyi, nasıl ve hangi sınırlarla ölçtüğünü anlatır. Puanlama
kodu (`legaluga_bench/scoring/`) bu belgeyle tutarlı tutulur; biri değişirse öteki de güncellenir.

## 1. Amaç ve soru

> Aynı yapay zekâ ajanına farklı Türk hukuku araştırma araçları verildiğinde, ajan
> hukuki sorulara ne kadar doğru, kaynağa dayalı ve uydurmasız cevap verir?

Ölçülen şey modelin değil, **aracın** katkısıdır. Bu yüzden bütün sistemlerde ajan modeli,
sistem istemi, araç bütçesi, zaman aşımı ve puanlama aynıdır; değişen yalnız ajana verilen
araç kümesidir. Araçsız (kapalı kitap) ve genel web araması baz çizgileri, bir aracın modele
ne kattığını ayırmak için her koşuda yer alır.

## 2. Çıkar çatışması beyanı ve tarafsızlık önlemleri

Benchmark, test edilen sistemlerden biri olan Legaluga'nın ekibi tarafından hazırlanmıştır.
Bu durum sonuçlara gölge düşürebileceği için şu kurallar uygulanır:

1. **Altın cevaplar yalnız resmî kaynaklardan gelir.** ÖSYM cevap anahtarları, Adalet
   Bakanlığı Bedesten servisi (karar ve mevzuat), mevzuat.gov.tr ve Anayasa Mahkemesi karar
   bilgi bankası. Hiçbir test edilen sistemin (Legaluga dahil) çıktısı altın veri üretiminde
   kullanılmaz. Resmî kaynak istemcisi (`legaluga_bench/official/`) bağımsız yazılmıştır.
2. **Görev üretimi tohumludur ve yeniden üretilebilir.** Karar örneklemi sabit tohumla
   rastgele seçilir; kimse "iyi sonuç veren" kararları elle seçmez.
3. **Kör hakem.** Açık uçlu cevapları puanlayan hakeme sistem adı verilmez; cevap metnindeki
   sistem ve araç adları maskelenir. Hakem modeli bütün sistemler için aynıdır.
4. **Ayrık geliştirme ve test bölümleri.** Görevlerin yaklaşık %15'i `dev`, kalanı `test`
   bölümündedir. Araç geliştirme (Legaluga dahil) yalnız `dev` üzerinde yapılmalıdır;
   yayımlanan sonuçlar `test` bölümünden verilir.
5. **Açık kod, açık ham çıktı.** Harness, istemler, puanlama ve her koşunun ham kayıtları
   (araç çağrıları dahil) yayımlanır. Rakipler kendi sistemlerini aynı harness ile koşabilir.
6. **Sürümler kaydedilir.** Her koşu, model kimliğini, ayarları ve tarihi `run_config.json`
   içinde saklar; sistemlerin araç listesi koşu anında kaydedilir.

## 3. Test edilen sistemler

Sistemler `configs/systems.yaml` dosyasında tanımlanır:

| Kimlik | Sistem | Erişim |
|---|---|---|
| `legaluga` | Legaluga MCP | Uzak MCP (Streamable HTTP), OAuth belirteci |
| `de_jure` | De Jure MCP (ticari) | Uzak MCP (Streamable HTTP), OAuth; yalnız arama/getirme araçları |
| `yargi_pro` | Yargı PRO (ticari) | Uzak MCP, OAuth / kurumsal anahtar |
| `acik_kaynak` | Yargı MCP + Mevzuat MCP (açık kaynak) | Yargı MCP yerel (stdio) + Mevzuat MCP barındırılan; tek sistem olarak |
| `legal_data_hunter` | Legal Data Hunter | Uzak MCP, anahtarla |
| `web_search` | Genel web araması | Anthropic sunucu tarafı `web_search` aracı |
| `closed_book` | Araçsız | — |

Açık kaynak araçlar içtihadı ve mevzuatı ayrı sunucularda verdiği için kullanıcıların yaptığı
gibi birlikte (`composite`) ölçülür. Lexpera, Kazancı, Sinerji gibi yalnız web arayüzü olan
ticari ürünlerin herkese açık bir API'si ya da MCP sunucusu bulunamadığından otomatik koşuya
alınmamıştır.

Yeni bir sistem eklemek için YAML'a bir giriş yazmak yeterlidir (MCP sunucusu olması koşuluyla).

**Araç politikası.** Her sistemin araştırma araçları, sunucunun kendi açıklamalarıyla
olduğu gibi ajana verilir; araç açıklamalarının kalitesi ürünün parçası sayılır. Sunucunun
MCP `initialize` yanıtındaki talimatları da (varsa), Claude gibi MCP istemcilerinin yaptığı
gibi sistem isteminin sonuna ayrı bir blok olarak eklenir; bu seçim `use_server_instructions`
ile kapatılabilir ve her koşuda kaydedilir. Koşu başında her sistemin sunucu sürümü, araç
listesi ve araç şemalarının özeti (`results/<koşu>/systems/<sistem>.json`) saklanır; böylece
koşular arasında sunucu tarafında yapılan değişiklikler görülebilir. Yalnız
araştırma dışı işler (belge/dilekçe üretimi, imar hesapları gibi) bütün sistemlerde aynı ilkeyle
çıkarılır. Her araç çıktısı 30.000 karakterle sınırlanır (bütün sistemlere aynı sınır).

## 4. Ajan

| Ayar | Varsayılan |
|---|---|
| Model | Koşu başına `--model` / `LBENCH_AGENT_MODEL` ile seçilir; bütün sistemlerde aynıdır ve `run_config.json`'a yazılır |
| Akıl yürütme düzeyi (effort) | `high` |
| En çok araç çağrısı | 20 |
| En çok tur | 16 |
| Görev zaman aşımı | 900 sn |

Bütçe dolduğunda ajan araçsız son bir turda cevabını vermeye zorlanır; bu yüzden hiçbir
sistem bütçe yüzünden cevapsız kalmaz. Sistem istemi bütün sistemlerde aynıdır ve hiçbir
aracı adıyla anmaz (`legaluga_bench/agent/prompts.py`). Model, refusal durumunda başka modele
devredilmez (sunucu tarafı yedek model kapalıdır); aksi hâlde aynı koşu içinde iki farklı
model karşılaştırılmış olurdu. Reddedilen görevler hata olarak sayılır ve raporlanır.

## 5. Track'ler

### 5.1 Sınav (`exam`)

**Kaynak.** Gerçek ÖSYM sınavları: Hukuk Mesleklerine Giriş Sınavı (HMGS 2024 Eylül, 2025/1,
2025/2, 2026 Nisan, 2026 Eylül), Hâkim ve Savcı Adaylığı sınavları (2018–2025, adli/idari ve
ortak alan), KPSS A Grubu Hukuk 2026 ve İYÖS 2025.

**Altın cevap.** ÖSYM aday ekranında her sorunun altında görünen resmî cevap anahtarı.

**Yazıya dökme.** Kaynaklar, adayların ÖSYM ekranından aldığı ekran görüntüleridir. Her
sayfa, görüntüyü doğrudan okuyan bir model tarafından yazıya dökülür (Tesseract OCR yalnız
yardımcıdır). Aynı oturumun iki bağımsız çekimi bulunan HMGS 2026 Eylül'de iki döküm
karşılaştırılır; cevap anahtarı uyuşmayan soru çıkarılır. Şu sorular set dışı bırakılır:
hukuk dışı GKGY soruları, cevap anahtarı görünmeyenler, şıkkı/gövdesi eksik olanlar ve
çözümü bir şekle dayananlar.

**Zaman.** Soru metninin başında sınavın adı ve tarihi verilir ve ajandan **sınav
tarihindeki** mevzuata göre cevap vermesi istenir; çünkü cevap anahtarı o tarihteki hukuka
göredir. Sınavdan sonra mevzuatı değişen sorular ayrıca işaretlenir ve raporda ayrı gösterilir.

**Güncellik ve anahtar denetimi.** Güncel katmandaki (2024 ve sonrası) her soru, araştırma aracı
kullanılmadan yalnız yerel resmî kanun metinleri (Bedesten, değişiklik ve iptal notlarıyla)
üzerinden denetlenir: (a) dayanak hüküm hangisi; (b) sınav tarihinden sonra cevabı
değiştirebilecek bir değişiklik, ek, mülga ya da AYM iptali var mı (`stale_risk`: evet / hayır /
belirsiz); (c) sınav tarihindeki hukuka göre resmî anahtar doğru mu. Anahtarı tutarsız
görünen sorularda kaynak sayfanın görüntüsüne yeniden bakılarak yazıya dökme hatası ayıklanır.
Anahtarı şüpheli (`anahtar_supheli`) ya da sınavdan sonraki bir değişiklikle cevabı değişmiş
olabilecek (`guncellik_riski`) sorular puanlamaya alınmaz. İlk denetimde 768 sorudan 766'sının
anahtarı tutarlı bulundu, 2'si şüpheli, 2'si güncellik riski taşıyordu; 39 soruda dayanak kanun
yerel sette olmadığından güncellik "belirsiz" kaldı ve raporda ayrı gösterilir.

**Puan.** Doğru şık 1, aksi 0. Raporda ders, soru türü (`statute` = belirli bir hükmün
lafzına/sayısına dayanan, `doctrine`, `case_law`, `calculation`, `mixed`) ve oturum kırılımları verilir.

**Bulaşma (contamination).** Eski ÖSYM soruları internette yayımlıdır ve modellerin eğitim
verisinde bulunabilir. Bunun etkisi kapalı kitap baz çizgisiyle ölçülür. Ajan modelinin bilgi
kesim tarihinden sonra yapılan oturumlar (ör. HMGS 2026 Eylül) bulaşmasız alt küme olarak
ayrıca raporlanmalıdır.

**Tavan etkisi.** Pilotta (20 güncel soru, yarısı ajan modelinin bilgi kesiminden sonraki HMGS
2026 Eylül'den) hem kapalı kitap hem genel web araması bütün soruları doğru cevapladı. Güçlü
bir ajan modeliyle bu track araçlar arasında ayrım yapmıyor; asıl ayrım mevzuat, karar bulma
ve atıf denetimi track'lerinde ortaya çıkıyor. Sınav track'i bu yüzden genel puanda
tutulur ama ayrıca (a) daha küçük ajan modelleriyle, (b) `statute` ve `calculation` türü
sorularla sınırlı alt kümeyle raporlanması önerilir.

**Telif.** ÖSYM soruları ÖSYM'nin yazılı izni olmadan yayımlanamaz. Bu yüzden soru metinleri
repoda yer almaz (`data/private/` git dışındadır). Repoda yalnız sayılar ve kaynak dosya
özetleri (`data/exams_manifest.json`) bulunur.

### 5.2 Karar bulma (`case_lookup`)

**Kaynak.** Bedesten'den sabit tohumla, katmanlı (Yargıtay hukuk/ceza daireleri ve genel
kurulları, Danıştay daireleri ve kurulları, bölge adliye mahkemeleri; 2014–2026) rastgele
örneklenen kararlar (`legaluga_bench/official/gold_cases.py`). Çok kısa (1.500 karakterden az)
kararlar ayırt edici içerik taşımadığı için örneklemden çıkarılır; ayrıca anlatımı yazan adım,
yalnız usule ilişkin kalıp kararları ayırt edilemez sayarak eler.

**Görev.** Kararın resmî tam metninden yazılmış, numara ve tarih içermeyen, avukat dilinde
bir olay ve sonuç anlatımı. Ajandan bu kararı bulup künyesini (en çok 3 aday) vermesi istenir.

**Puan.** Doğru karar (esas + karar numarası; daire belirtilmişse o da tutmalı) 1. sıradaysa 1,
2. sıradaysa 1/2, 3. sıradaysa 1/3, yoksa 0 (MRR@3).

### 5.3 Atıf denetimi (`citation_check`)

**Görev.** "Dilekçe taslağında geçen" beş karar atfı; ajan her biri için `var`, `tarih_hatali`,
`yok` ya da `belirsiz` hükmü verir.

**Altın veri.** Gerçek künyeler Bedesten örnekleminden gelir. Uydurma künyeler üç yolla
üretilir: (a) karar numarası değiştirilir ve değiştirilmiş künyenin Bedesten'in **bütün
dairelerinde** bulunmadığı doğrulanır; (b) hiç var olmamış bir daire yazılır (Yargıtay 24–27.
Hukuk Dairesi, Danıştay 18–19. Daire); (c) gerçek kararın tarihi kaydırılır (`tarih_hatali`).

**Puan.** Doğru hüküm 1; `tarih_hatali` hükmünde doğru tarih de verilmişse 1, verilmemişse
0,75. Görev puanı beş atfın ortalamasıdır. Raporda ayrıca yakalanan uydurma atıf oranı ve
gerçek atfı "yok" sayma (yanlış alarm) oranı verilir.

### 5.4 Mevzuat (`statute`)

**Görev.** Yürürlükteki bir kanun hükmünün içeriğine dair soru (süre, sınır, şart vb.).

**Altın veri.** Madde metni resmî mevzuat kaynağından alınır; soruyu, kabul edilen cevap
kalıplarını ve madde metninde bulunması gereken ifadeleri bu metinden üretir.

**Puan.** 0,5 × cevap doğruluğu + 0,3 × doğru kanun ve madde + 0,2 × aktarılan metnin
sadakati (madde metnindeki zorunlu ifadelerin ne kadarının aynen aktarıldığı).

### 5.5 Açık araştırma (`research`)

**Görev.** Mevzuat ve içtihat gerektiren, gerekçeli cevap isteyen sorular.

**Puan.** 0,7 × rubrik puanı + 0,3 × atıf geçerliliği.
- *Rubrik puanı:* kör hakem, soruya özgü ölçütleri (0 / 0,5 / 1) puanlar.
- *Atıf geçerliliği:* cevaptaki bütün karar ve madde atıfları resmî kaynakta otomatik
  denetlenir. Geçerlilik = bulunan atıf / denetlenebilen atıf. Hiç atıf vermeyen cevabın
  geçerlilik terimi 0'dır (araştırma sorusu kaynak ister). Kararlarda numara başka bir dairede
  bulunuyorsa atıf geçerli sayılmaz (`chamber_mismatch`) ama uydurma da sayılmaz.

## 6. Raporlama ve istatistik

- Her sistem × track için ortalama puan ve %95 bootstrap güven aralığı (2.000 yeniden örnekleme, sabit tohum).
- Sistem çiftleri yalnız ikisinin de cevapladığı **ortak görevler** üzerinden karşılaştırılır:
  eşleştirilmiş bootstrap farkı ve sınav track'inde kesin McNemar testi.
- Genel puan, bütün track'leri koşan sistemler için track ortalamalarının eşit ağırlıklı ortalamasıdır.
- Maliyet ve işletim göstergeleri: ortalama araç çağrısı, süre, girdi/çıktı belirteci, hata
  oranı ve araç hatası oranı.
- **Dayanak oranı (grounding):** cevapta verilen karar künyelerinden esas ve karar numarası
  ajanın o görevdeki araç çıktılarında gerçekten geçenlerin oranı. Künyenin modelin belleğinden
  değil aracın döndürdüğü kaynaktan geldiğini gösterir; araçsız sistemlerde tanımsızdır.
- **Uydurma atıf oranı:** açık araştırma cevaplarındaki atıflardan resmî kaynakta bulunamayanların oranı.

## 7. Bilinen sınırlar

- **Bedesten kapsamı.** Bedesten her kararı yayımlamaz. "Bulunamadı", kararın hiç var
  olmadığının kesin kanıtı değildir. Uydurma künyeler bu yüzden ya olmayan dairelerden ya da
  bütün dairelerde bulunmadığı doğrulanmış numara değişikliklerinden üretilir. Açık araştırma
  cevaplarındaki atıf denetiminde, Bedesten'in büyük ölçüde kapsamadığı kararlar (içtihadı
  birleştirme kararları, Büyük Genel Kurul, 2010 öncesi kararlar, bölge adliye mahkemesi
  kararları) bulunamadığında uydurma değil "denetlenemedi" sayılır. Aynı kural, değişiklik
  kanunlarında ve madde ağacındaki numara boşluklarında bulunamayan maddelere de uygulanır.
- **Kaynak eğilimi.** Karar bulma görevleri Bedesten'den örneklendiği için Bedesten'i kullanan
  araçlar kapsam avantajına sahip olabilir. Bu, kullanıcının erişebildiği resmî kaynağı
  yansıtır; ancak raporda kaynak türüne göre kırılım verilir.
- **Tek model.** Sonuçlar seçilen ajan modeline bağlıdır; farklı modellerle tekrarlanması önerilir.
- **Hakem modeli.** LLM hakemi insan değerlendirmesinin yerini tutmaz; açık araştırma
  track'inde rastgele bir alt kümenin insan tarafından ikinci kez puanlanması önerilir.
- **Yazıya dökme hataları.** Görüntüden yazıya dökmede hata olabilir; iki çekimli oturumlarda
  uyuşmazlıklar ölçülür ve ayıklanır.
- **Mevzuat değişiklikleri.** Eski sınav sorularının cevapları sonraki değişikliklerle
  güncelliğini yitirebilir; bu sorular işaretlenir.

## 8. Önceki çalışmalar

- **TRLawBench** (Said Sürücü): geçmiş ÖSYM sorularından 97 çoktan seçmeli soru; araç
  değerlendirmesi yok. Ticari kullanım yasak olduğu için soruları kullanılmamıştır; sınav
  track'i doğrudan ÖSYM kaynaklarından yeniden kurulmuştur.
- **mecellem-legal-bench** (NewMind AI): rubrikli açık uçlu Türkçe hukuk soruları ve araç
  çıktısına dayanma metriği; açık araştırma track'i ve dayanak oranı için yöntemsel öncüldür.
- Türkçe mevzuat atfı uydurma benchmark'ı (LawChatAI) ve İngilizce atıf denetimi çalışmaları
  atıf denetimi track'indeki hata türlerine (yanlış daire, numara, tarih, olmayan karar) ilham vermiştir.

Bildiğimiz kadarıyla bu benchmark, Türk hukuku araştırma araçlarını (MCP sunucularını) aynı
ajan üzerinden doğrudan karşılaştıran ilk çalışmadır.

**Ortak derlem uyarısı.** Birçok araç aynı açık karar derleminden (≈11 milyon künye, CC0)
yararlanmaktadır. Altın veri bu derlemden değil, doğrudan resmî kaynaklardan canlı olarak
alınır ve alındığı an ile özetiyle saklanır.

## 9. Yeniden üretim

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
cp .env.example .env              # anahtarları doldurun
python -m legaluga_bench systems --probe
python -m legaluga_bench build-exams          # data/private altında ÖSYM soruları gerekir
python -m legaluga_bench run --run-name pilot --tracks exam,case_lookup,citation_check --limit 50 --today 13.10.2026
python -m legaluga_bench score --run-name pilot
python -m legaluga_bench report --run-name pilot
```
