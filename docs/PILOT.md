# Pilot koşu — 15 Ekim 2026

İlk uçtan uca koşu. Amaç sistemleri sıralamak değil, görev setinin ve puanlamanın ayırt edici olup
olmadığını görmekti. Sayılar küçük örneklemden gelir ve güven aralıkları geniştir.

## Kurulum

- **Görevler:** test bölümünden sabit tohumla seçilen 45 görev: 20 sınav (10'u ajan modelinin bilgi
  kesiminden sonraki HMGS 2026 Eylül'den), 8 mevzuat, 8 karar bulma, 4 atıf denetimi (20 atıf),
  5 açık araştırma. Seçim betiği görev kimliklerini sabitler; aynı görevler bütün sistemlerde koşuldu.
- **Sistemler:** Legaluga MCP, Yargı MCP + Mevzuat MCP (açık kaynak), genel web araması, kapalı kitap.
  Yargı PRO (hesap yok) ve Legal Data Hunter (ücretsiz plan kotası doldu) koşulmadı.
- **Ajan:** harness döngüsü yerine harici koşucu. Her sistem için, yalnız o sistemin araçlarına
  izin verilen bir oturum ajanı görevleri `render` ile aldı, cevabı `record` ile kaydetti. Görev
  başına en çok 20 araç çağrısı. Bütün sistemlerde aynı model ve aynı istem.
- **Puanlama:** otomatik track'ler resmî altın veriyle; açık araştırma kör hakemle (cevaplar
  rastgele kodlu ve karışık sırada, sistem adları maskelenmiş) ve atıflar Bedesten'de otomatik
  doğrulanarak.

## Sonuçlar

| Sistem | Sınav | Mevzuat | Karar bulma | Atıf denetimi | Açık araştırma | Genel | Ort. araç çağrısı |
|---|---|---|---|---|---|---|---|
| Yargı MCP + Mevzuat MCP | 100.0 | 100.0 | 100.0 | 100.0 | 95.1 | 99.0 | 4.31 |
| Legaluga MCP¹ | 100.0 | 100.0 | 100.0 | 100.0 | 94.4 | 98.9 | 2.69 |
| Genel web araması | 100.0 | 87.5 | 12.5 | 58.8 | 95.6 | 70.9 | 4.76 |
| Kapalı kitap | 100.0 | 71.2 | 0.0 | 3.8 | 88.3 | 52.7 | 0 |

¹ Legaluga Core API koşu boyunca HTTP 530 döndürüyordu: `search_cases_v1` çalışmadı,
`semantik_ictihat_ara` yalnız Bedesten adaylarıyla çalıştı. Sonuçlar bu bozulmuş hâli yansıtır.

Açık araştırmada sistemler arası farkların hepsi güven aralığının içinde (n = 5). Araştırma
cevaplarında resmî kaynakta bulunamayan atıf oranı: web araması %2, diğerleri %0.

## Bulgular

1. **Sınav track'i tavana vuruyor.** Dört sistem de 20 sorunun hepsini doğru cevapladı; bunlara
   modelin eğitim verisinde olamayacak HMGS 2026 Eylül soruları da dahil. Güçlü bir ajan modeliyle
   bu track araçları ayırt etmiyor. Daha küçük modellerle ve yalnız `statute`/`calculation` türü
   sorularla ayrıca raporlanmalı.
2. **Uzman araçlar ile genel araçlar arasındaki fark büyük ve net.** Karar bulmada Bedesten'e
   erişen iki MCP sistemi 8 kararın 8'ini 1. sırada buldu; web araması 1'ini, kapalı kitap hiçbirini.
   Atıf denetiminde MCP sistemleri bütün uydurma ve tarihi hatalı künyeleri yakaladı; web araması
   çoğu atfa "belirsiz" dedi (karar metinleri ücretli duvar arkasında ya da siteler erişimi
   engelliyor), kapalı kitap hepsine.
3. **İki Bedesten tabanlı sistem bu görevlerde birbirinden ayrışmıyor.** Karar bulma, atıf
   denetimi ve mevzuat görevleri, aynı resmî kaynağı arayan iki sistem için de kolay. Aradaki
   tek belirgin fark verimlilik: Legaluga görev başına ortalama 2,69, açık kaynak 4,31 araç çağrısı
   yaptı. İki sistemi ayırmak için daha zor görevler gerekiyor: anahtar kelimeyle bulunamayan
   (eş anlamlı, dolaylı) olay anlatımları, Bedesten'in tam metin aramasının kaçırdığı kararlar,
   çok adımlı atıf zincirleri, mevzuatın eski hâlini isteyen sorular.
4. **Kapalı kitap künye uydurmadı.** Araçsız model hiçbir karar numarası vermedi, bilmediği yeri boş
   bıraktı. Bu, istemdeki "künye uydurma" ilkesinin bu modelde işlediğini gösterir; daha zayıf
   modellerde ölçülmeli.

## Puanlamada bulunan ve düzeltilen hatalar

Pilot, otomatik atıf doğrulamasında üç yanlış alarm kaynağını ortaya çıkardı; hepsi düzeltildi ve
birim testleri eklendi:

- **Bedesten kapsamı dışındaki kararlar** (içtihadı birleştirme kararları, 2010 öncesi kararlar,
  bölge adliye mahkemesi kararlarının çoğu) bulunamadığında "uydurma" sayılıyordu; artık
  "denetlenemedi" sayılıyor. Düzeltmeden önce Legaluga'nın araştırma cevaplarında %6 "uydurma"
  görünüyordu; işaretlenenlerin hepsi gerçek kararlardı (ör. YİBK 1990/4 E., 1991/3 K.).
- **Metinden çıkarılan künyenin mahkemesi yanlış tahmin ediliyordu.** JSON'da doğru verilmiş bir
  Yargıtay kararı, metindeki tekrarında yakındaki "BAM'lar" kelimesi yüzünden BAM kararı sayılıp
  bulunamıyordu. Aynı esas/karar numarası yapılandırılmış alanda varsa metindeki tekrar artık
  atlanıyor.
- **Değişiklik kanunlarının maddeleri.** Bedesten, başka kanunlara işlenmiş maddeleri ağaçta
  göstermiyor; 7445 sayılı Kanun m.18 bu yüzden "yok" sayılıyordu. Değişiklik kanunlarında ve madde
  numarası dizisindeki boşluklarda eksik madde artık "denetlenemedi".

## Legaluga için ürün gözlemleri

Pilot sırasında Legaluga araçlarında görülenler (Core kapalıyken):

- Core API HTTP 530 (koşu boyunca); `semantik_ictihat_ara` iki kez 60 sn zaman aşımı ve iki aramada
  CORE_PARTIAL.
- `karar_getir` iki kez Bedesten hız sınırına (HTTP 429) takıldı.
- `search_cases_v1` Danıştay için INVALID_INPUT ("İstenen mahkeme kapsamı bu kaynakta etkin değil").
- `karar_ara` "35.590" gibi tutarları "35 590" biçimine çevirdiği için sayıyla aramalar sonuç
  vermedi; tam metinde geçen özel adlar ("Pakistan", "Alanya") 0 sonuç döndürdü. Bir kararı bulmak
  10 çağrı sürdü; açık kaynak araç aynı kararı 4 çağrıda buldu.
- `emsal_atif_dogrula` bir kez geçici HTTP 500 döndürdü (tekrar denemede düzeldi).

## Sınırlar

- Harici koşucuda araç çıktıları kaydedilmedi; dayanak oranı (grounding), süre ve belirteç
  sayıları ölçülemedi. Harness ile (`run` komutu, API anahtarıyla) tekrarlanmalı.
- Hakem, ajanla aynı model ailesinden; insan ikinci puanlaması yapılmadı.
- Örneklem küçük (sistem başına 45 görev); farkların çoğu istatistiksel olarak anlamlı değil.
- Legaluga sonuçları Core kapalıyken alındı.

## Sonraki adımlar

1. Legaluga Core açıkken Legaluga koşusunu tekrarlamak.
2. Harness ile (araç çıktıları kayıtlı) tam test bölümünü koşmak; dayanak oranını ölçmek.
3. Bedesten tabanlı sistemleri ayırt edecek zor karar bulma ve araştırma görevleri eklemek.
4. Yargı PRO ve Legal Data Hunter'ı (ücretli planla) eklemek; daha küçük bir ajan modeliyle
   sınav track'ini tekrarlamak.
