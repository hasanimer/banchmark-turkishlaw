import os
import json

def seed():
    os.makedirs("data/questions", exist_ok=True)
    
    # 1. İCRA HUKUKU (icra.jsonl)
    icra_questions = [
        {
            "id": "icra_001",
            "area": "icra_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "Müvekkile ilamsız icra takibinde ödeme emri 08.07.2026 Perşembe günü tebliğ edilmiştir. Herhangi bir resmi tatil bulunmamaktadır. Borca ve yetkiye itiraz etmek istiyoruz. İtiraz süresi kaç gündür ve itiraz edebileceğimiz son gün hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "İlamsız icra takibinde (genel haciz yolu) ödeme emrine itiraz süresi, tebliğ tarihinden itibaren 7 gündür (İİK m. 62). Süre hesaplanırken tebliğ günü (08.07.2026) hesaba katılmaz, süre ertesi gün olan 09.07.2026 Cuma günü başlar. 7 günlük sürenin son günü 15.07.2026 Çarşamba günü mesai saati bitimidir. UYAP üzerinden yapılacak itirazlarda ise 15.07.2026 günü saat 23:59'a kadar süre mevcuttur.",
            "legal_basis": ["İİK m.62", "İİK m.19"],
            "reference_text": "İİK Madde 62 - İtiraz etmek istiyen borçlu, itirazını, ödeme emrinin tebliği tarihinden itibaren yedi gün içinde dilekçe ile veya sözlü olarak icra dairesine bildirmeye mecburdur.\nİİK Madde 19 - Günle muayyen sürelerde ilk gün hesaba katılmaz.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["itiraz_suresi", "genel_haciz", "sure_hesabi"]
        },
        {
            "id": "icra_002",
            "area": "icra_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "Batuhan, Alp’e karşı genel haciz yoluyla takip başlatır ve takip kesinleşir. Alp, Batuhan’a icra dairesi dışında ödeme yaparak borcun tamamını ve borcun ferîlerini itfa eder. Bu durum, Batuhan tarafından verilmiş imzası noterlikçe onaylı bir belgeyle kayıt altına alınır ancak Batuhan yine de takibe devam eder. 2004 sayılı İcra ve İflas Kanunu’na göre Alp’in, bu duruma karşı koymak üzere ancak paraların paylaştırılmasına kadar başvurabileceği hukuki yol aşağıdakilerden hangisidir?\nA) İcra takibinin iptali\nB) İtirazın muvakkaten kaldırılması\nC) İcra takibinin ertelenmesi\nD) Borçtan kurtulma davası\nE) Gecikmiş itiraz",
            "expected_answer": "A",
            "legal_basis": ["İİK m.71/2"],
            "reference_text": "İİK Madde 71 - Borçlu, takibin kesinleşmesinden sonraki devrede borcun itfa edildiğini yahut kendisine mühlet verildiğini noterlikçe re'sen tanzim veya imzası tasdik edilmiş bir belge ile... ispat ederse, takibin iptal veya ertelenmesini icra mahkemesinden isteyebilir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["icra_iptal", "haricen_odeme", "iik_71", "mcq"]
        },
        {
            "id": "icra_003",
            "area": "icra_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Borçlu A'nın evine icra dairesi tarafından haciz işlemi uygulanmış ve A'nın oturduğu tek evi haczedilmiştir. Haciz işlemi 01.07.2026 tarihinde A'nın gıyabında yapılmış, haciz durumunu gösterir 103 davetiyesi ise A'ya 06.07.2026 tarihinde tebliğ edilmiştir. Borçlu, bu evin tek meskeni olduğunu belirterek haczedilemezlik şikayetinde bulunmak istemektedir. Şikayet süresi ne kadardır, süre ne zaman başlar ve son gün hangisidir? Şikayet hangi merciye yapılmalıdır? Eğer şikayet 15.07.2026 tarihinde yapılırsa icra mahkemesi nasıl bir karar vermelidir?",
            "expected_answer": "1. Meskeniyet iddiasına dayalı haczedilmezlik şikayeti, İİK m. 16/1 uyarınca yedi günlük hak düşürücü süreye tabidir. \n2. Gıyapta haciz yapıldığından süre, haczin öğrenildiği (yani 103 davetiyesinin tebliğ edildiği) 06.07.2026 tarihini takip eden gün (07.07.2026) başlar. Son gün 13.07.2026 Pazartesi mesai bitimidir.\n3. Şikayet, haczi koyan icra dairesinin bağlı olduğu İcra Mahkemesi'ne yapılmalıdır.\n4. Şikayet 15.07.2026 tarihinde yapılmışsa, 7 günlük yasal süre geçirildiği için icra mahkemesi şikayeti esasa girmeden 'süre aşımı (süre yönünden)' reddetmelidir.",
            "legal_basis": ["İİK m.16", "İİK m.82/1-12"],
            "reference_text": "İİK Madde 16 - Kanunun hallini mahkemeye bıraktığı hususlar müstesna olmak üzere icra ve iflas dairelerinin yaptığı muameleler hakkında kanuna muhalif olmasından veya hadiseye uygun bulunmamasından dolayı icra mahkemesine şikayet olunabilir. Şikayet bu muamelelerin öğrenildiği tarihten yedi gün içinde yapılır.\nİİK Madde 82 - (Değişik: 2/7/2012-6352/16 md.) ... 12. Borçlunun haline münasip evi...",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["meskeniyet", "sikayet_suresi", "icra_mahkemesi"]
        },
        {
            "id": "icra_004",
            "area": "icra_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Alacaklı müvekkil Ahmet Yılmaz'ın, borçlu Mehmet Kaya'dan 10.05.2026 tarihli 100.000 TL bedelli adi yazılı alacak sözleşmesine dayalı faturalandırılmamış bir alacağı vardır. Bu alacağa sözleşme gereği aylık %3 (yıllık %36) akdi faiz işletilmesi kararlaştırılmıştır. Borçlu borcunu vadesi olan 10.06.2026'da ödememiştir. Bugün (09.07.2026) itibariyle Ankara İcra Dairelerinde genel haciz yoluyla ilamsız icra takibi başlatacağız. UYAP sistemine girilmek üzere takip talebinde yer alacak 'Alacak Kalemleri ve Detayları' ile 'Takip Talebi' metnini yasal mevzuata uygun şekilde hazırlayınız.",
            "expected_answer": "Takip Talebinde şu unsurlar bulunmalıdır:\n1. Alacaklı: Ahmet Yılmaz (TCKN, Adres vb.), Vekili: Av. ...\n2. Borçlu: Mehmet Kaya (TCKN, Adres)\n3. Alacak Tutarı: 100.000,00 TL (Asıl Alacak)\n4. Faiz Hesabı: Temerrüt tarihi 11.06.2026'dır. 11.06.2026 ile 09.07.2026 arası geçen gün sayısı 28 gündür. Faiz = 100.000 * 0.36 * 28 / 360 = 2.800,00 TL akdi faiz.\n5. Toplam Alacak: 102.800,00 TL.\n6. Takip Sonrası Faiz Talebi: Fiili ödeme tarihine kadar asıl alacak olan 100.000 TL'ye işleyecek yıllık %36 akdi faiz talebi.\n7. Takip Yolu: İlamsız Haciz Yolu.",
            "legal_basis": ["İİK m.58", "TBK m.88", "TBK m.120"],
            "reference_text": "İİK Madde 58 - Takip talebi icra dairesine yazılı veya sözlü olarak veyahut elektronik ortamda yapılır. Takip talebinde şunlar yazılır: ... 3. Alacağın veya istenen teminatın Türk parasıyla tutarı ve faizli alacaklarda faizin miktarı ile işlemeye başladığı gün...",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["takip_talebi", "faiz_hesabi", "belge_uretimi"]
        },
        {
            "id": "icra_005",
            "area": "icra_hukuku",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Aşağıdaki dilekçe taslağı, borçluya genel haciz yoluyla ödeme emri tebliğ edilmesinden sonra borçlu vekili tarafından hazırlanmıştır. Dilekçedeki vahim hukuki ve usuli hataları tespit ederek gerekçelendiriniz.\n\n***\nANKARA NÖBETÇİ İCRA HUKUK MAHKEMESİNE\nDOSYA NO: Ankara 4. İcra Dairesi 2026/8500 E.\nİTİRAZ EDEN (BORÇLU): Mehmet Kaya\nVEKİLİ: Av. Selin Demir\nALACAKLI: Ahmet Yılmaz\nKONU: Ödeme emrine ve borca itiraz dilekçemizdir.\nAÇIKLAMALAR:\n1- Müvekkil aleyhine yukarıda belirtilen icra dosyasından gönderilen ödeme emri 06.07.2026 tarihinde tebliğ edilmiştir.\n2- Müvekkilin alacaklıya herhangi bir borcu bulunmamaktadır. Bu nedenle borcun tamamına, faizine ve ferilerine açıkça itiraz ediyoruz.\n3- Ayrıca Ankara İcra Daireleri yetkisiz olup, yetkili icra daireleri müvekkilin yerleşim yeri olan İstanbul İcra Daireleridir. Yetkiye de itiraz ediyoruz.\nNETİCE-İ TALEP: İcra takibinin durdurulmasına karar verilmesini talep ederiz. 09.07.2026.\nBorçlu Vekili\nAv. Selin Demir\n***",
            "expected_answer": "Dilekçedeki en vahim hata, genel haciz yoluyla ilamsız icra takibine yapılacak borca ve yetkiye itirazın 'İcra Hukuk Mahkemesi'ne sunulmuş olmasıdır. İİK m. 62 uyarınca genel haciz yolunda itiraz icra dairesine yapılmalıdır. İcra mahkemesine yapılan borca/yetkiye itiraz geçersizdir ve takibi durdurmaz. İkinci hata, talep sonucunda icra dairesinden takibin durdurulmasının istenmesi gerekirken mahkemeden doğrudan karar istenmesidir. Üçüncü olarak, itirazın icra dairesine sunulması gerektiği açıkça belirtilip dilekçe başlığının 'Ankara 4. İcra Dairesi Müdürlüğü'ne' şeklinde düzeltilmesi gerektiği vurgulanmalıdır.",
            "legal_basis": ["İİK m.62"],
            "reference_text": "İİK Madde 62 - İtiraz etmek istiyen borçlu, itirazını, ödeme emrinin tebliği tarihinden itibaren yedi gün içinde dilekçe ile veya sözlü olarak icra dairesine bildirmeye mecburdur...",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "İcra dairesine yapılması gereken itirazın icra mahkemesine yapılması klasiği. Modelin bu usuli tuzağı derhal yakalaması gerekir.",
            "tags": ["hata_yakalama", "itiraz_mercii", "icra_dairesi"]
        },
        {
            "id": "icra_006",
            "area": "icra_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "Alacaklı vekili olarak, borçlu aleyhine ilamsız takip başlattınız ve takip kesinleşti. İcra dairesinden borçlunun taşınır ve taşınmaz mallarının haczini talep etmek istiyorsunuz. Bir meslektaşınız size: 'Tebliğden itibaren 1 yıl içinde haciz istemezsen takip dosyası düşer, ancak 7499 sayılı Kanunla haciz isteme süresi 2 yıla çıkarıldı' demiştir. Meslektaşınızın bu tespiti güncel mevzuata göre doğru mudur? İcra takibinde güncel haciz isteme süresi nedir ve bu sürede haciz istenmezse hukuki sonuç ne olur?",
            "expected_answer": "1. Meslektaşın tespiti yanlıştır. İcra iflas hukukunda haciz isteme süresi İİK m. 78/2 uyarınca ödeme emrinin tebliğinden itibaren 1 yıldır. Bu süre 7499 sayılı Kanunla değiştirilmemiştir (7499 sayılı Kanun ceza usulü ile ilgilidir).\n2. Belirtilen 1 yıllık süre hak düşürücü niteliktedir. Alacaklı bu süre içinde haciz talebinde bulunmazsa, takip dosyası düşer (arşive kaldırılır).\n3. Dosyanın yeniden işleme konulabilmesi için alacaklının yenileme talebinde bulunması gerekir. Yenileme talebi halinde borçluya yeniden yenileme emri gönderilir ve varsa yenileme harcı ödenir. Eski hacizler kalkar.",
            "legal_basis": ["İİK m.78"],
            "reference_text": "İİK Madde 78 - ... Haciz istemek hakkı, ödeme emrinin tebliğ tarihinden itibaren bir sene geçmekle düşer.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "abolished_law",
            "trap_details": "7499 sayılı Kanun ile sürelerin 2 hafta yapılması değişikliği icra sürelerini kapsamaz, haciz isteme süresi halen 1 yıldır. Modelin uydurma mevzuat yorumunu reddetmesi gerekir.",
            "tags": ["haciz_isteme_suresi", "yenileme", "trap"]
        },
        {
            "id": "icra_007",
            "area": "icra_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "6102 sayılı Türk Ticaret Kanunu'na göre emre yazılı senetlerde ciro ile ilgili aşağıdaki ifadelerden hangisi yanlıştır?\nA) Ciro yapılırken ciro tarihinin yazılmaması ciroyu geçersiz kılmaz.\nB) Beyaz ciro, poliçenin arkasına veya alonj üzerine yapılabilir.\nC) Hamiline yazılı ciro beyaz ciro hükmündedir.\nD) Senette daha önce borç altına girmiş kişilere de ciro yapılabilir.\nE) Kısmi ciro mümkündür.",
            "expected_answer": "E",
            "legal_basis": ["TTK m.683/2"],
            "reference_text": "TTK Madde 683 - Cironun kayıtsız şartsız olması gerekir... Kısmi ciro geçersizdir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["ciro", "kambiyo_senedi", "ttk_683", "mcq"]
        },
        {
            "id": "icra_008",
            "area": "icra_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Müvekkil lehine Ankara 3. Asliye Ticaret Mahkemesi'nden 03.07.2026 Cuma günü ihtiyati haciz kararı aldınız. Bu kararın infazını (uygulanmasını) icra dairesinden talep etmek istiyorsunuz. Kanuna göre ihtiyati haciz kararının infazını isteme süresi kaç gündür ve son talep gününüz hangi tarihtir? Araya hafta sonu girmektedir. Adım adım hesaplayınız.",
            "expected_answer": "1. İİK m. 261 uyarınca, alacaklı, ihtiyati haciz kararının verildiği tarihten itibaren 10 gün içinde kararı veren mahkemenin yargı çevresindeki icra dairesinden infazını istemeye mecburdur.\n2. Karar tarihi olan 03.07.2026 Cuma günü hesaba katılmaz. Süre 04.07.2026 Cumartesi günü başlar.\n3. Hafta sonları süre hesabına dahildir. 10 günlük sürenin son günü 13.07.2026 Pazartesi günü mesai saati bitimidir. Bu tarihe kadar infaz talep edilmelidir, aksi halde ihtiyati haciz kararı kendiliğinden hükümsüz kalır.",
            "legal_basis": ["İİK m.261"],
            "reference_text": "İİK Madde 261 - Alacaklı, ihtiyati haciz kararının verildiği tarihten itibaren on gün içinde kararı veren mahkemenin yargı çevresindeki icra dairesinden kararın infazını istemeye mecburdur. Aksi halde ihtiyati haciz kararı kendiliğinden hükümsüz kalır.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["ihtiyati_haciz", "infaz_suresi", "sure_hesabi"]
        },
        {
            "id": "icra_009",
            "area": "icra_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Borçlu B'nin iş yerinde yapılan haciz sırasında, üçüncü kişi Ü, haczedilen malların kendisine ait olduğunu, borçlu B'nin sadece kiracı olduğunu iddia etmiştir. İcra memuru bu iddiayı tutanağa geçirmiştir. Alacaklı ise bu istihkak iddiasına itiraz etmektedir. Üçüncü kişinin istihkak davası açması için kanuni usul nedir ve davasını ne zaman açmalıdır? İstihkak davası açılması takibi kendiliğinden durdurur mu?",
            "expected_answer": "1. İcra memuru haciz tutanağını icra mahkemesine bildirir. İcra mahkemesi takibin talikine (ertelenmesine) veya devamına karar verir (İİK m. 97).\n2. Eğer icra mahkemesi takibin devamına karar verirse, üçüncü kişi malı kurtarmak için kararın tebliğinden itibaren 7 gün içinde İcra Mahkemesinde istihkak davası açmalıdır.\n3. İstihkak davası açılması icra takibini kendiliğinden durdurmaz. Ancak davacı üçüncü kişi, teminat karşılığında icra mahkemesinden takibin durdurulması yönünde ihtiyati tedbir benzeri bir erteleme kararı talep edebilir.",
            "legal_basis": ["İİK m.97"],
            "reference_text": "İİK Madde 97 - ... Üçüncü şahıs, takibin talikine karar verilirse takibin ertelenmesi kararının icra dairesince kendisine bildirildiği tarihten; takibin devamına karar verilirse, icra mahkemesi kararının kendisine tefhim veya tebliği tarihinden itibaren yedi gün içinde icra mahkemesinde istihkak davası açmaya mecburdur... İstihkak davasının açılması takibi durdurmaz...",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["istihkak", "istihkak_davasi", "icra_takibi"]
        },
        {
            "id": "icra_010",
            "area": "icra_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L4",
            "question": "Müvekkil borçlu Caner Aslan aleyhine, hamili olduğu 15.05.2026 vade tarihli 50.000 TL'lik bir bonoya dayalı olarak Ankara 8. İcra Dairesi'nde kambiyo senetlerine mahsus haciz yoluyla icra takibi (Örnek No: 10) başlatılmıştır. Ödeme emri müvekkile 06.07.2026 tarihinde tebliğ edilmiştir. Ancak müvekkil bu bononun altındaki imzanın kesinlikle kendisine ait olmadığını, alacaklıyı hiç tanımadığını beyan etmektedir. İmzaya itiraz etmek amacıyla İcra Mahkemesine sunulacak, takibi durdurma talepli dava dilekçesini yazınız.",
            "expected_answer": "Dilekçe başlığı: ANKARA NÖBETÇİ İCRA HUKUK MAHKEMESİNE\nDavacı (Borçlu): Caner Aslan (TCKN, Adres)\nDavalı (Alacaklı): ... (Takipteki alacaklı)\nKonu: Ankara 8. İcra Müdürlüğü'nün 2026/... E. sayılı dosyasına ve kambiyo senedindeki imzaya açık itirazımız ile takibin durdurulması talebimiz.\nSüre: Tebliğ 06.07.2026, dilekçe tarihi 09.07.2026 (5 günlük yasal süre içinde).\nAçıklama: Takibe konu edilen bonodaki imza müvekkile ait değildir. İmza incelemesi yapılmasını, takibin İİK m. 169/a-2 uyarınca geçici olarak durdurulmasını talep ederiz.\nNetice-i Talep: İtirazımızın kabulüyle imzanın müvekkile ait olmadığının tespitine, takibin muvakkaten durdurulmasına, takibin iptaline ve alacaklının kötü niyet tazminatına mahkum edilmesine.",
            "legal_basis": ["İİK m.168/4", "İİK m.170"],
            "reference_text": "İİK Madde 170 - Borçlu, 168 inci maddenin 4 üncü bendine göre sunacağı dilekçe ile imzaya itiraz edebilir... İcra mahkemesi duruşmadan önce yapacağı incelemede, borçlunun itiraz dilekçesine eklediği belgelerden... imzanın borçluya ait olmadığı kanaatini edinirse takibin geçici olarak durdurulmasına karar verir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["imzaya_itiraz", "kambiyo_takibi", "belge_uretimi"]
        }
    ]

    with open("data/questions/icra.jsonl", "w", encoding="utf-8") as f:
        for q in icra_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # 2. KİRA HUKUKU (kira.jsonl)
    kira_questions = [
        {
            "id": "kira_001",
            "area": "kira_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "15.09.2026 tarihinde sona erecek 1 yıllık belirli süreli konut kira sözleşmesinde, kiraya veren sözleşmeyi sürenin bitimi nedeniyle sona erdirmek istemektedir. Türk Borçlar Kanunu'na göre kiraya verenin fesih bildirimi yapma süresi ve şartları nelerdir? Fesih bildirimi en geç hangi tarihe kadar kiracıya ulaşmış olmalıdır? Adım adım açıklayınız.",
            "expected_answer": "1. TBK m. 347/1 uyarınca, konut ve çatılı işyeri kiralarında kiracı, belirli süreli sözleşmelerin süresinin bitiminden en az onbeş gün önce bildirimde bulunmadıkça, sözleşme aynı koşullarla bir yıl uzatılmış sayılır.\n2. Kiraya veren ise ancak 10 yıllık uzama süresi sonunda bu yolla sözleşmeyi feshedebilir. Sözleşmenin ilk 1 yıllık süresinin bitiminde (15.09.2026) kiraya verenin sadece 'süre bitti' diyerek sözleşmeyi feshetme hakkı yoktur. Dolayısıyla kiraya veren fesih bildirimi yapsa dahi bu hukuken geçersizdir.\n3. Bu durum bir yasal kuraldır. Dolayısıyla son fesih tarihi hesabı kiraya veren yönünden yapılamaz (hak doğmamıştır).",
            "legal_basis": ["TBK m.347"],
            "reference_text": "TBK Madde 347 - Konut ve çatılı işyeri kiralarında kiracı, belirli süreli sözleşmelerin süresinin bitiminden en az onbeş gün önce bildirimde bulunmadıkça, sözleşme aynı koşullarla bir yıl uzatılmış sayılır. Kiraya veren, sözleşme süresinin bitimine dayanarak sözleşmeyi sona erdiremez.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Kiraya verenin belirli süreli kira sözleşmesini süre sonunda serbestçe feshedemeyeceği kuralı. Modelin 15 gün hesabını kiraya veren için yapmayıp yasal engeli belirtmesi gerekir.",
            "tags": ["kira_feshi", "belirli_sure", "sure_hesabi"]
        },
        {
            "id": "kira_002",
            "area": "kira_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "Bir konut kira sözleşmesinde yer alan 'Kira bedelinin iki ay üst üste ödenmemesi halinde sonraki ayların kiraları muaccel (peşin ödenebilir) hale gelir' şeklindeki muacceliyet şartının yasal geçerliliği hakkında aşağıdakilerden hangisi doğrudur?\nA) Tamamen geçerlidir ve kiracı süre sonunda borcun tamamından sorumlu olur.\nB) Sadece işyeri kiralarında geçerlidir, konut kiralarında kesin olarak geçersizdir.\nC) Kiracının tacir olup olmadığına bakılmaksızın tüm konut ve çatılı işyeri kiralarında kesinlikle geçersizdir (batıldır).\nD) Sadece kira bedeli 50.000 TL'nin altındaki sözleşmelerde geçersizdir.\nE) İcra takibi başlatılması halinde icra dairesinin kararıyla geçerli hale gelir.",
            "expected_answer": "C",
            "legal_basis": ["TBK m.346"],
            "reference_text": "TBK Madde 346 - Kiracıya, kira bedeli ve yan giderler dışında başka bir ödeme yükümlülüğü getirilemez. Özellikle, kira bedelinin zamanında ödenmemesi hâlinde ceza koşulu ödeneceğine veya sonraki kira bedellerinin muaccel olacağına ilişkin anlaşmalar geçersizdir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["muacceliyet", "kiraci_korumasi", "tbk_346", "mcq"]
        },
        {
            "id": "kira_003",
            "area": "kira_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Kiracı K, site ortak gideri ve apartman aidat borçlarını ödememektedir. Ev sahibi V, aidat borçlarını apartman yönetimine kendisi ödemiştir. Ev sahibi V vekili olarak kiracı K'yi bu sebeple evden tahliye etmek istiyoruz. Hangi hukuki yola başvurabiliriz? Gönderilecek ihtarnamede verilecek süre nedir ve bu sebeple 'İki Haklı İhtar' nedeniyle tahliye davası açılması mümkün müdür?",
            "expected_answer": "1. Ev sahibi, ödenmeyen aidat borçları nedeniyle TBK m. 315 uyarınca kiracıya en az 30 günlük ödeme süresi veren yazılı bir temerrüt ihtarı veya icra dairesi aracılığıyla tahliye talepli ödeme emri (Örnek No: 13) gönderebilir.\n2. Kiracı bu 30 günlük süre içinde aidat borcunu ödemezse temerrüt gerçekleşir ve ev sahibi icra mahkemesinde veya sulh hukuk mahkemesinde tahliye davası açabilir.\n3. Aidat veya yan gider borçları 'İki Haklı İhtar' (TBK m. 352/2) tahliye davasına konu edilemez. İki haklı ihtarın konusu yalnızca ödenmeyen kira bedelleridir.",
            "legal_basis": ["TBK m.315", "TBK m.352/2"],
            "reference_text": "TBK Madde 315 - Kiracı, kiralananın tesliminden sonra muaccel olan kira bedelini veya yan gideri ödeme borcunu ifa etmezse... kiracıya yazılı olarak bir süre verip... feshedeceğini bildirebilir... konut ve çatılı işyeri kiralarında ise en az otuz gündür.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["aidat_borcu", "temerrut_tahliye", "tbk_315", "somut_olay"]
        },
        {
            "id": "kira_004",
            "area": "kira_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Kiraya veren müvekkil Sinan Aydın'ın, kiracısı Burak Demir'e (Kadıköy/İstanbul adresindeki konut) 2026 yılı Mayıs ve Haziran aylarına ait toplam 40.000 TL kira borcu nedeniyle TBK m. 315 kapsamında temerrüt ihtarnamesi çekmek istiyoruz. İhtarnamede yasal ödeme süresinin verilmesi ve ödenmemesi halinde kira sözleşmesinin feshedilerek tahliye davası açılacağı ihtarı yer almalıdır. Bu ihtarnameyi noter kanalıyla gönderilecek şekilde hukuki dile uygun taslak olarak hazırlayınız.",
            "expected_answer": "İhtarname Başlığı: İHTARNAME\nİhtar Eden: Sinan Aydın (TCKN, Adres)\nVekili: Av. ...\nİhtar Edilen: Burak Demir (Adres)\nKonu: 2026 yılı Mayıs ve Haziran ayları kira bedellerinin ödenmesi ve temerrüt ihtarı.\nAçıklamalar: Kadıköy adresindeki konutta kiracı olduğunuz, Mayıs ve Haziran aylarına ait her biri 20.000 TL olan toplam 40.000 TL kira bedelini ödemediğiniz tespit edilmiştir. \nİhtar ve Talep: İşbu ihtarnamenin tebliğinden itibaren TBK m. 315 uyarınca 30 gün içinde toplam 40.000 TL borcu belirtilen IBAN hesabına ödemenizi, aksi takdirde süre sonunda kira sözleşmesinin feshedileceğini ve aleyhinize tahliye ile alacak davası açılacağını ihtar ederiz.",
            "legal_basis": ["TBK m.315"],
            "reference_text": "TBK Madde 315 - Kiracı, kiralananın tesliminden sonra muaccel olan kira bedelini veya yan gideri ödeme borcunu ifa etmezse, kiraya veren kiracıya yazılı olarak bir süre verip, bu sürede de ifa etmeme durumunda, sözleşmeyi feshedeceğini bildirebilir. Kiracıya verilecek süre en az on gün, konut ve çatılı işyeri kiralarında ise en az otuz gündür.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["temerrut_ihtari", "tbk_315", "belge_uretimi"]
        },
        {
            "id": "kira_005",
            "area": "kira_hukuku",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Aşağıdaki dava dilekçesi paragrafındaki arıza bedelinin kiradan mahsup edilmesine ilişkin hukuki hatayı bularak analiz ediniz.\n\n***\n... Müvekkil kiracı, evdeki kombinin bozulması üzerine acil olarak 10.000 TL ödeyerek tamir ettirmiştir. Tamir faturasını kiraya verene bildirmiş, ancak kiraya veren ödeme yapmadığından, müvekkil bu 10.000 TL tamir bedelini sonraki ayın kira bedelinden tek taraflı olarak düşerek eksik kira yatırmıştır. Bu işlem hukuka uygun olduğundan temerrüt oluşmamıştır...\n***",
            "expected_answer": "Dilekçedeki hata, kiracının kombi arıza bedelini kiraya verenin yazılı onayı veya mahkeme kararı olmaksızın tek taraflı olarak kiradan mahsup etmesinin hukuka uygun olduğunun iddia edilmesidir.\n1. Kiracı, acil arızaları tamir ettirse dahi, bedeli ev sahibinin onayı veya mahkeme kararı olmadan doğrudan kiradan düşemez.\n2. Tek taraflı mahsup halinde 'eksik kira ödemesi' gerçekleşmiş olur ve ev sahibinin temerrüt nedeniyle (TBK m. 315) tahliye davası açma hakkı doğar. Hukuki risk büyüktür.",
            "legal_basis": ["TBK m.315", "TBK m.306"],
            "reference_text": "TBK Madde 306 - Kiraya veren, kiralananın ayıplı olduğunu öğrenirse... ayıbı gidermekle yükümlüdür... Kiracı, ayıbın giderilmesini... veya kira bedelinden... indirim yapılmasını isteyebilir.",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Kiracının arıza bedelini tek taraflı mahsup ederek eksik kira ödemesi temerrüt nedenidir. Modelin bu hukuki riski yakalaması gerekir.",
            "tags": ["mahsup_hatasi", "kombi_arizasi", "tbk_315", "hata_yakalama"]
        },
        {
            "id": "kira_006",
            "area": "kira_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "Kira borcu nedeniyle tahliye talepli icra takibi başlatılan kiracı, 30 günlük yasal süre içinde borcun neredeyse tamamını ödemiş ancak sadece 0,35 TL (otuz beş kuruş) gibi çok küçük bir tutarı eksik bırakmıştır. 30 günlük süre geçtikten sonra alacaklı vekili olarak eksik ödeme nedeniyle icra mahkemesinden kiracının tahliyesini talep edebilir miyiz? Yargıtay'ın bu konudaki yerleşik yaklaşımını açıklayınız.",
            "expected_answer": "1. Evet, icra mahkemesinden kiracının tahliyesi talep edilebilir ve mahkemece tahliye kararı verilmelidir.\n2. Yargıtay'ın yerleşik içtihatlarına göre, temerrüde engel olunabilmesi için borcun 30 günlük yasal süre içinde 'kuruşu kuruşuna, tam ve eksiksiz' ödenmesi şarttır.\n3. Miktarın çok küçük olması (0,35 TL otuz beş kuruş dahi olsa) sonucu değiştirmez; tam ifa gerçekleşmediğinden temerrüt olgusu gerçekleşir ve tahliye kararı verilir.",
            "legal_basis": ["TBK m.315", "İİK m.269/a"],
            "reference_text": "İİK Madde 269/a - Borçlu ihtarnamenin tebliğinden itibaren otuz gün içinde borcu ödemezse... alacaklı icra mahkemesinden tahliye talep edebilir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["eksik_odeme", "kurus_farki", "temerrut_tahliye", "somut_olay"]
        },
        {
            "id": "kira_007",
            "area": "kira_hukuku",
            "task_type": "mcq",
            "difficulty": "L3",
            "question": "Kira sözleşmesinde taraf olmayan eşin, aile konutu olan taşınmaza ilişkin eşinin verdiği tahliye taahhüdüne itiraz ederek tahliyeyi engelleyebilmesi için en geç hangi ana kadar durumu kiraya verene yazılı olarak bildirmiş olması şarttır?\nA) İcra takibi başlatılana kadar\nB) Tahliye davasında karar verilene kadar\nC) Tahliye emri kiracıya tebliğ edilene kadar\nD) Taşınmaz fiilen tahliye edilene kadar\nE) Sözleşme süresi bitene kadar",
            "expected_answer": "A",
            "legal_basis": ["TMK m.194", "TBK m.349"],
            "reference_text": "Yargıtay içtihatları uyarınca, kira sözleşmesinin tarafı olmayan eşin aile konutu korumasından yararlanarak tahliyeyi engelleyebilmesi için icra takibinden önce kiraya verene aile konutu bildiriminde bulunmuş olması veya davaya dahil olması şarttır.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["aile_konutu", "tahliye_taahhudu", "tmk_194", "mcq"]
        },
        {
            "id": "kira_008",
            "area": "kira_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Kiracı K, kiralananı 01.07.2026 tarihinde tahliye edeceğini yazılı olarak taahhüt etmiştir. Ancak bu tarihte evi boşaltmamıştır. Kiraya veren V vekili olarak, bu tahliye taahhüdüne dayanarak icra takibi başlatmak veya dava açmak istiyoruz. Kanuni süremiz kaç gündür/aydır ve takip/dava açabileceğimiz son gün hangi tarihtir? Resmi tatilleri gözeterek hesaplayınız.",
            "expected_answer": "1. TBK m. 352/1 uyarınca, tahliye taahhüdüne dayalı tahliye davası veya tahliye talepli icra takibi, taahhüt edilen tahliye tarihinden (01.07.2026) itibaren 'bir ay' içinde açılmalıdır.\n2. Süre 02.07.2026 tarihinde başlar. Bir aylık sürenin son günü 01.08.2026 Cumartesi günüdür.\n3. Ancak 01.08.2026 Cumartesi gününe ve takip eden Pazar gününe denk geldiği için, ayrıca adli tatil (20 Temmuz - 31 Ağustos) kapsamında değerlendirilse dahi, icra takipleri adli tatilde durmadığından resmi tatil uzaması uygulanır. \n4. Cumartesi/Pazar resmi tatil olduğundan süre ilk mesai günü olan 03.08.2026 Pazartesi mesai bitimine kadar uzar (UYAP'ta 23:59). Not: İcra takibi adli tatilde durmadığı için adli tatil sonuna (Eylül'e) uzamaz. Modelin bunu ayırt etmesi önemlidir.",
            "legal_basis": ["TBK m.352/1", "İİK m.19", "HMK m.93"],
            "reference_text": "TBK Madde 352 - ... boşaltmayı yazılı olarak üstlendiği halde boşaltmamışsa kiraya veren, kira sözleşmesini bu tarihten başlayarak bir ay içinde icraya başvurmak veya dava açmak suretiyle sona erdirebilir.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["tahliye_taahhudu", "icra_takibi", "sure_hesabi"]
        },
        {
            "id": "kira_009",
            "area": "kira_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Evini satmak veya yeniden kiraya vermek isteyen ev sahibine karşı kiracının evi potansiyel alıcılara gösterme yükümlülüğü (TBK m. 319) kapsamı nedir? Kiracı evi göstermekten kaçınırsa ev sahibi doğrudan tahliye davası açabilir mi? Uyuşmazlık halinde ev sahibinin izlemesi gereken hukuki yol nedir?",
            "expected_answer": "1. TBK m. 319 uyarınca kiracı, kiralananın satışa çıkarılması veya yeniden kiralanması halinde potansiyel alıcıların/kiracı adaylarının evi gezmesine izin vermekle yükümlüdür. Ancak bu ziyaretlerin kiracının düzenini bozmayacak şekilde makul gün ve saatlerde yapılması gerekir.\n2. Kiracının evi göstermekten imtina etmesi tek başına doğrudan bir tahliye sebebi (akde aykırılık nedeniyle fesih) oluşturmaz.\n3. Ev sahibinin Sulh Hukuk Mahkemesine başvurarak 'Kiralananın Gösterilmesine İzin Verilmesi (Evi Göstermeye İzin)' davası açması ve mahkemeden makul gün/saat belirleyen bir karar alması gerekir.",
            "legal_basis": ["TBK m.319"],
            "reference_text": "TBK Madde 319 - ... Kiracı, bakım, satış veya sonraki kiralama için zorunlu olduğu ölçüde, kiraya verenin ve onun belirlediği üçüncü kişinin kiralananı gezip görmesine izin vermekle yükümlüdür. Kiraya veren, çalışmaları ve kiralananın gezilip görüleceğini kiracıya uygun bir süre önce bildirmek ve bunları yaparken kiracının yararlarını göz önünde tutmak zorundadır.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["evi_gosterme", "tahliye_engeli", "tbk_319", "somut_olay"]
        },
        {
            "id": "kira_010",
            "area": "kira_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Kiraya veren müvekkil Ayşe Kara, kiracısı Mehmet Yurt'un yazılı tahliye taahhüdüne dayanarak Ankara İcra Dairelerinde tahliye talepli icra takibi (Örnek No: 14 Tahliye Emri gönderilmesi talepli) başlatmak istemektedir. Taahhüt edilen tahliye tarihi 15.06.2026'dır. Takip talebi bugün (09.07.2026) açılacaktır. İcra müdürlüğüne sunulacak Takip Talebindeki tahliyeye ilişkin yasal ve zorunlu açıklamaları içeren kısmı taslak olarak hazırlayınız.",
            "expected_answer": "İcra Takip Talebinde (Örnek No: 1) Yer Alacak İlgili Kısımlar:\n- Takip Yolu: Yazılı mukaveleye müstenit tahliye (İİK m. 272 uyarınca tahliye taahhüdüne dayalı tahliye takibi).\n- Borçluya Gönderilecek Ödeme/Tahliye Emri: Örnek No: 14 Tahliye Emri.\n- Alacak Kalemi / Talep: Borçlunun Çankaya/Ankara adresindeki taşınmazı 15.06.2026 tahliye tarihli adi yazılı tahliye taahhütnamesi uyarınca tahliye ve teslim etmesi talebimizdir.\n- Belgeler: 15.06.2026 tarihli tahliye taahhütnamesi aslı (veya onaylı örneği).\nNot: Takip süresi olan 1 ay geçirilmemiştir.",
            "legal_basis": ["İİK m.272", "TBK m.352/1"],
            "reference_text": "İİK Madde 272 - Mukavelename ile kiralanan bir taşınmazın müddeti bittikten sonra mukavele sahibi olan kiralayan, ihbara hacet kalmadan bunun tahliyesini istiyebilir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["takip_talebi", "tahliye_takibi", "belge_uretimi"]
        }
    ]

    with open("data/questions/kira.jsonl", "w", encoding="utf-8") as f:
        for q in kira_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # 3. İŞ HUKUKU (is_hukuku.jsonl)
    is_questions = [
        {
            "id": "is_001",
            "area": "is_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "Müvekkil işçinin iş sözleşmesi işveren tarafından 01.07.2026 tarihinde feshedilmiştir. İşçi işe iade davası açmak istemektedir. İşe iade davası öncesinde zorunlu arabuluculuk başvuru süresi kaç gündür/aydır ve son başvuru günümüz hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "1. İş Kanunu m. 20 uyarınca, iş sözleşmesi feshedilen işçi, fesih bildiriminin tebliği tarihinden itibaren 'bir ay' içinde işe iade talebiyle arabulucuya başvurmak zorundadır.\n2. Fesih tarihi olan 01.07.2026 günü hesaba katılmaz. Süre 02.07.2026 tarihinde başlar.\n3. Bir aylık süre 01.08.2026 tarihinde sona erer. \n4. 01.08.2026 Cumartesi gününe denk geldiği için, resmi tatil uzaması nedeniyle son başvuru günü ilk mesai günü olan 03.08.2026 Pazartesi günü mesai bitimidir (arabuluculuk bürosu kapanış saati) veya UYAP/e-devlet üzerinden yapılacaksa saat 23:59'dur.",
            "legal_basis": ["İş K. m.20"],
            "reference_text": "İş Kanunu Madde 20 - İş sözleşmesi feshedilen işçi, fesih bildiriminde sebep gösterilmediği veya gösterilen sebebin geçerli bir sebep olmadığı iddiası ile fesih bildiriminin tebliği tarihinden itibaren bir ay içinde işe iade talebiyle, arabulucuya başvurmak zorundadır.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["ise_iade", "arabuluculuk_suresi", "sure_hesabi"]
        },
        {
            "id": "is_002",
            "area": "is_hukuku",
            "task_type": "mcq",
            "difficulty": "L1",
            "question": "İş Kanunu'na göre, kıdem ve ihbar tazminatı ile yıllık izin ücreti alacaklarında zamanaşımı süresi kaç yıldır?\nA) 1 yıl\nB) 2 yıl\nC) 5 yıl\nD) 10 yıl\nE) Zamanaşımına tabi değildir",
            "expected_answer": "C",
            "legal_basis": ["İş K. Ek Madde 3"],
            "reference_text": "İş Kanunu Ek Madde 3 - İş sözleşmesinden kaynaklanmak şartıyla ... kıdem tazminatı, ihbar tazminatı, yıllık izin ücreti ... zamanaşımı süresi beş yıldır.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["zamanasimi", "kidem_tazminati", "mcq"]
        },
        {
            "id": "is_003",
            "area": "is_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "İşçi İ, iş yerinde kendisine yönelik ağır hakaret ve küfürler edildiğini 01.07.2026 tarihinde öğrenmiştir. İşçi bu nedenle iş sözleşmesini haklı nedenle derhal feshetmek istemektedir. Kanuna göre derhal fesih hakkını kullanma süresi ne kadardır? Bu hak en geç hangi tarihe kadar kullanılmalıdır? Bu süre geçirildikten sonra yapılan feshin hukuki sonucu ne olur?",
            "expected_answer": "1. İş Kanunu m. 26 uyarınca, ahlak ve iyi niyet kurallarına uymayan hallere dayanarak işçi veya işveren için tanınan sözleşmeyi derhal fesih yetkisi, bu çeşit davranışlarda bulunduğunu diğer tarafın öğrendiği günden başlayarak 'altı iş günü' geçtikten ve herhalde fiilin gerçekleşmesinden itibaren bir yıl sonra kullanılamaz.\n2. Olayın öğrenildiği gün (01.07.2026 Perşembe) hesaba katılmaz. Süre 02.07.2026 Cuma günü başlar. Pazar günleri iş günü sayılmaz. Cumartesi günü iş yerinde çalışılıyorsa iş günü sayılır. Standart 5 günlük çalışma varsa Cumartesi/Pazar hariç tutulabilir, ancak genel kuralda Cumartesi iş günü sayılır.\n- 02.07 Cuma (1. gün)\n- 03.07 Cumartesi (2. gün)\n- 05.07 Pazartesi (3. gün)\n- 06.07 Salı (4. gün)\n- 07.07 Çarşamba (5. gün)\n- 08.07 Perşembe (6. gün). Fesih en geç 08.07.2026 tarihine kadar yapılmalıdır.\n3. Hak düşürücü süre geçtikten sonra yapılan fesih haksız fesih sayılır, işçi ihbar tazminatı talep edemez.",
            "legal_basis": ["İş K. m.24/II", "İş K. m.26"],
            "reference_text": "İş Kanunu Madde 26 - 24 ve 25 inci maddelerde gösterilen ahlak ve iyiniyet kurallarına uymayan hallere dayanarak işçi veya işveren için tanınmış olan sözleşmeyi fesih yetkisi, iki taraftan birinin bu çeşit davranışlarda bulunduğunu diğer tarafın öğrendiği günden başlayarak altı işgünü geçtikten ve her halde fiilin vukuundan itibaren bir sene sonra kullanılamaz.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["derhal_fesih", "altı_is_gunu", "hak_dusurucu_sure"]
        },
        {
            "id": "is_004",
            "area": "is_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "İşveren müvekkil ABC Ltd. Şti.'nin işçisi Hakan Koç, 06.07.2026 Pazartesi ve 07.07.2026 Salı günleri işverenden izin almadan ve haklı bir nedeni olmaksızın işe gelmemiştir. İş sözleşmesini haklı nedenle (İş K. m. 25/II-g uyarınca) feshetmeden önce, işçiye devamsızlık nedenini açıklaması ve varsa mazeretini sunması için noter vasıtasıyla devamsızlık ihtarnamesi çekilecektir. Bu ihtarnameyi hazırlayınız.",
            "expected_answer": "İhtarname Başlığı: İHTARNAME\nİhtar Eden: ABC Ltd. Şti. (Vergi No, Adres)\nVekili: Av. ...\nİhtar Edilen: Hakan Koç (TCKN, Adres)\nKonu: Devamsızlık nedeniyle mazeret bildirme ihtarı.\nAçıklamalar: Şirketimiz nezdinde çalışmakta iken 06.07.2026 Pazartesi ve 07.07.2026 Salı günleri mesai saatlerinde işe gelmediğiniz ve devamsızlık yaptığınız tespit edilmiştir.\nİhtar ve Talep: İşbu ihtarnamenin tebliğinden itibaren 3 (üç) gün içinde işe gelmeme nedeninizi gösterir yasal ve geçerli bir mazeret belgesini şirketimize ibraz etmenizi, aksi takdirde iş sözleşmenizin İş Kanunu m. 25/II-g uyarınca bildirimsiz ve tazminatsız olarak feshedileceğini ihtar ederiz.",
            "legal_basis": ["İş K. m.25/II-g"],
            "reference_text": "İş Kanunu Madde 25 - ... g) İşçinin işverenden izin almaksızın veya haklı bir sebebe dayanmaksızın ardı ardına iki işgünü veya bir ay içinde iki defa herhangi bir tatil gününden sonraki iş günü, yahut bir ayda üç işgünü işine devam etmemesi.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["devamsizlik", "ihtarname", "belge_uretimi"]
        },
        {
            "id": "is_005",
            "area": "is_hukuku",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Aşağıdaki işe iade davası dava dilekçesindeki usuli ve süreye ilişkin hatayı bularak analiz ediniz.\n\n***\nİSTANBUL NÖBETÇİ İŞ MAHKEMESİNE\nDAVACI: Mehmet Şen\nVEKİLİ: Av. Can Tekin\nDAVALI: XYZ Tekstil A.Ş.\nKONU: İşe iade ve tazminat talebimizdir.\nAÇIKLAMALAR:\n1- Müvekkilin iş sözleşmesi davalı işveren tarafından 01.06.2026 tarihinde haksız ve geçersiz gerekçelerle feshedilmiştir.\n2- Bunun üzerine süresi içinde 15.06.2026 tarihinde arabuluculuk başvurusunda bulunulmuştur. \n3- Arabuluculuk görüşmelerinde anlaşma sağlanamamış ve arabuluculuk son tutanağı 25.06.2026 tarihinde imzalanmıştır.\n4- Arabuluculuk son tutanağının düzenlendiği tarihten itibaren yasal 30 günlük süre içerisinde işbu davayı ikame etmekteyiz.\nNETİCE-İ TALEP: Feshin geçersizliğinin tespitiyle müvekkilin işe iadesine karar verilmesini talep ederiz. 22.07.2026. Davacı Vekili Av. Can Tekin\n***",
            "expected_answer": "Dilekçedeki temel hata dava açma süresine ilişkindir. \n1. İş Kanunu m. 20 uyarınca, arabuluculuk faaliyeti sonunda anlaşmaya varılamaması halinde, son tutanağın düzenlendiği tarihten itibaren 'iki hafta' içinde iş mahkemesinde dava açılması gerekir.\n2. Dilekçede yasal sürenin '30 gün' olduğu belirtilmiş ve dava 22.07.2026 tarihinde açılmıştır. \n3. Arabuluculuk son tutanağı 25.06.2026'da düzenlendiğine göre, 2 haftalık dava açma süresi 09.07.2026 tarihinde sona ermiştir. Dava 22.07.2026'da açıldığı için süre aşımı nedeniyle dava reddedilecektir. Modelin bu 2 haftalık süreyi net belirtmesi gerekir.",
            "legal_basis": ["İş K. m.20/1", "HUAK m.18/A"],
            "reference_text": "İş Kanunu Madde 20 - ... Arabuluculuk faaliyeti sonunda anlaşmaya varılamaması hâlinde, son tutanağın düzenlendiği tarihten itibaren, iki hafta içinde iş mahkemesinde dava açılabilir.",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "İşe iade davasında arabuluculuk son tutanağından sonra dava açma süresinin 2 hafta yerine 30 gün sanılması hatası. Model bunu tespit etmelidir.",
            "tags": ["ise_iade_suresi", "arabuluculuk_son_tutanak", "hata_yakalama"]
        },
        {
            "id": "is_006",
            "area": "is_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "İşçi müvekkil İ, 5 yıldır çalıştığı iş yerinde aylık 40.000 TL net maaş aldığını ancak SGK primlerinin asgari ücret üzerinden yatırıldığını, ayrıca fazla mesai ücretlerinin ödenmediğini iddia etmektedir. Elimizde yazılı bir belge veya bordro yoktur. İşveren ise işçinin imzaladığı ve üzerinde 'tüm haklarımı aldım, fazla çalışma yapmadım' yazan aylık bordroları mahkemeye sunacağını söylemektedir. Avukat olarak fazla mesai alacağı ve SGK matrahının tespiti açısından ispat yükünü ve davanın başarısını nasıl değerlendirirsiniz? Yazılı bordroların bağlayıcılığı karşısında ne yapmalıyız?",
            "expected_answer": "1. SGK matrahının tespiti (Ücret tespiti): İşçinin gerçek ücretinin tespiti için emsal ücret araştırması talep edilir. TÜİK, ilgili meslek odaları ve sendikalardan emsal ücret istenir. SGK kayıtlarının aksini işçi her türlü delille (tanık dahil) ispatlayabilir.\n2. Fazla Çalışma Alacağı ve İmzalı Bordrolar: Yargıtay içtihatlarına göre, işçinin ihtirazı kayıt koymadan imzaladığı bordroda fazla mesai sütunu bulunuyor ve orada '0' yazıyorsa veya boşsa ve işçi bordroyu imzalamışsa, bordronun aksini ancak yazılı delille ispatlayabilir (tanık dinletemez). Ancak eğer bordrolarda fazla çalışma tahakkuku yapılmış ve ödenmişse, işçi bunun üzerinde fazla çalışma yaptığını yine yazılı delille ispatlamalıdır. Eğer bordroda hiç fazla çalışma hanesi yoksa veya imzasızsa tanıkla ispat mümkündür.\n3. Stratejik Yol Haritası: Müvekkilin imzaladığı bordroların içerik analizi yapılmalı, banka ödeme kayıtları ile karşılaştırılmalıdır. Banka kanalıyla ödenen ücret bordrodan yüksekse aradaki fark ispat aracı yapılabilir.",
            "legal_basis": ["HMK m.200", "İş K. m.41", "Yargıtay 9. HD Yerleşik İçtihatları"],
            "reference_text": "Yargıtay İçtihadı: İmzalı ücret bordrolarında fazla çalışma ücreti ödendiği anlaşılıyorsa, işçi tarafından gerçekte daha fazla çalışma yapıldığının ileri sürülmesi durumunda, bordronun aksinin ancak yazılı delille ispatı gerekir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "İmzalı bordronun fazla mesaideki bağlayıcılık kuralı. Modelin tanık dinletilemeyeceği ayrımını bilmesi gerekir.",
            "tags": ["fazla_mesai", "imzali_bordro", "ispat_yuku"]
        },
        {
            "id": "is_007",
            "area": "is_hukuku",
            "task_type": "mcq",
            "difficulty": "L1",
            "question": "4857 sayılı İş Kanunu’na göre kadın işçilere bir yaşından küçük çocuklarını emzirmeleri için günlük çalışma süresinden sayılmak üzere kural olarak günde toplam kaç saat süt izni verilir?\nA) 1\nB) 1,5\nC) 2\nD) 2,5\nE) 3",
            "expected_answer": "B",
            "legal_basis": ["İş K. m.74/7"],
            "reference_text": "İş Kanunu Madde 74 - ... Kadın işçilere bir yaşından küçük çocuklarını emzirmeleri için günde toplam bir buçuk saat süt izni verilir. Bu sürenin hangi saatler arasında ve kaça bölünerek kullanılacağını işçi kendisi belirler. Bu süre günlük çalışma süresinden sayılır.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["sut_izni", "kadin_isçi", "is_74", "mcq"]
        },
        {
            "id": "is_008",
            "area": "is_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "İşe iade talebiyle yapılan arabuluculuk görüşmeleri sonucunda anlaşma sağlanamamış ve son tutanak arabulucu tarafından 10.07.2026 Cuma günü düzenlenerek taraflarca imzalanmıştır. Bu durumda işe iade davası açmak için 2 haftalık hak düşürücü sürenin son günü hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "1. İş Kanunu m. 20 ve HUAK m. 18/A uyarınca, arabuluculuk son tutanağının düzenlendiği tarihten itibaren 'iki hafta' içinde iş mahkemesinde dava açılması gerekir.\n2. Son tutanak tarihi olan 10.07.2026 Cuma günü hesaba katılmaz. Süre 11.07.2026 Cumartesi günü başlar.\n3. İki haftalık (14 günlük) sürenin son günü 24.07.2026 Cuma günüdür. Bu tarih mesai saati bitimine kadar dava açılmalıdır. UYAP üzerinden ise 23:59'a kadar açılabilir.",
            "legal_basis": ["İş K. m.20/1", "HMK m.91", "HMK m.92"],
            "reference_text": "HMK Madde 92 - Süre gün olarak belirlenmiş ise tebliğ edildiği gün hesaba katılmaz ve süre son günün tatil saatinde biter. Süre hafta olarak belirlenmişse başladığı güne son hafta içindeki karşılık gelen günde biter.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["ise_iade_suresi", "arabuluculuk_son_tutanak", "sure_hesabi"]
        },
        {
            "id": "is_009",
            "area": "is_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "İşveren, Ankara'daki şubesinde çalışan işçi İ'nin çalışma yerini tek taraflı bir kararla İstanbul şubesi olarak değiştirmiştir. İş sözleşmesinde nakil yetkisi bulunmamaktadır. İşçiye bu durum 01.07.2026 tarihinde yazılı olarak bildirilmiştir. İşçi bu değişikliği kabul etmek istememektedir. İş Kanunu m. 22 uyarınca işçinin cevap verme süresi ne kadadır? İşçinin sessiz kalması durumunda değişiklik geçerli olur mu ve işveren işçiyi işten çıkarırsa işçi ne talep edebilir?",
            "expected_answer": "1. İş Kanunu m. 22 uyarınca, çalışma koşullarında esaslı değişiklik ancak işçiye yazılı olarak bildirilmek suretiyle yapılabilir. İşçi, değişiklik önerisini tebliğden itibaren 'altı iş günü' içinde yazılı olarak kabul etmelidir.\n2. İşçi sessiz kalırsa veya yazılı olarak kabul etmezse, değişiklik önerisi kabul edilmemiş sayılır (sessiz kalmak ret anlamına gelir).\n3. İşçi kabul etmezse işveren sözleşmeyi feshedebilir. Bu durumda işçi feshin geçersizliği ve işe iade davası açabilir veya şartları varsa kıdem ve ihbar tazminatı talep edebilir.",
            "legal_basis": ["İş K. m.22"],
            "reference_text": "İş Kanunu Madde 22 - İşveren, iş sözleşmesiyle veya iş sözleşmesinin eki niteliğindeki personel yönetmeliği ve benzeri kaynaklar ya da işyeri uygulamasıyla oluşan çalışma koşullarında esaslı bir değişikliği ancak durumu işçiye yazılı olarak bildirmek suretiyle yapabilir. Bu şekle uygun olarak yapılmayan ve işçi tarafından altı işgünü içinde yazılı olarak kabul edilmeyen değişiklikler işçiyi bağlamaz.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["calisma_kosullarinda_degisiklik", "esasli_degisiklik", "somut_olay"]
        },
        {
            "id": "is_010",
            "area": "is_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "İşçi müvekkil Ahmet Yılmaz, 01.06.2020 ile 09.07.2026 tarihleri arasında çalışmış olup, son net maaşı 35.000 TL'dir. İşveren son 3 aydır maaşını ödememektedir. Bu nedenle işçi iş sözleşmesini haklı nedenle (İş K. m. 24/II-e uyarınca) derhal feshetmekte ve kıdem tazminatı ile ödenmeyen 3 aylık maaş alacağını talep etmektedir. Noter vasıtasıyla çekilecek fesih ihtarnamesini hazırlayınız.",
            "expected_answer": "İhtarname Başlığı: İHTARNAME\nİhtar Eden: Ahmet Yılmaz (TCKN, Adres)\nVekili: Av. ...\nİhtar Edilen: XYZ Ticaret A.Ş. (Adres)\nKonu: İş sözleşmesinin haklı nedenle feshi, kıdem tazminatı ve ücret alacaklarının ödenmesi talebi.\nAçıklamalar: Şirketiniz bünyesinde 01.06.2020 tarihinden beri çalışmaktayım. Son 3 aya (Nisan, Mayıs, Haziran 2026) ait ücretlerimin ödenmemesi nedeniyle iş sözleşmesini İş K. m. 24/II-e uyarınca haklı nedenle feshediyorum.\nTalep: 6 yıllık çalışmaya ilişkin kıdem tazminatımın ve 3 aylık ödenmeyen ücret alacağımın 3 gün içinde belirtilen IBAN hesabıma yatırılmasını, aksi halde hukuki yollara başvurulacağını ihtar ederim.",
            "legal_basis": ["İş K. m.24/II-e"],
            "reference_text": "İş Kanunu Madde 24 - ... e) İşveren tarafından işçinin ücreti kanun hükümleri veya sözleşme şartlarına uygun olarak hesap edilmez veya ödenmezse...",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["fesih_ihtarnamesi", "ucret_odememe", "belge_uretimi"]
        }
    ]

    with open("data/questions/is_hukuku.jsonl", "w", encoding="utf-8") as f:
        for q in is_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # 4. CEZA / CMK (ceza.jsonl)
    ceza_questions = [
        {
            "id": "ceza_001",
            "area": "ceza_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "Sanık S hakkında Asliye Ceza Mahkemesi tarafından verilen mahkumiyet kararı 02.07.2026 Perşembe günü sanık müdafiinin hazır bulunduğu duruşmada yüzüne karşı tefhim edilmiştir. 7499 sayılı Kanunla yapılan süre değişiklikleri kapsamında, karara karşı istinaf başvuru süresi kaç gündür/haftadır ve istinaf dilekçesi/süre tutum dilekçesi sunabileceğimiz son gün hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "1. 7499 sayılı Kanun ile yapılan değişiklik uyarınca (1 Haziran 2024 yürürlük tarihli), ceza mahkemelerinde istinaf süresi kararın tefhim veya tebliğinden itibaren 'iki hafta' olarak belirlenmiştir (Eski 7 günlük süre yürürlükten kalkmıştır).\n2. Karar 02.07.2026 Perşembe günü tefhim edildiğine göre, tefhim günü hesaba katılmaz. Süre 03.07.2026 Cuma günü başlar.\n3. İki haftalık sürenin son günü, tefhim gününe tekabül eden gün olan 16.07.2026 Perşembe günü mesai saati bitimidir (UYAP üzerinden 23:59).",
            "legal_basis": ["CMK m.273/1", "7499 Sayılı Kanun"],
            "reference_text": "CMK Madde 273 - (Değişik: 2/3/2024-7499/16 md.) İstinaf istemi, hükmün tefhim veya tebliğinden itibaren iki hafta içinde hükmü veren mahkemeye bir dilekçe verilmesi veya zabıt katibine bir beyanda bulunulması suretiyle yapılır.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["istinaf_suresi", "ceza_muhakemesi", "7499_kanun"]
        },
        {
            "id": "ceza_002",
            "area": "ceza_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "5271 sayılı Ceza Muhakemesi Kanunu’na göre eski hâle getirmeyle ilgili aşağıdaki ifadelerden hangisi yanlıştır?\nA) Dilekçe, engelin kalkmasından itibaren iki hafta içinde verilir.\nB) Dilekçe sahibi, sürenin geçmesinde kusuru olmadığına ilişkin olguları açıklar.\nC) Eski hâle getirme isteminin reddine ilişkin kararlar kesindir.\nD) Dilekçe, süreye uyulduğunda usule ilişkin işlemleri yapacak olan mahkemeye verilir.\nE) Dilekçe verilmesi, kararın yerine getirilmesini kendiliğinden durdurmaz.",
            "expected_answer": "C",
            "legal_basis": ["CMK m.42/1"],
            "reference_text": "CMK Madde 42 - ... Eski hâle getirme isteminin reddine ilişkin karara karşı itiraz yoluna gidilebilir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["eski_hale_getirme", "cmk_42", "mcq"]
        },
        {
            "id": "ceza_003",
            "area": "ceza_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Sanık hakkında verilen Hükmün Açıklanmasının Geri Bırakılması (HAGB) kararına karşı başvurulabilecek yasa yolu nedir? Bu başvuru hangi süre içinde, nereye yapılmalıdır? Başvuruyu inceleyecek olan mercii hangisidir? Açıklayınız.",
            "expected_answer": "1. HAGB kararlarına karşı istinaf yoluna başvurulamaz. Kanun yolu 'itiraz'dır (CMK m. 231/12).\n2. İtiraz süresi, kararın tefhim veya tebliğinden itibaren 7 gündür (Burada 7499 sayılı Kanunla ceza yargılamasındaki genel 2 haftalık sürenin HAGB itirazlarını kapsamadığı, HAGB itirazlarının özel itiraz usulüne tabi olduğu ve CMK m. 268 uyarınca 7 gün olduğu kabul edilmektedir).\n3. İtiraz, kararı veren mahkemeye sunulacak dilekçe ile yapılır. İnceleme mercii Asliye Ceza için Ağır Ceza Mahkemesidir.",
            "legal_basis": ["CMK m.231/12", "CMK m.268"],
            "reference_text": "CMK Madde 231 - ... 12. Hükmün açıklanmasının geri bırakılması kararına itiraz edilebilir.\nCMK Madde 268 - Hâkim veya mahkeme kararına karşı itiraz, kanunda aksi belirtilmeyen hâllerde tefhim veya tebliğden itibaren yedi gün içinde yapılır.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["hagb", "itiraz", "ceza_muhakemesi"]
        },
        {
            "id": "ceza_004",
            "area": "ceza_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Soruşturma kapsamında 'nitelikli yağma' suçlamasıyla Sulh Ceza Hakimliği tarafından tutuklanan şüpheli Murat Koç vekili sıfatıyla, tutuklama kararına itiraz edeceğiz. Müvekkilin sabit ikametgah sahibi olduğunu, delillerin toplandığını ve kararın orantısız olduğunu belirterek tahliyesini talep eden tutukluluğa itiraz dilekçesi taslağı hazırlayınız.",
            "expected_answer": "Dilekçe Başlığı: ANKARA ( ) SULH CEZA HAKİMLİĞİNE\n(Gönderilmek Üzere Ankara Nöbetçi Sulh Ceza Hakimliğine)\nSoruşturma No: 2026/... Soruşturma\nTutuklamaya İtiraz Eden (Şüpheli): Murat Koç\nVekili: Av. ...\nKonu: Ankara ( ). Sulh Ceza Hakimliği'nin ... tarihli tutuklama kararına itirazımız ve tahliye talebimiz.\nAçıklamalar: Müvekkil hakkında nitelikli yağma suçundan tutuklama kararı verilmiştir. Ancak suçun unsurları oluşmamıştır, deliller karartılamaz, müvekkilin kaçma şüphesi yoktur. Tutuklama en son çaredir. Adli kontrol tedbirleri uygulanabilir.\nNetice-i Talep: İtirazımızın kabulüyle tutuklama kararının kaldırılmasına, müvekkilin salıverilmesine, hakimlik aksi kanaatte ise adli kontrol hükümleriyle serbest bırakılmasına.",
            "legal_basis": ["CMK m.101", "CMK m.104", "CMK m.105"],
            "reference_text": "CMK Madde 101 - ... Şüpheli veya sanık, salıverilmeyi isteme hakkına sahiptir. Tutuklamaya veya tutukluluğun devamına ilişkin karara karşı itiraz edilebilir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["tutukluluğa_itiraz", "tahliye_talebi", "belge_uretimi"]
        },
        {
            "id": "ceza_005",
            "area": "ceza_hukuku",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Aşağıdaki savunma dilekçesindeki usuli/hukuki hatayı tespit ediniz.\n\n***\nANKARA 5. ASLİYE CEZA MAHKEMESİNE\nDOSYA NO: 2026/150 Esas\nSANIK: Ahmet Tekin\nVEKİLİ: Av. Buket Yılmaz\nMÜŞTEKİ: Caner Aslan\nKONU: Şikayetten vazgeçme nedeniyle davanın düşürülmesi talebimizdir.\nAÇIKLAMALAR:\n1- Müvekkil hakkında müşteki Caner Aslan'a yönelik 'Taksirle Yaralama' (TCK m. 89/1) suçundan kamu davası açılmıştır.\n2- Müşteki duruşmada şikayetinden vazgeçtiğini beyan etmiştir. Taksirle yaralama suçu şikayete bağlı bir suçtur. \n3- Şikayetten vazgeçme nedeniyle davanın ceza verilmesine yer olmadığına kararı verilerek sonlandırılmasını talep ederiz. \nNETİCE-İ TALEP: Yukarıda açıklanan nedenlerle, müvekkil hakkındaki davanın şikayetten vazgeçme nedeniyle düşürülmesine karar verilmesini talep ederiz. 09.07.2026. Sanık Vekili Av. Buket Yılmaz\n***",
            "expected_answer": "Dilekçedeki çelişki/hata açıklama ve netice-i talep arasındadır. \n1. Açıklamalar 3. maddede 'ceza verilmesine yer olmadığına' karar verilmesi talep edilmiş, netice-i talepte ise 'düşme kararı' istenmiştir.\n2. TCK m. 73/4 ve CMK m. 223/8 uyarınca, soruşturulması ve kovuşturulması şikayete bağlı olan suçlarda şikayetten vazgeçme halinde davanın 'düşmesine' karar verilir. 'Ceza verilmesine yer olmadığına' kararı verilmez.\n3. Hata: Ceza verilmesine yer olmadığı kararı talebinin dilekçeden çıkarılarak doğrudan 'düşme kararı' talep edilmesi gerekir.",
            "legal_basis": ["TCK m.73/4", "CMK m.223/8"],
            "reference_text": "CMK Madde 223 - ... 8. Türk Ceza Kanununda öngörülen düşme sebeplerinin varlığı veya soruşturma veya kovuşturma şartının gerçekleşmeyeceğinin anlaşılması hallerinde, davanın düşmesine karar verilir.",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Şikayetten vazgeçmede 'ceza verilmesine yer olmadığı' ile 'düşme' kararının karıştırılması hatası.",
            "tags": ["sikayetten_vazgecme", "dusme_karari", "hata_yakalama"]
        },
        {
            "id": "ceza_006",
            "area": "ceza_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "Ceza mahkemelerinde 7499 sayılı Kanun değişikliği öncesinde uygulanan 7 günlük istinaf süresi, 1 Haziran 2024 tarihi itibariyle iki haftaya çıkarılmıştır. Ancak bir meslektaşınız size: 'Bu 2 haftalık süre sadece sanıklar için geçerlidir, Cumhuriyet Savcısının istinaf başvuru süresi halen 7 gündür' demiştir. Meslektaşınızın iddiası doğru mudur? Cumhuriyet Savcısının güncel ceza istinaf süresi nedir?",
            "expected_answer": "1. Meslektaşın iddiası yanlıştır.\n2. 7499 sayılı Kanun ile CMK m. 273'te yapılan değişiklikte, Cumhuriyet savcısının istinaf süresi de dahil olmak üzere tüm taraflar için istinaf süresi tefhim veya tebliğden itibaren 'iki hafta' olarak eşitlenmiştir.\n3. Kanunda savcı için ayrı bir 7 günlük süre kalmamıştır. Savcı da iki hafta içinde istinaf yoluna başvurmalıdır.",
            "legal_basis": ["CMK m.273", "7499 Sayılı Kanun"],
            "reference_text": "CMK Madde 273 - (Değişik: 2/3/2024-7499/16 md.) İstinaf istemi, hükmün tefhim veya tebliğ tarihinden itibaren iki hafta içinde hükmü veren mahkemeye bir dilekçe verilmesi...",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "abolished_law",
            "trap_details": "7499 sayılı kanun değişikliği öncesi savcının süresi ve sanığın süresi farklılıkları tamamen kaldırılmıştır. Modelin bu ayrımı bilmesi ve yanlış bilgiyi çürütmesi gerekir.",
            "tags": ["savcı_istinaf_suresi", "ceza_istinaf", "trap"]
        },
        {
            "id": "ceza_007",
            "area": "ceza_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "Aşağıdaki suçlardan hangisinin gece vakti işlenmesi kanunda ayrıca nitelikli hâl olarak düzenlenmiştir?\nA) Konut dokunulmazlığının ihlali suçu\nB) Cinsel saldırı suçu\nC) Kasten yaralama suçu\nD) Bilişim sistemine girme suçu\nE) Israrlı takip suçu",
            "expected_answer": "A",
            "legal_basis": ["TCK m.116/4"],
            "reference_text": "TCK Madde 116 - ... 4. Fiilin, cebir veya tehdit kullanılmak suretiyle ya da gece vakti işlenmesi halinde, kişi bir yıldan üç yıla kadar hapis cezası ile cezalandırılır.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["gece_vakti", "konut_dokunulmazligi", "tck_116", "mcq"]
        },
        {
            "id": "ceza_008",
            "area": "ceza_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Sanık S'nin yokluğunda (gıyabında) verilen mahkumiyet kararı, sanık vekili sıfatıyla bize 03.07.2026 Cuma günü tebliğ edilmiştir. Karara karşı istinaf kanun yoluna başvurmak istiyoruz. İstinaf başvuru süremiz kaç gündür/haftadır ve son gün hangi tarihtir? Resmi tatilleri gözeterek hesaplayınız.",
            "expected_answer": "1. 7499 sayılı Kanun uyarınca ceza istinaf süresi tebliğden itibaren 'iki hafta'dır.\n2. Tebliğ tarihi olan 03.07.2026 Cuma günü hesaba katılmaz. Süre 04.07.2026 Cumartesi günü başlar.\n3. Süre hafta olarak belirlendiğinden, iki haftalık sürenin son günü, tebliğ gününe karşılık gelen gün olan 17.07.2026 Cuma günü mesai bitimidir (UYAP'ta 23:59). Hafta sonları süreye dahildir.",
            "legal_basis": ["CMK m.273", "HMK m.92"],
            "reference_text": "CMK Madde 273 - ... iki hafta içinde...\nHMK Madde 92 - Süre hafta olarak belirlenmişse başladığı güne son hafta içindeki karşılık gelen günde biter.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["istinaf_suresi", "giyapta_karar", "sure_hesabi"]
        },
        {
            "id": "ceza_009",
            "area": "ceza_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Şüpheli Ş, 'kasten öldürme' suçundan gözaltına alınmıştır. Bireysel bir suçtur. Kanuna göre gözaltı süresi en fazla ne kadardır? Bu sürenin uzatılması mümkün müdür? Yol süresi hesabı nasıl yapılır? Açıklayınız.",
            "expected_answer": "1. CMK m. 91/1 uyarınca, gözaltı süresi, yakalama yerine en yakın hâkim veya mahkemeye gönderilmesi için zorunlu yol süresi hariç, yakalama anından itibaren yirmi dört saati geçemez.\n2. Zorunlu yol süresi en fazla on iki saat olabilir.\n3. Toplu suçlar hariç olmak üzere, bireysel suçlarda gözaltı süresi uzatılamaz (Kural olarak 24 saat + yol süresi).\n4. Hak ihlali olmaması için bu sürelere sıkı sıkıya uyulmalıdır.",
            "legal_basis": ["CMK m.91"],
            "reference_text": "CMK Madde 91 - Gözaltı süresi, yakalama yerine en yakın hâkim veya mahkemeye gönderilmesi için zorunlu yol süresi hariç, yakalama anından itibaren yirmidört saati geçemez. Zorunlu yol süresi oniki saatten fazla olamaz.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["gozalti_suresi", "yol_suresi", "somut_olay"]
        },
        {
            "id": "ceza_010",
            "area": "ceza_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Müşteki müvekkil Canan Aksoy, eski ortağı Kerem Soylu tarafından kandırılarak sahte imzalı bir sözleşmeyle 500.000 TL dolandırıldığını iddia etmektedir. 'Nitelikli dolandırıcılık' (TCK m. 158) suçu şüphesiyle Cumhuriyet Başsavcılığına sunulmak üzere, şüpheli hakkında kamu davası açılması talepli suç duyurusu dilekçesi hazırlayınız.",
            "expected_answer": "Dilekçe Başlığı: ANKARA CUMHURİYET BAŞSAVCILIĞINA\nMüşteki: Canan Aksoy (TCKN, Adres)\nVekili: Av. ...\nŞüpheli: Kerem Soylu (TCKN/Adres)\nSuç: Nitelikli Dolandırıcılık (TCK m. 158/1-f/h vb.) ve Resmi Belgede Sahtecilik (TCK m. 204).\nSuç Tarihi: 2026 yılı Mayıs ayı.\nAçıklamalar: Şüphelinin müvekkili hileli davranışlarla aldatarak sahte imzalı sözleşme imzalattığı ve 500.000 TL haksız kazanç sağladığı hususları delillerle sunulmuştur.\nNetice-i Talep: Şüpheli hakkında gerekli soruşturmanın yapılarak kamu davası açılmasına karar verilmesi talebi.",
            "legal_basis": ["TCK m.158", "TCK m.204", "CMK m.158"],
            "reference_text": "TCK Madde 158 - Dolandırıcılık suçunun; ... f) Bilişim sistemlerinin... h) Hileli davranışlarla...",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["suc_duyurusu", "dolandiricilik", "belge_uretimi"]
        }
    ]

    with open("data/questions/ceza.jsonl", "w", encoding="utf-8") as f:
        for q in ceza_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # Diğer 4 alanı da hızlıca doldurarak 80 soruyu tamamlayalım.
    # 5. TAZMİNAT / TBK (tazminat.jsonl)
    tazminat_questions = [
        {
            "id": "tazminat_001",
            "area": "tazminat_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "Müvekkil, bir haksız fiil sonucunda yaralanmış ve faili ile uğradığı zararı 01.07.2026 tarihinde tam olarak öğrenmiştir. Bu haksız fiilden kaynaklanan maddi ve manevi tazminat davası açmak istiyoruz. Türk Borçlar Kanunu'na göre zamanaşımı süresi kaç yıldır ve davanın zamanaşımına uğrayacağı son gün hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "1. TBK m. 72/1 uyarınca, haksız fiilden kaynaklanan tazminat istemi, zarar görenin zararı ve tazminat yükümlüsünü öğrendiği tarihten başlayarak 'iki yıl' geçmekle zamanaşımına uğrar.\n2. Öğrenme günü (01.07.2026) hesaba katılmaz. Süre 02.07.2026 tarihinde başlar.\n3. İki yıllık sürenin son günü 01.07.2028 Cumartesi günüdür. Hafta sonuna denk geldiği için son gün ilk mesai günü olan 03.07.2028 Pazartesi günü mesai bitimidir.",
            "legal_basis": ["TBK m.72"],
            "reference_text": "TBK Madde 72 - Tazminat istemi, zarar görenin zararı ve tazminat yükümlüsünü öğrendiği tarihten başlayarak iki yıl ve her hâlde fiilin işlendiği tarihten başlayarak on yıl geçmekle zamanaşımına uğrar.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["zamanasimi", "haksiz_fiil", "sure_hesabi"]
        },
        {
            "id": "tazminat_002",
            "area": "tazminat_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "6098 sayılı Türk Borçlar Kanunu'na göre kanundan, durumun gereğinden veya sözleşmede öngörülen özel koşullardan doğan ayrık hâller dışında satılanın yarar ve hasarı, taşınır satışlarında kural olarak hangi ana kadar satıcıya aittir?\nA) Sözleşmenin kurulması\nB) Satış bedelinin satıcıya ödenmesi\nC) Alıcının, satılanı gözden geçirmesi\nD) Satılanın zilyetliğinin alıcıya devri\nE) Alıcının, satılanda ayıp bulunmadığını satıcıya bildirmesi",
            "expected_answer": "D",
            "legal_basis": ["TBK m.208/1"],
            "reference_text": "TBK Madde 208 - Kanundan, durumun gereğinden veya sözleşmede öngörülen özel koşullardan doğan ayrık hâller dışında, satılanın yarar ve hasarı, taşınır satışlarında zilyetliğin devri... anına kadar satıcıya aittir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["yarar_hasar", "tasinir_satisi", "tbk_208", "mcq"]
        },
        {
            "id": "tazminat_003",
            "area": "tazminat_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "01.07.2021 tarihinde meydana gelen çift taraflı ölümlü trafik kazasında, müvekkilin eşi vefat etmiştir. Kazaya sebebiyet veren araç sürücüsü hakkında asliye ceza mahkemesinde ceza davası devam etmektedir. Müvekkil, sürücüye ve araç sahibine karşı destekten yoksun kalma tazminatı davası açmak istemektedir. Karayolları Trafik Kanunu m. 109 uyarınca normalde zamanaşımı 2 yıldır ve süre geçmiş görünmektedir. Bu durumda dava zamanaşımı yönünden reddedilir mi? Ceza zamanaşımı süresi nasıl uygulanır?",
            "expected_answer": "1. KTK m. 109/2 uyarınca, motorlu araç kazalarından doğan tazminat yükümlülüklerinde, kaza cezayı gerektiren bir fiil ise ve ceza kanununda daha uzun bir zamanaşımı süresi öngörülmüşse, bu süre maddi tazminat davaları için de geçerlidir (uzamış ceza zamanaşımı).\n2. Ölümlü trafik kazası TCK m. 85 kapsamında 'taksirle ölüme neden olma' suçunu oluşturur ve bu suçun ceza zamanaşımı TCK m. 66/1-d uyarınca 15 yıldır.\n3. Dolayısıyla, tazminat davası açma süresi kaza tarihi olan 01.07.2021'den itibaren 15 yıldır. Zamanaşımı dolmamıştır, dava açılabilir.",
            "legal_basis": ["KTK m.109/2", "TCK m.66", "TCK m.85"],
            "reference_text": "KTK Madde 109 - ... Motorlu araç kazalarından doğan maddi tazminat davaları, zarar görenin zararı ve tazminat yükümlüsünü öğrendiği tarihten başlayarak iki yıl ve herhalde kaza gününden başlayarak on yıl geçmekle zamanaşımına uğrar. Ancak kaza bir ceza kanunu hükmüne göre cezayı gerektiren bir fiilden ibaretse... daha uzun zamanaşımı süresi uygulanır.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["trafik_kazasi", "uzamis_zamanasimi", "somut_olay"]
        },
        {
            "id": "tazminat_004",
            "area": "tazminat_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Müvekkil Hasan Kaya, 01.06.2026 tarihinde geçirmiş olduğu trafik kazasında yaralanmıştır. Karşı tarafın Zorunlu Mali Sorumluluk Sigortası (Trafik Sigortası) yapan sigorta şirketi olan Anadolu Sigorta A.Ş.'ye dava öncesinde Karayolları Trafik Kanunu m. 97 uyarınca başvuru yapılması zorunludur. Sigorta şirketine sunulacak başvuru dilekçesini taslak olarak hazırlayınız.",
            "expected_answer": "Dilekçe Başlığı: ANADOLU SİGORTA A.Ş. GENEL MÜDÜRLÜĞÜNE\nBaşvuran: Hasan Kaya (TCKN, Adres)\nVekili: Av. ...\nKonu: 01.06.2026 tarihli kaza nedeniyle geçici/sürekli iş göremezlik tazminatı talebimiz.\nAçıklamalar: 01.06.2026 tarihinde müvekkilin içinde bulunduğu araca, şirketinizce sigortalı ... plakalı araç çarpmış ve müvekkil yaralanmıştır. KTK m. 97 uyarınca dava öncesi şirketinizden tazminat talep etme zorunluluğumuz doğmuştur. \nTalep: Müvekkilin iş göremezlik tazminatının hesaplanarak yasal süresi (15 gün) içinde belirtilen IBAN'a yatırılmasını talep ederiz.",
            "legal_basis": ["KTK m.97"],
            "reference_text": "KTK Madde 97 - Zarar görenin, zorunlu mali sorumluluk sigortasında öngörülen sınırlar içinde dava yoluna gitmeden önce ilgili sigorta kuruluşuna yazılı başvuruda bulunması gerekir. Sigorta kuruluşunun başvuru tarihinden itibaren en geç 15 gün içinde başvuruyu yazılı olarak cevaplamaması veya verilen cevabın talebi karşılamaması halinde dava açılabilir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["sigorta_basvurusu", "ktk_97", "belge_uretimi"]
        },
        {
            "id": "tazminat_005",
            "area": "tazminat_hukuku",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Aşağıdaki tazminat talepli dava dilekçesindeki faiz talebine ilişkin hatayı bularak analiz ediniz.\n\n***\nANKARA NÖBETÇİ TİCARET MAHKEMESİNE\nDAVACI: ABC İnşaat A.Ş.\nVEKİLİ: Av. Hakan Demir\nDAVALI: XYZ Lojistik Ltd. Şti.\nKONU: Maddi tazminat talebimizdir.\nAÇIKLAMALAR:\n1- Davalı şirkete ait tır, müvekkil şirketin ticari mal taşıyan aracına 01.05.2026 tarihinde çarparak 100.000 TL maddi hasar vermiştir.\n2- Her iki tarafın aracı da ticari araç olup, gerçekleştirilen faaliyet ticari iş niteliğindedir.\n3- Bu nedenle 100.000 TL maddi tazminatın kaza tarihi olan 01.05.2026 tarihinden itibaren işleyecek yasal faizi ile birlikte davalıdan tahsiline karar verilmesini talep ederiz. \nNETİCE-İ TALEP: ... maddi tazminatın yasal faizi ile tahsiline... Av. Hakan Demir\n***",
            "expected_answer": "Dilekçedeki hata faiz türünün yanlış talep edilmesidir.\n1. TTK m. 19/2 ve 3095 sayılı Kanun m. 2 uyarınca, tarafların ticari şirket olması ve hasara neden olan fiilin ticari nitelikte olması durumunda davacı, 'yasal faiz' yerine daha yüksek olan 'avans faizi (ticari faiz)' talep etme hakkına sahiptir.\n2. Yasal faiz talep edilmesi müvekkilin daha az faiz almasına neden olur. Dilekçede 'avans faizi ile tahsiline' şeklinde düzeltme yapılmalıdır.",
            "legal_basis": ["TTK m.19/2", "3095 Sayılı Kanun m.2"],
            "reference_text": "3095 Sayılı Kanun Madde 2 - Türkiye Cumhuriyet Merkez Bankasının önceki yılın 31 Aralık günü kısa vadeli avanslar için uyguladığı faiz oranı, yukarıda açıklanan miktardan fazla ise, arada sözleşme olmasa bile, ticari işlerde temerrüt faizi bu oran üzerinden istenebilir.",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Ticari işlerde daha düşük yasal faiz istenmesi hatası. Avans faizi talep edilmelidir.",
            "tags": ["faiz_turu", "ticari_faiz", "hata_yakalama"]
        },
        {
            "id": "tazminat_006",
            "area": "tazminat_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "Sözleşmesel sorumluluğa dayalı (örneğin müvekkil şirkete teslim edilen makinenin ayıplı olması nedeniyle üretimin durmasından kaynaklanan tazminat) davalarda zamanaşımı süresi yasal olarak kaç yıldır? Bir meslektaşınız bunun haksız fiil gibi 2 yıl olduğunu savunmaktadır. Hangisi doğrudur?",
            "expected_answer": "1. Sözleşmeye aykırılıktan (sözleşmesel sorumluluk) doğan tazminat taleplerinde zamanaşımı, TBK m. 146 uyarınca kanunda aksine bir hüküm bulunmadıkça genel zamanaşımı süresi olan 'on yıldır'.\n2. Haksız fiillerdeki 2 yıllık süre burada uygulanmaz.\n3. Dolayısıyla meslektaşınızın iddiası yanlıştır. Ayıplı makine tesliminden kaynaklanan tazminat taleplerinde genel zamanaşımı 10 yıldır (ancak satım sözleşmesindeki ayıptan sorumluluk süreleri saklıdır; eğer ayıplı mal davası ise TBK m. 244 uyarınca 2 yıllık süre mevcuttur. Eğer sadece sözleşmeye aykırılıktan doğan genel zarar tazminatı ise 10 yıldır. Modelin bu ayrımı yapması beklenir).",
            "legal_basis": ["TBK m.146", "TBK m.112"],
            "reference_text": "TBK Madde 146 - Kanunda aksine bir hüküm bulunmadıkça, her alacak on yıllık zamanaşıma tabidir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Sözleşmesel sorumluluktaki genel zamanaşımı ile haksız fiil sürelerinin karıştırılması.",
            "tags": ["zamanasimi", "sozlesmesel_sorumluluk", "trap"]
        },
        {
            "id": "tazminat_007",
            "area": "tazminat_hukuku",
            "task_type": "mcq",
            "difficulty": "L3",
            "question": "Aşağıdakilerden hangisi 6098 sayılı Türk Borçlar Kanunu’nda kefilin asıl borçludan güvence verilmesini ve borçtan kurtarılmasını isteme hakkını doğuran sebepler arasında sayılmamıştır?\nA) Asıl borçlunun kefile karşı üstlendiği yükümlülüklere aykırı davranması\nB) Asıl borçlunun temerrüde düşmesi\nC) Asıl borçlunun yerleşim yerini diğer bir ülkeye nakletmesi yüzünden takibatın önemli ölçüde güçleşmesi\nD) Asıl borçlunun mali durumunun kötüleşmesi\nE) Asıl borçlunun kendisine ait olan bir defiden vazgeçmiş olması",
            "expected_answer": "E",
            "legal_basis": ["TBK m.601"],
            "reference_text": "TBK Madde 601 - Kefil aşağıdaki hâllerde, asıl borçludan güvence verilmesini ve borç vadesi gelmişse borçtan kurtarılmasını isteyebilir: 1. Asıl borçlu, kefile karşı üstlendiği yükümlülüklere... 2. Asıl borçlu temerrüde düşmüşse... 3. Asıl borçlunun yerleşim yerini... nakletmesi yüzünden takibat... 4. Asıl borçlunun mali durumu kötüleşmişse...",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["kefalet", "guvence_isteme", "tbk_601", "mcq"]
        },
        {
            "id": "tazminat_008",
            "area": "tazminat_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Satım sözleşmesinde alıcıya teslim edilen malın ayıplı çıkması durumunda, satıcının ayıptan doğan sorumluluk davalarındaki zamanaşımı süresi (satıcının ağır kusuru bulunmamaktadır) teslim tarihinden itibaren kaç yıldır ve teslimat 03.07.2026 tarihinde yapılmışsa zamanaşımının son günü nedir? Adım adım hesaplayınız.",
            "expected_answer": "1. TBK m. 244/1 uyarınca, satılanın ayıplı olmasından doğan davalar, satılan alıcıya daha sonra kullanılmak üzere teslim edilmiş olsa bile, satıcı daha uzun bir süre için sorumluluk üstlenmiş olmadıkça, teslim tarihinden itibaren 'iki yıl' geçmekle zamanaşımına uğrar.\n2. Teslim tarihi 03.07.2026 hesaba katılmaz. Süre 04.07.2026 tarihinde başlar.\n3. İki yıllık sürenin son günü 03.07.2028 Pazartesi günü mesai saati bitimidir. Hafta sonu uzaması gerekmez çünkü pazartesi gününe denk gelmektedir.",
            "legal_basis": ["TBK m.244"],
            "reference_text": "TBK Madde 244 - Satılanın ayıplı olmasından doğan davalar, satılan alıcıya daha sonra kullanılmak üzere teslim edilmiş olsa bile, satıcı daha uzun bir süre için sorumluluk üstlenmiş olmadıkça, teslim tarihinden itibaren iki yıl geçmekle zamanaşımına uğrar.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["ayipli_mal", "zamanasimi", "sure_hesabi"]
        },
        {
            "id": "tazminat_009",
            "area": "tazminat_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "Üniversite öğrencisi A, annesi T'ye ait lüks bir çantayı gizlice alarak kız arkadaşı B'ye hediye etmiştir. Bunu öğrenen T (bir sabah haber programının sunucusu), yayın sırasında canlı yayında B ve ailesine yönelik: 'Bu aile beleşçiliği ile bilinen bir ailedir zaten. Kızlarının oğlumu kandırarak çantamı almasına da şaşırmadım. Babasının reklam ajansındaki mankenlerle ahlaki olmayan gizli ilişkileri, annesinin de medya patronlarına yanaştığı bir kızdan başka davranış beklenmezdi' şeklinde iddialarda bulunmuştur. B ve ailesinin, T'nin bu yayınındaki iddialarına karşı başvurabilecekleri hukuki imkanlar nelerdir? Gerekçeleri ve yasal dayanaklarıyla birlikte açıklayınız.",
            "expected_answer": "1. Kişilik haklarına yönelik müdahaleler hukuka aykırıdır (TMK m. 24). T'nin yayın organı üzerinden yaptığı açıklamalar şeref ve haysiyete yönelik hukuka aykırı bir saldırıdır. Kitle iletişim araçlarındaki haber verme/eleştiri hakkı sınırları (kamu yararı, gerçeklik ve amaç-araç dengesi) haysiyet kırıcı ifadeler nedeniyle aşılmıştır.\n2. Saldırının önlenmesi ve durdurulması davaları: Saldırı devam ediyorsa son verilmesi (durdurma), sona ermiş ama etkileri sürüyorsa hukuka aykırılığın tespiti (tespit), yeni bir saldırı tehlikesi varsa bunun önlenmesi (önleme) davası açılabilir (TMK m. 25).\n3. Manevi Tazminat davası: Yaşanan elem, acı ve ıstırap nedeniyle manevi tazminat talep edilebilir (TMK m. 25, TBK m. 56).\n4. Maddi Tazminat davası: Bu haksız yayın nedeniyle B ve ailesinin mesleki veya ekonomik bir kaybı oluşmuşsa maddi tazminat istenebilir.\n5. Kazancın İadesi: Eğer T bu sansasyonel yayın nedeniyle ek bir kazanç elde etmişse, gerçek olmayan vekaletsiz iş görme hükümlerine göre bu haksız kazancın iadesi talep edilebilir.",
            "legal_basis": ["TMK m.24", "TMK m.25", "TBK m.56"],
            "reference_text": "TMK Madde 24 - Hukuka aykırı olarak kişilik hakkına saldırılan kimse, hâkimden, saldırıda bulunanlara karşı korunmasını isteyebilir.\nTMK Madde 25 - Davacı, hâkimden saldırı tehlikesinin önlenmesini, sürmekte olan saldırıya son verilmesini, sona ermiş olsa bile etkileri devam eden saldırının hukuka aykırılığının tespitini isteyebilir... Manevi tazminat da talep edebilir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["kisilik_haklari", "manevi_tazminat", "vekaletsiz_is_gorme", "somut_olay"]
        },
        {
            "id": "tazminat_010",
            "area": "tazminat_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L4",
            "question": "Müvekkil Ayşe Demir, bir özel hastanede 01.05.2026 tarihinde yapılan yanlış ameliyat (malpraktis) sonucu sol bacağında kalıcı hasar oluştuğunu ve çalışamaz duruma geldiğini iddia etmektedir. Hekim Op. Dr. Can Şen ve Özel Şifa Hastanesi aleyhine maddi (iş göremezlik) ve manevi (100.000 TL) tazminat davası açacağız. Görevli mahkemede açılmak üzere dava dilekçesi taslağı hazırlayınız.",
            "expected_answer": "Dilekçe Başlığı: ANKARA NÖBETÇİ TÜKETİCİ MAHKEMESİNE\nDavacı: Ayşe Demir (TCKN, Adres)\nVekili: Av. ...\nDavalılar: 1- Op. Dr. Can Şen 2- Özel Şifa Hastanesi\nKonu: Malpraktis nedeniyle maddi ve manevi tazminat talebimizdir.\nHarca Esas Değer: 1.000 TL (Maddi tazminat - belirsiz alacak) + 100.000 TL (Manevi tazminat).\nAçıklamalar: 01.05.2026 tarihinde gerçekleştirilen ameliyattaki hekim hatası ve hastanenin organizasyon kusuru sonucu müvekkilde kalıcı iş göremezlik oluşmuştur. Tüketici mahkemesi görevlidir.\nNetice-i Talep: Maddi tazminatın belirsiz alacak davası olarak şimdilik 1.000 TL'sinin, manevi tazminatın 100.000 TL'sinin kaza tarihinden itibaren işleyecek faiziyle tahsili.",
            "legal_basis": ["TKHK m.3", "TKHK m.73", "TBK m.49"],
            "reference_text": "Tüketici Kanunu Madde 73 - Tüketici işlemleri ile tüketiciye yönelik uygulamalardan doğabilecek uyuşmazlıklara ilişkin davalarda tüketici mahkemeleri görevlidir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["malpraktis", "dava_dilekcesi", "belge_uretimi"]
        }
    ]

    with open("data/questions/tazminat.jsonl", "w", encoding="utf-8") as f:
        for q in tazminat_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # 6. İDARE / VERGİ (idare_vergi.jsonl)
    idare_questions = [
        {
            "id": "idare_001",
            "area": "idare_vergi_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "İdari işlemin iptali davasında, idare mahkemelerinde genel dava açma süresi kaç gündür? İdari işlem müvekkile 01.07.2026 tarihinde tebliğ edilmiştir. Herhangi bir ara verme (adli tatil) durumu olmadığı varsayımıyla dava açabileceğimiz son gün hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "1. İYUK m. 7/1 uyarınca, idare mahkemelerinde genel dava açma süresi 'altmış gündür'.\n2. Tebliğ tarihi olan 01.07.2026 günü hesaba katılmaz. Süre 02.07.2026 tarihinde başlar.\n3. Temmuz ayı 31 gün çektiği için: Temmuz'da 30 gün geçer. Kalan 30 gün Ağustos ayından kullanılır. 60 günlük sürenin son günü 30.08.2026 Pazar günüdür.\n4. Ancak 30 Ağustos Zafer Bayramı resmi tatilidir, ertesi gün 31.08.2026 Pazartesi günüdür. Bu nedenle dava açma süresinin son günü 31.08.2026 Pazartesi mesai bitimidir (veya UYAP üzerinden 23:59).",
            "legal_basis": ["İYUK m.7", "İYUK m.8"],
            "reference_text": "İYUK Madde 7 - 1. Dava açma süresi, özel kanunlarında ayrı süre gösterilmeyen hallerde Danıştayda ve idare mahkemelerinde altmış... gündür.\nİYUK Madde 8 - 1. Süreler tebliğ tarihini izleyen günden başlar. 2. Tatil günleri sürelere dahildir. Ancak sürenin son günü tatil gününe rastlarsa, süre tatil gününü izleyen çalışma gününün bitimine kadar uzar.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["dava_acma_suresi", "idari_yargi", "sure_hesabi"]
        },
        {
            "id": "idare_002",
            "area": "idare_vergi_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "2577 sayılı İdari Yargılama Usulü Kanunu’na göre idari yargı yerlerinin (I. Danıştay, II. İdare mahkemeleri, III. Vergi mahkemeleri) hangilerinde görülen davaların duruşmalarında savcının bulunması şarttır?\nA) Yalnız I\nB) Yalnız II\nC) Yalnız III\nD) I ve III\nE) I, II ve III",
            "expected_answer": "A",
            "legal_basis": ["İYUK m.18/4"],
            "reference_text": "İYUK Madde 18 - ... Danıştayda görülen davaların duruşmalarında savcının bulunması şarttır.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["durusma", "savci_bulunmasi", "iyuk_18", "mcq"]
        },
        {
            "id": "idare_003",
            "area": "idare_vergi_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "İdare Mahkemesi tarafından yürütmenin durdurulması (YD) talebimizin reddine karar verilmiştir. Bu karara karşı itiraz edebilir miyiz? İtiraz mercii neresidir ve itiraz süresi kaç gündür? Açıklayınız.",
            "expected_answer": "1. İYUK m. 27/7 uyarınca, yürütmenin durdurulması kararlarına karşı itiraz edilebilir.\n2. İtiraz süresi, kararın tebliğinden itibaren 'yedi gündür'.\n3. İdare mahkemesi kararına karşı itiraz, kararı veren mahkemenin bağlı olduğu Bölge İdare Mahkemesi'ne (BİM) yapılır. BİM'in verdiği karar kesindir.",
            "legal_basis": ["İYUK m.27/7"],
            "reference_text": "İYUK Madde 27 - ... 7. Yürütmenin durdurulması kararlarına karşı tebliğ tarihini izleyen günden itibaren yedi gün içinde ... itiraz edilebilir. İtiraz üzerine verilen kararlar kesindir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["yurutmenin_durdurulmasi", "itiraz_suresi", "idari_yargi"]
        },
        {
            "id": "idare_004",
            "area": "idare_vergi_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Müvekkil Canan Şahin'e ait Çankaya/Ankara'daki taşınmaz için Ankara Büyükşehir Belediye Encümeni tarafından 01.06.2026 tarihinde yıkım ve idari para cezası kararı verilmiştir. Karar müvekkile 15.06.2026 tarihinde tebliğ edilmiştir. Ankara İdare Mahkemesi'nde açılmak üzere yürütmenin durdurulması istemli iptal davası dilekçesi taslağı hazırlayınız.",
            "expected_answer": "Dilekçe Başlığı: ANKARA NÖBETÇİ İDARE MAHKEMESİNE\nDavacı: Canan Şahin (TCKN, Adres)\nVekili: Av. ...\nDavalı: Ankara Büyükşehir Belediye Başkanlığı\nKonu: Ankara Büyükşehir Belediye Encümeni'nin 01.06.2026 tarih ve ... sayılı yıkım ve idari para cezası kararının iptali ve Yürütmenin Durdurulması talebimiz.\nAçıklamalar: Belediye encümen kararı hukuka aykırıdır. İmar Kanunu'na uygun yapıda yıkım kararı verilemez. Yürütmenin durdurulması şartları (telafisi güç zarar ve açık hukuka aykırılık) oluşmuştur.\nNetice-i Talep: Davalı idarenin savunması alınmaksızın yürütmenin durdurulmasına, idari işlemin iptaline.",
            "legal_basis": ["İYUK m.7", "İYUK m.27", "İmar K. m.32", "İmar K. m.42"],
            "reference_text": "İYUK Madde 27 - ... 2. Danıştay veya idari mahkemeler, idari işlemin uygulanması halinde telafisi güç veya imkansız zararların doğması ve idari işlemin açıkça hukuka aykırı olması şartlarının birlikte gerçekleşmesi durumunda... yürütmenin durdurulmasına karar verebilirler.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["iptal_davasi", "yurutmenin_durdurulmasi", "belge_uretimi"]
        },
        {
            "id": "idare_005",
            "area": "idare_vergi_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Suriye vatandaşı (A), geçici koruma statüsüyle Türkiye'de Diş Hekimliği Fakültesini bitirmiş ve diş hekimi olarak çalışma izni başvurusu yapmıştır. İdare, 1219 sayılı Kanun m. 30'daki 'Türk olma' şartını gerekçe göstererek talebi reddetmiştir. (A), bu işlemin hukuka aykırı olduğunu ve ayrımcılığa uğradığını ileri sürmektedir. Yabancıların temel haklarının sınırlanması rejimini ve (A)'nın ayrımcılık iddialarını eşitlik ilkesi ve uluslararası sözleşmeler bağlamında değerlendiriniz.",
            "expected_answer": "1. Yabancıların Haklarının Sınırlanması Rejimi: Anayasa m. 16 uyarınca yabancıların temel hak ve hürriyetleri milletlerarası hukuka uygun olarak kanunla sınırlanabilir. Somut olayda sınırlama 1219 sayılı Kanun m. 30 (kanunilik) ile yapılmıştır ve Tüm Göçmen İşçilerin Haklarının Korunmasına Dair Uluslararası Sözleşme m. 52/1 (milletlerarası hukuka uygunluk) uyarınca devletin belirli işlerde sınırlama yetkisi bulunduğundan sınırlama rejime uygundur.\n2. Eşitlik İlkesi ve Ayrımcılık Değerlendirmesi: Eşitlik ilkesi, benzer durumdakilere benzer, farklı durumdakilere farklı davranılmasını gerektirir. Somut olayda (A) diş hekimidir, tıp mezunu olan (B) ise aile hekimi olarak çalışmaktadır. Kanun bu iki meslek statüsünü farklı kabul etmiş ve diş hekimliğinde yabancıların çalışmasını yasaklamıştır. İki mesleğin hukuki statüsü farklı olduğundan, farklı durumda olanlar arasında farklı kurallar uygulanması eşitlik ilkesine veya ayrımcılık yasağına aykırılık teşkil etmez.",
            "legal_basis": ["Anayasa m.16", "1219 Sayılı Kanun m.30", "Tüm Göçmen İşçilerin Haklarının Korunması Sözleşmesi m.52"],
            "reference_text": "Anayasa Madde 16 - Temel hak ve hürriyetler, yabancılar için, milletlerarası hukuka uygun olarak kanunla sınırlanabilir.\n1219 Sayılı Kanun Madde 30 - Türkiye Cumhuriyeti dahilinde dişçilik sanatını icra ve diş tabibi unvanını taşyabilmek için Türk olmak... lazımdır.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["yabancilar_hukuku", "calisma_izni", "esitlik_ilkesi", "somut_olay"]
        },
        {
            "id": "idare_006",
            "area": "idare_vergi_hukuku",
            "tags": ["adli_tatil", "iyuk_8", "sure_hesabi"]
        },
        {
            "id": "idare_007",
            "area": "idare_vergi_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "İdarenin bir fiili (eylemi) nedeniyle zarara uğrayan kişinin (tam yargı davası açmak isteyen) doğrudan dava açmadan önce idareye başvurarak hakkının yerine getirilmesini istemesi zorunlu mudur? Bu başvurunun süresi nedir?\nA) Zorunlu değildir, doğrudan dava açılabilir.\nB) Zorunludur. Eylemin öğrenilmesinden itibaren 1 yıl ve her halde 5 yıl içinde idareye başvurulmalıdır.\nC) Zorunludur. Eylemin öğrenilmesinden itibaren 60 gün içinde idareye başvurulmalıdır.\nD) Zorunludur. Eylemin öğrenilmesinden itibaren 30 gün içinde idareye başvurulmalıdır.\nE) Sadece idari cezalarda zorunludur, maddi zararlarda doğrudan dava açılır.",
            "expected_answer": "B",
            "legal_basis": ["İYUK m.13"],
            "reference_text": "İYUK Madde 13 - İdari eylemlerden hakları ihlal edilmiş olanların idari dava açmadan önce, bu eylemleri yazılı bildirim üzerine veya başka suretle öğrendikleri tarihten itibaren bir yıl ve her halde eylem tarihinden itibaren beş yıl içinde ilgili idareye başvurarak haklarının yerine getirilmesini istemeleri gereklidir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["tam_yargi", "idareye_basvuru", "mcq"]
        },
        {
            "id": "idare_008",
            "area": "idare_vergi_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Vergi mahkemesinde dava açma süresi 30 gündür. Bir vergi ceza ihbarnamesi müvekkile 01.07.2026 tarihinde tebliğ edilmiştir. Adli tatil (ara verme) hükümleri saklı kalmak kaydıyla, dava açabileceğimiz son gün hangi tarihtir? Adım adım hesaplayınız.",
            "expected_answer": "1. İYUK m. 7/1 uyarınca vergi mahkemelerinde genel dava açma süresi 30 gündür.\n2. Tebliğ tarihi olan 01.07.2026 hesaba katılmaz. Süre 02.07.2026 tarihinde başlar.\n3. 30 günlük sürenin son günü 31.07.2026 Cuma günüdür. (Temmuz ayı 31 gün çekmektedir, süre tebliğden sonraki gün başladığından tam olarak 31 Temmuz'da biter).",
            "legal_basis": ["İYUK m.7/1"],
            "reference_text": "İYUK Madde 7 - ... vergi mahkemelerinde otuz gündür.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["vergi_davasi", "dava_suresi", "sure_hesabi"]
        },
        {
            "id": "idare_009",
            "area": "idare_vergi_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Müvekkilin ruhsatlı inşaatı idare tarafından mühürlenmiştir. Mühürleme işlemi 01.07.2026 tarihinde yapılmış ancak müvekkile herhangi bir yazılı tebligat yapılmamıştır. Müvekkil durumu 05.07.2026 tarihinde şantiyeye gittiğinde öğrenmiştir. İptal davası açmak için 60 günlük dava açma süresinin başlangıcı hangi tarihtir? Tebligat yapılmamış olması dava açma hakkını engeller mi?",
            "expected_answer": "1. Tebligat yapılmamış olması dava açma hakkını engellemez. İdari işlemin yazılı tebligatla bildirilmesi asıldır ancak fiili öğrenme durumunda da dava açılabilir.\n2. İYUK m. 7 uyarınca süre tebliğle başlar. Tebliğ yoksa, işlemin kesin olarak öğrenildiği tarih (ıttıla tarihi) olan 05.07.2026 tarihi öğrenme tarihi kabul edilir.\n3. Dava açma süresi öğrenme tarihini izleyen gün yani 06.07.2026 tarihinde başlar ve 60 gündür.",
            "legal_basis": ["İYUK m.7"],
            "reference_text": "İYUK Madde 7 - ... Dava açma süresi, tebliğ, ilan veya ihbar tarihini izleyen günden başlar.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["ittila", "fiili_ogrenme", "somut_olay"]
        },
        {
"expected_answer": "Dilekçe Başlığı: ÇANKAYA BELEDİYE BAŞKANLIĞINA\nBaşvuran: ... (Müvekkil TCKN, Adres)\nVekili: Av. ...\nKonu: Hizmet kusuru nedeniyle 50.000 TL maddi, 50.000 TL manevi tazminat talebimizdir.\nAçıklamalar: 01.06.2026 tarihinde belediyenizin sorumluluk alanındaki rögarda açık bırakılan kapak nedeniyle müvekkil düşmüş ve bacağı kırılmıştır. Tedavi masrafları ve iş kaybı oluşmuştur.\nTalep: İYUK m. 13 uyarınca toplam 100.000 TL tazminatın yasal süresi (30 gün) içinde ödenmesi.",
            "legal_basis": ["İYUK m.13"],
            "reference_text": "İYUK Madde 13 - İdari eylemlerden hakları ihlal edilmiş olanların idari dava açmadan önce... ilgili idareye başvurarak haklarının yerine getirilmesini istemeleri gereklidir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["idari_basvuru", "hizmet_kusuru", "belge_uretimi"]
        }
    ]

    with open("data/questions/idare_vergi.jsonl", "w", encoding="utf-8") as f:
        for q in idare_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # 7. AVUKATLIK / UYAP (avukatlik_uyap.jsonl)
    avukatlik_questions = [
        {
            "id": "avukatlik_001",
            "area": "avukatlik_pratigi",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "Avukatlık Kanunu m. 35/A uyarınca karşı tarafa yapılan uzlaşma davetinde, karşı tarafın davete cevap vermesi veya uzlaşma toplantısına katılması için kanunda öngörülen cevap süresi kaç gündür? Davet yazısı karşı tarafa 01.07.2026 tarihinde tebliğ edilmişse bu sürenin son günü nedir? Adım adım hesaplayınız.",
            "expected_answer": "1. Avukatlık Kanunu m. 35/A ve ilgili Yönetmelik uyarınca, uzlaşma davetine karşı tarafın cevap verme süresi tebliğden itibaren 'üç aydır' (Kanunun 35/A maddesinde süre belirtilmemiş ancak Avukatlık Kanunu Yönetmeliği m. 16/2 uyarınca karşı tarafa en az 30 gün süre verilir; ya da Avukatlık Kanunu m. 35/A kapsamında açılan uzlaşma tutanağı süreleri incelendiğinde, tebliğden itibaren makul süre verilir. Yönetmelikteki asgari 30 günlük süre veya uygulamada kabul edilen süre belirtilmelidir. Ancak dikkat: Avukatlık Kanunu m. 35/A kapsamında kanuni bir zorunlu cevap süresi doğrudan kanun metninde gün olarak yazılı değildir, ancak davette belirtilen süre esastır. Yönetmelik uyarınca en az otuz gün süre verilmesi zorunludur. Dolayısıyla 30 gün üzerinden hesap yapılırsa: 01.07.2026 tebliğ, son gün 31.07.2026'dır).",
            "legal_basis": ["Avukatlık Kanunu m.35/A", "Avukatlık Kanunu Yönetmeliği m.16"],
            "reference_text": "Avukatlık Kanunu Yönetmeliği Madde 16 - ... Davet yazısında karşı tarafa en az otuz günlük bir süre verilerek...",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["uzlasma", "avukatlik_kanunu", "sure_hesabi"]
        },
        {
            "id": "avukatlik_002",
            "area": "avukatlik_pratigi",
            "task_type": "mcq",
            "difficulty": "L1",
            "question": "Avukatlık Kanunu'na göre, avukatın işi reddetmesi halinde durumu iş sahibine bildirmesi gerekir. İş sahibi tarafından tevdi olunan işi gerekçe göstermeden reddeden avukat, bu durumu iş sahibine kaç gün içinde bildirmelidir?\nA) Derhal (aynı gün)\nB) 3 gün içinde\nC) 7 gün içinde\nD) 15 gün içinde\nE) Süreye tabi değildir",
            "expected_answer": "B",
            "legal_basis": ["Avukatlık Kanunu m.37"],
            "reference_text": "Avukatlık Kanunu Madde 37 - Avukat, kendisine teklif olunan işi sebep göstermeden reddedebilir. Reddetmek istediği işi üç gün içinde iş sahibine bildirmeye mecburdur.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["isi_reddetme", "avukatlik_kanunu", "mcq"]
        },
        {
            "id": "avukatlik_003",
            "area": "avukatlik_pratigi",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Davalı (B) şirketinin ofisini, dava dilekçesinin tebliğinden hemen sonra sel basmıştır. Bu nedenle şirket temsilcisi iki haftalık yasal cevap süresi içinde cevap dilekçesi verememiştir. Süre geçtikten sonra (B) şirketinin cevap dilekçesini sunabilmesini sağlayacak bir hukuki çare var mıdır? Varsa hangi süre içinde, hangi gerekçelerle ve hangi merciden talep edilmelidir?",
            "expected_answer": "1. HMK m. 95 uyarınca, elde olmayan sebeplerle (somut olayda sel felaketi) kanuni süreyi kaçıran taraf 'Eski Hale Getirme' (reinstatement) yoluna başvurabilir.\n2. Eski hale getirme talebi, engelin ortadan kalkmasından (sel felaketinin sona ermesinden ve temsilcinin işlemi yapabilecek duruma gelmesinden) itibaren 'iki hafta' içinde yapılmalıdır.\n3. Başvuru, kaçırılan işlemin yapılacağı (davaya bakan) mahkemeye sunulacak bir dilekçeyle yapılır.\n4. Süresinde yapılamayan cevap dilekçesi de bu iki haftalık eski hale getirme başvuru süresi içinde mahkemeye sunulmak zorundadır (HMK m. 97/1).",
            "legal_basis": ["HMK m.95", "HMK m.96", "HMK m.97", "HMK m.98"],
            "reference_text": "HMK Madde 95 - 1. Elde olmayan sebeplerle, kanunda belirtilen... süre içinde bir işlemi yapamayan taraf, eski hâle getirme talebinde bulunabilir.\nHMK Madde 96 - ... engelin ortadan kalkmasından itibaren iki hafta içinde...",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["eski_hale_getirme", "cevap_suresi", "hmk_95", "somut_olay"]
        },
        {
            "id": "avukatlik_004",
            "area": "avukatlik_pratigi",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Müvekkil Hasan Şen ile avukat olarak aranızda, Ankara Asliye Ceza Mahkemesinde görülecek bir 'Kasten Yaralama' davasının takibi için avukatlık ücret sözleşmesi imzalayacaksınız. Ücret 50.000 TL olarak belirlenmiştir. Vekalet ücretinin ödeme zamanı ve masrafların kime ait olacağını da belirleyen yasalara uygun bir Avukatlık Sözleşmesi taslağı hazırlayınız.",
            "expected_answer": "Sözleşme Başlığı: AVUKATLIK ÜCRET SÖZLEŞMESİ\nTaraflar: 1- Av. ... 2- Hasan Şen (Müvekkil)\nİşin Konusu: Ankara Asliye Ceza Mahkemesinde görülecek kasten yaralama davasının takibi.\nÜcret Tutarı: 50.000 TL net vekalet ücreti.\nÖdeme Koşulları: Vekalet ücretinin yarısı (25.000 TL) sözleşme tarihinde peşin, kalan yarısı ilk duruşma gününden önce ödenecektir.\nGider ve Masraflar: Davayla ilgili harç, posta ve mahkeme masrafları ile seyahat giderleri müvekkil tarafından karşılanacaktır.\nYetkili Mahkeme: Ankara Mahkemeleri.",
            "legal_basis": ["Avukatlık Kanunu m.163", "Avukatlık Kanunu m.164"],
            "reference_text": "Avukatlık Kanunu Madde 163 - Avukatlık sözleşmesi yazılı olarak yapılır. Avukatlık ücretinin kararlaştırılmamış olması sözleşmenin geçersizliğini gerektirmez.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["ucret_sozlesmesi", "avukatlik_sozlesmesi", "belge_uretimi"]
        },
        {
            "id": "avukatlik_005",
            "area": "avukatlik_pratigi",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Bir avukatın, vekaletnamesinde 'tevkil' (başkasını vekil tayin etme) yetkisi olmadığı halde, başka bir avukata kendi imzasıyla 'yetki belgesi' düzenleyerek duruşmaya göndermesi durumunda oluşacak hukuki riski ve usuli hatayı değerlendiriniz. Duruşmada karşı taraf vekili itiraz ederse ne olur?",
            "expected_answer": "1. HMK ve Avukatlık Kanunu uyarınca, bir avukatın başka bir avukatı yetkilendirebilmesi (yetki belgesi düzenlemesi) için, kendisine verilen vekaletnamede açıkça 'tevkil' yetkisinin bulunması şarttır.\n2. Tevkil yetkisi olmaksızın düzenlenen yetki belgesi geçersizdir.\n3. Hukuki Risk: Karşı taraf vekili veya mahkeme bu durumu tespit ederse, yetkisiz temsil söz konusu olur. Mahkeme yetkisiz avukatın beyanlarını kabul etmez, duruşmaya katılmasına izin vermeyebilir veya vekaletname ibrazı için süre verir. Süresinde uygun vekaletname sunulmazsa işlemler geçersiz sayılabilir.",
            "legal_basis": ["HMK m.74", "Avukatlık Kanunu m.56"],
            "reference_text": "Avukatlık Kanunu Madde 56 - ... Vekiller vasıtasıyla takip edilen işlerde, avukata tebliğ edilen kararlar müvekkile tebliğ edilmiş sayılır. Avukatlar, vekaletnamede yetki verilmişse başkasını tevkil edebilirler.",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Tevkil yetkisi olmayan vekaletnameye dayalı yetki belgesi düzenlenmesi usul hatası.",
            "tags": ["tevkil_yetkisi", "yetki_belgesi", "hata_yakalama"]
        },
        {
            "id": "avukatlik_006",
            "area": "avukatlik_pratigi",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "UYAP Avukat Portalı üzerinden bir davanın son gününde (örneğin dava açma süresinin son günü olan 09.07.2026) dava açmak istiyorsunuz. Harç ve gider avansını UYAP üzerinden saat 23:30'da yatırdınız. Ancak dava tevzi formu ertesi gün (10.07.2026) tarihinde sistem tarafından oluşturulmuştur. Dava yasal süresi içinde açılmış sayılır mı? UYAP işlemlerinde davanın resmi açılış tarihi ve saati nasıl belirlenir?",
            "expected_answer": "1. HMK Yönetmeliği m. 36/4 ve yerleşik Yargıtay içtihatları uyarınca, elektronik ortamda açılan davalarda davanın açıldığı tarih, harç ve gider avansının UYAP sistemi üzerinden ödendiği ve onaylandığı andır.\n2. Ödeme 09.07.2026 tarihinde saat 23:30'da (yani gün bitmeden önce) yapıldığı için dava yasal süresi içinde açılmış sayılır.\n3. Tevzi formunun ertesi gün oluşturulması davanın açılış tarihini etkilemez. Ödeme anındaki tarih esastır.",
            "legal_basis": ["HMK Yönetmeliği m.36"],
            "reference_text": "HMK Yönetmeliği Madde 36 - ... UYAP üzerinden açılan davalarda, harç ve gider avansının yatırıldığı tarih dava tarihi olarak kabul edilir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["uyap", "dava_tarihi", "harc_odeme"]
        },
        {
            "id": "avukatlik_007",
            "area": "avukatlik_pratigi",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Dava devam ederken davayı gören ilk derece mahkemesi hakimi, davalı (B) şirketinin avukatına borcun zamanaşımına uğradığını söylemiştir (ihsas-ı reyde bulunmuştur). Davacı (A) bunu öğrendiğinde hakimin bu davaya bakmasına engel olabilir mi? Bunun hukuki gerekçesini, başvurunun süresini, şeklini ve hangi mercie yapılacağını açıklayınız. Ayrıca, hakim bu ret talebini doğrudan kendisi geri çevirebilir mi? Hangi hallerde geri çevirebilir?",
            "expected_answer": "1. Hakimin Reddi ve İhsas-ı Rey: HMK m. 36/1-a uyarınca hakimin iki taraftan birine öğüt vermesi veya yol göstermesi, hakimin tarafsızlığından şüphe edilmesini gerektiren hakimin reddi sebebidir. Hakim davalı vekiline zamanaşımı itirazında bulunması gerektiğini ima ederek ihsas-ı reyde bulunmuştur. Davacı A, hakimin reddini talep edebilir.\n2. Süre ve Şekil: Davacı A, ret sebebini öğrendikten sonraki ilk duruşmada, yeni bir işlem yapmadan önce hakimin reddi dilekçesini reddi istenen hakimin bağlı olduğu mahkemeye sunmalıdır. Dilekçede ret sebepleri ve inandırıcı deliller belirtilmelidir.\n3. Hakimin Ret Talebini Geri Çevirmesi (HMK m. 41): Reddi istenen hakim, merci incelemesine göndermeden önce şu üç durumda ret talebini kendisi doğrudan geri çevirebilir:\n   a) Talebin süresinde yapılmamış olması,\n   b) Ret sebebi ve buna ilişkin inandırıcı delil veya emare gösterilmemiş olması,\n   c) Talebin davayı uzatmak amacıyla yapıldığının açıkça anlaşılması.",
            "legal_basis": ["HMK m.36", "HMK m.38", "HMK m.41"],
            "reference_text": "HMK Madde 36 - Hâkimin tarafsızlığından şüpheyi gerektiren önemli bir sebebin bulunması hâlinde... reddedilebilir.\nHMK Madde 41 - Hâkimin reddi talebi; süresinde yapılmamışsa, ret sebebi... gösterilmemişse, davayı uzatmak amacıyla yapıldığı açıkça anlaşılıyorsa... reddedilen hâkim tarafından geri çevrilir.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["hakimin_reddi", "ihsas_i_rey", "hmk_36", "somut_olay"]
        },
        {
            "id": "avukatlik_008",
            "area": "avukatlik_pratigi",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Yetkisiz mahkemede açılan bir davada mahkemece yetkisizlik kararı verilmiştir. Davaya yetkili mahkemede devam edilebilmesi için kim tarafından, hangi süre içinde, hangi işlemlerin yapılması gereklidir? Bu süre ne zaman başlar? Bu işlemlerin yapılmaması durumunda davanın akıbeti ne olacaktır?",
            "expected_answer": "1. Taraflardan birinin iki hafta içinde yetkisizlik kararı veren mahkemeye başvurarak dosyanın yetkili mahkemeye gönderilmesini talep etmesi gerekir (HMK m. 20/1). Mahkeme dosyayı kendiliğinden göndermez.\n2. İki haftalık başvuru süresi; yetkisizlik kararı verildiği anda kesinse (kanun yolu kapalıysa) kararın tebliğinden; kanun yolu açık olup da süre içinde başvurulmamışsa kararın kesinleştiği tarihten; kanun yoluna başvurulmuşsa bu başvurunun reddi kararının tebliğ tarihinden itibaren başlar.\n3. Süresinde başvuru yapılmazsa, yetkisizlik kararı veren mahkemece davanın açılmamış sayılmasına karar verilir. Davanın açılmasıyla doğan tüm usuli ve maddi sonuçlar ortadan kalkar.",
            "legal_basis": ["HMK m.20"],
            "reference_text": "HMK Madde 20 - Görevsizlik veya yetkisizlik kararı verilmesi hâlinde... kararın kesinleştiği tarihten... itibaren iki hafta içinde kararı veren mahkemeye başvurarak, dava dosyasının görevli veya yetkili mahkemeye gönderilmesini talep etmesi gerekir; aksi takdirde, bu mahkemece davanın açılmamış sayılmasına karar verilir.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["yetkisizlik", "dosya_gonderme", "hmk_20", "sure_hesabi"]
        },
        {
            "id": "avukatlik_009",
            "area": "avukatlik_pratigi",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Bursa’da ikamet eden tacir (A), yaz aylarında ailesiyle kalmak amacıyla, Tekirdağ’da bulunan bir müstakil evi, merkezi İstanbul Beşiktaş'ta bulunan ve emlak sektöründe faaliyet gösteren (B) Emlak A.Ş’den kiralamıştır. Bedel peşin ödenmiş ancak ev teslim edilmemiştir. \n1) (A)’nın açacağı alacak davası hangi yer veya yerler mahkemesinde açılabilir? Açıklayınız.\n2) Taraflar kira sözleşmesine, 'İşbu kira sözleşmesinden doğan uyuşmazlıklar Kartal veya Bakırköy Mahkemeleri’nde görülecektir' kaydını koysalardı bu durum yetkili mahkemeyi nasıl etkilerdi? Gerekçeleriyle açıklayınız.",
            "expected_answer": "1. Yetkili Mahkemeler (Genel ve Özel Yetki):\n   a) Genel Yetki: HMK m. 6 uyarınca davalı tüzel kişinin davanın açıldığı tarihteki yerleşim yeri (merkezi) olan Beşiktaş'ın bağlı olduğu İstanbul (Çağlayan) Sulh Hukuk Mahkemesidir.\n   b) Özel Yetki: HMK m. 10 uyarınca sözleşmenin ifa edileceği yer mahkemesidir. Sözleşmede ifa yeri kararlaştırılmadığından para borcu alacağının iadesi TBK m. 89 uyarınca alacaklının yerleşim yeri olan Bursa Sulh Hukuk Mahkemesi'nde ödenir. Dolayısıyla Bursa Sulh Hukuk Mahkemesi de yetkilidir. Davacı iki mahkemeden birini seçebilir.\n2. Yetki Sözleşmesinin Etkisi (HMK m. 17): Tarafların her ikisi de tacirdir ve kesin yetki hali bulunmamaktadır. Dolayısıyla sözleşmeye konulan yetki şartı geçerlidir. Bu durumda yetki sözleşmesiyle belirlenen Kartal (İstanbul Anadolu) ve Bakırköy mahkemeleri yetkili hale gelir. Yetki sözleşmesinde aksine açıklama yoksa davanın sadece bu mahkemelerde açılması gerekir (yetki sözleşmesinin münhasırlığı).",
            "legal_basis": ["HMK m.6", "HMK m.10", "HMK m.17", "TBK m.89"],
            "reference_text": "HMK Madde 6 - Genel yetkili mahkeme, davalı... davanın açıldığı tarihteki yerleşim yeri mahkemesidir.\nHMK Madde 10 - Sözleşmeden doğan davalar, sözleşmenin ifa edileceği yer mahkemesinde de açılabilir.\nHMK Madde 17 - Tacirler veya kamu tüzel kişileri... uyuşmazlık hakkında bir veya birden çok mahkemeyi yetkili kılabilirler.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["yetkili_mahkeme", "yetki_sozlesmesi", "hmk_17", "somut_olay"]
        },
        {
            "id": "avukatlik_010",
            "area": "avukatlik_pratigi",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Müvekkilin davasını başarıyla sonuçlandırdınız ve kesinleşti. Ancak müvekkil sözleşmede yazılı olan 30.000 TL vekalet ücretini ödememektedir. Avukatlık Kanunu m. 164 kapsamında müvekkile vekalet ücretini ödemesi için noter vasıtasıyla çekilecek muacceliyet ve temerrüt ihtarnamesi hazırlayınız.",
            "expected_answer": "İhtarname Başlığı: İHTARNAME\nİhtar Eden: Av. ... (TCKN, Adres)\nİhtar Edilen: ... (Müvekkil adı, TCKN, Adres)\nKonu: Avukatlık vekalet ücreti alacağının ödenmesi ihtarı.\nAçıklamalar: Aranızda imzalanan ... tarihli sözleşme gereği takibini yürüttüğüm ve kesinleşen ... mahkemesindeki davanın takibi başarıyla tamamlanmıştır. Ancak sözleşmesel vekalet ücreti olan 30.000 TL ödenmemiştir.\nTalep: İşbu ihtarnamenin tebliğinden itibaren 3 gün içinde 30.000 TL vekalet ücreti borcunu belirtilen IBAN hesabıma yatırmanızı, aksi takdirde yasal yollara başvurulacağını ihtar ederim.",
            "legal_basis": ["Avukatlık Kanunu m.164", "Avukatlık Kanunu m.166"],
            "reference_text": "Avukatlık Kanunu Madde 164 - Avukatlık ücreti, avukatın hukuki yardımının karşılığı olan meblağ veya değeri ifade eder.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["vekalet_ucreti", "ihtarname", "belge_uretimi"]
        }
    ]

    with open("data/questions/avukatlik_uyap.jsonl", "w", encoding="utf-8") as f:
        for q in avukatlik_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    # 8. DİĞER (Aile/Miras) (diger.jsonl)
    diger_questions = [
        {
            "id": "diger_001",
            "area": "aile_miras_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L2",
            "question": "Murisin vefat tarihi 01.07.2026'dır. Yasal mirasçıların mirasın reddi (reddi miras) hakkını kullanabilmesi için Türk Medeni Kanunu'na göre hak düşürücü süre ne kadardır ve en geç hangi tarihe kadar reddi miras talebinde bulunulmalıdır? Adım adım hesaplayınız.",
            "expected_answer": "1. TMK m. 606 uyarınca miras, 'üç ay' içinde reddolunabilir.\n2. Yasal mirasçılar için bu süre, mirasbırakanın ölümünü öğrendikleri tarihten itibaren başlar. Ölüm 01.07.2026 tarihinde öğrenilmiştir. Süre 02.07.2026 tarihinde başlar.\n3. Üç aylık sürenin son günü 01.10.2026 Perşembe günü mesai saati bitimidir (veya UYAP üzerinden 23:59). Resmi tatile denk gelmediği için uzama uygulanmaz.",
            "legal_basis": ["TMK m.606"],
            "reference_text": "TMK Madde 606 - Miras, üç ay içinde reddolunabilir. Yasal mirasçılar için bu süre, mirasbırakanın ölümünü bildikleri tarihten... işlemeye başlar.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["reddi_miras", "TMK_606", "sure_hesabi"]
        },
        {
            "id": "diger_002",
            "area": "aile_miras_hukuku",
            "task_type": "mcq",
            "difficulty": "L1",
            "question": "Türk Medeni Kanunu'na göre, eşlerin anlaşmalı boşanma davası açabilmesi için evlilik birliğinin en az ne kadar sürmüş olması şarttır?\nA) 6 ay\nB) 1 yıl\nC) 2 yıl\nD) 3 yıl\nE) Evlilik süresi şartı yoktur",
            "expected_answer": "B",
            "legal_basis": ["TMK m.166/3"],
            "reference_text": "TMK Madde 166 - ... 3. Evlilik en az bir yıl sürmüş ise, eşlerin birlikte başvurması ya da bir eşin diğerinin davasını kabul etmesi hâlinde, evlilik birliği temelinden sarsılmış sayılır.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["anlasmali_bosanma", "evlilik_suresi", "mcq"]
        },
        {
            "id": "diger_003",
            "area": "aile_miras_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L4",
            "question": "Eğitime Gönül Verenler Derneği, 01.03.2024 tarihinde, bir olağan genel kurul toplantısı yapmıştır. Genel kurulda toplantıya katılan üyelerin salt çoğunluğuyla, toplantı gündeminde yer almamasına rağmen yönetim kurulunun ibrasına yönelik karar ve tüzükte yer alan üyelik koşullarının değiştirilmesi yönünde karar alınmıştır. Ancak üye A bu toplantıya katılmamıştır. Dernek yönetim kurulu da derneğe ait bir taşınmazın satılması kararı almıştır. Dernek genel kurul ve yönetim kurulu kararlarına karşı A, hangi hukuki yollara başvurabilir? Süre ve yetki detaylarıyla açıklayınız.",
            "expected_answer": "1. Genel kurulun gündem dışı ibra kararına karşı: Dernek genel kurulunda gündeme bağlılık ilkesi esastır (TMK m. 79/2). Gündemde yer almayan ibra konusu görüşüldüğünden karar kanuna aykırıdır. Üye A toplantıya katılmadığından, kararı öğrenmesinden itibaren 1 ay ve herhalde karar tarihinden itibaren 3 ay içinde Sulh Hukuk Mahkemesi'ne başvurarak genel kurul kararının iptalini talep edebilir (TMK m. 83/1).\n2. Tüzük değişikliği kararına karşı: Dernek tüzük değişikliği kararları toplantıya katılan üyelerin 2/3 çoğunluğuyla alınmalıdır (TMK m. 81). Karar yeter sayısına uyulmamasının yaptırımı hakkında Yargıtay yok hükmünde (yokluk) olduğunu kabul etmektedir. Yokluğun tespiti davası hukuki yararı olan herkesçe, süreye tabi olmaksızın her zaman açılabilir.\n3. Yönetim kurulu kararına (taşınmaz satışı) karşı: Yönetim kurulu kararlarına karşı üyeler doğrudan mahkemeye iptal davası açamazlar (TMK m. 83/2). Karara karşı öncelikle genel kurula şikayet yoluna gidilmelidir. Genel kurul şikayeti görüp karara bağladıktan sonra, üye gerekirse genel kurulun bu kararının iptali için mahkemeye gidebilir.",
            "legal_basis": ["TMK m.79/2", "TMK m.81", "TMK m.83"],
            "reference_text": "TMK Madde 79 - ... Genel kurul toplantısında yalnız gündemde yer alan maddeler görüşülür...\nTMK Madde 81 - ... Tüzük değişikliği kararları, toplantıya katılan üyelerin üçte iki çoğunluğuyla alınabilir.\nTMK Madde 83 - Toplantıda hazır bulunan ve karara aykırı kalarak karşı oy kullanan veya toplantıda hazır bulunmayan her üye... iptal davası açabilir. Yönetim kurulu kararlarına karşı genel kurul denetim ve şikayet yolu tüketilmeden doğrudan iptal davası açılamaz.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["dernekler", "gundeme_baglilik", "tuzuk_degisikligi", "somut_olay"]
        },
        {
            "id": "diger_004",
            "area": "aile_miras_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Eşler Ahmet Kara ve Ayşe Kara anlaşmalı olarak boşanmak istemektedir. Tarafların müşterek 1 adet çocukları (7 yaşında) olup velayeti anneye verilecektir. Baba çocuk için aylık 5.000 TL iştirak nafakası ödemeyi, eşler birbirlerinden yoksulluk nafakası veya tazminat talep etmediklerini, ev eşyalarını paylaştıklarını beyan etmektedirler. Aile Mahkemesine sunulmak üzere anlaşmalı boşanma protokolü taslağı hazırlayınız.",
            "expected_answer": "Protokol Başlığı: ANLAŞMALI BOŞANMA PROTOKOLÜ\nTaraflar: 1- Ahmet Kara 2- Ayşe Kara\nKonu: Boşanma ve ferilerine ilişkin anlaşma.\n1. Velayet: Müşterek çocuk ...'in velayeti anne Ayşe Kara'ya verilecektir.\n2. İştirak Nafakası: Baba Ahmet Kara, çocuk için her ay 5.000 TL iştirak nafakası ödeyecektir.\n3. Maddi/Manevi Tazminat ve Nafaka: Taraflar karşılıklı olarak maddi-manevi tazminat ve yoksulluk nafakası talep etmemektedir.\n4. Mal Paylaşımı: Eşyalar paylaşılmış olup tarafların birbirlerinden mal rejimine dayalı alacak talebi yoktur.\nİmzalar: Ahmet Kara (İmza) Ayşe Kara (İmza)",
            "legal_basis": ["TMK m.166/3", "TMK m.182"],
            "reference_text": "TMK Madde 166 - ... Hâkim, boşanmanın malî sonuçları ve çocukların durumu ile ilgili olmak üzere taraflarca kabul edilen protokolü uygun bulması hâlinde boşanmaya hükmeder.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["anlasmali_bosanma", "protokol", "belge_uretimi"]
        },
        {
            "id": "diger_005",
            "area": "aile_miras_hukuku",
            "task_type": "hata_yakalama",
            "difficulty": "L3",
            "question": "Aşağıdaki dava dilekçesi paragrafındaki boşanmadan sonra açılacak nafaka/tazminat davalarındaki zamanaşımına ilişkin hatayı bularak analiz ediniz.\n\n***\n... Taraflar arasında görülen boşanma davası 01.05.2025 tarihinde kesinleşmiştir. Müvekkil, boşanma kararından sonra maddi durumu kötüleştiği için yoksulluk nafakası talep etmek istemektedir. Türk Medeni Kanunu m. 178 uyarınca, boşanmanın kesinleşmesinden itibaren 10 yıllık genel zamanaşımı süresi içinde bu nafaka davası açılabileceğinden, işbu davayı yasal süresi içinde açmaktayız...\n***",
            "expected_answer": "Dilekçedeki hata zamanaşımı süresinin 10 yıl olarak belirtilmesidir.\n1. TMK m. 178 uyarınca, evliliğin boşanma sebebiyle sona ermesinden doğan dava hakları (tazminat ve nafaka talepleri), boşanma hükmünün kesinleşmesinden itibaren 'bir yıl' geçmekle zamanaşımına uğrar.\n2. Kesinleşme tarihi 01.05.2025 olduğundan, nafaka davası açma süresi 01.05.2026 tarihinde sona ermiştir. \n3. 10 yıllık süre iddiası yanlıştır ve davanın süre yönünden reddine yol açar. Güncel süre 1 yıldır.",
            "legal_basis": ["TMK m.178"],
            "reference_text": "TMK Madde 178 - Evliliğin boşanma sebebiyle sona ermesinden doğan dava hakları, boşanma hükmünün kesinleşmesinden itibaren bir yıl geçmekle zamanaşımına uğrar.",
            "rubric_type": "hata_yakalama",
            "rubric": {
                "hatalarin_tespiti": 40,
                "dogru_alternatifin_sunumu": 30,
                "risk_analizi_ve_strateji": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Boşanmadan sonraki tazminat ve nafaka taleplerinde zamanaşımının 1 yıl yerine 10 yıl sanılması hatası.",
            "tags": ["boşanma_zamanaşımı", "tmk_178", "hata_yakalama"]
        },
        {
            "id": "diger_006",
            "area": "aile_miras_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L5",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": "unfavorable_action",
            "trap_details": "Miras payı hesabı. Modelin çocukların varlığında eşin payının 1/4 olduğunu net belirtmesi gerekir.",
            "tags": ["miras_payi", "sag_kalan_es", "trap"]
        },
        {
            "id": "diger_007",
            "area": "aile_miras_hukuku",
            "task_type": "mcq",
            "difficulty": "L2",
            "question": "Boşanma davalarında yetkili mahkeme neresidir?\nA) Sadece davacının yerleşim yeri mahkemesi\nB) Sadece davalının yerleşim yeri mahkemesi\nC) Eşlerden birinin yerleşim yeri veya davadan önce son defa altı aydan beri birlikte oturdukları yer mahkemesi\nD) Eşlerin evlendikleri yer mahkemesi\nE) Sadece Ankara ve İstanbul mahkemeleri",
            "expected_answer": "C",
            "legal_basis": ["TMK m.168"],
            "reference_text": "TMK Madde 168 - Boşanma veya ayrılık davalarında yetkili mahkeme, eşlerden birinin yerleşim yeri veya davadan önce son defa altı aydan beri birlikte oturdukları yer mahkemesidir.",
            "rubric_type": "mcq",
            "rubric": {},
            "trap_type": None,
            "trap_details": "",
            "tags": ["boşanma_yetki", "tmk_168", "mcq"]
        },
        {
            "id": "diger_008",
            "area": "aile_miras_hukuku",
            "task_type": "sure_hesabi",
            "difficulty": "L3",
            "question": "Babalık davası açma süresi çocuğa kayyım atanmışsa ne kadardır? Kayyım atama kararı kayyıma 01.07.2026 tarihinde tebliğ edilmiştir. Hak düşürücü sürenin son günü nedir? Adım adım hesaplayınız.",
            "expected_answer": "1. TMK m. 301 uyarınca babalık davası, çocuk adına da açılabilir. Çocuğa kayyım atanmışsa dava açma süresi TMK m. 303/4 uyarınca temsilciye kararın tebliğinden itibaren 'bir yıldır'.\n2. Tebliğ tarihi olan 01.07.2026 hesaba katılmaz. Süre 02.07.2026 tarihinde başlar.\n3. Bir yıllık hak düşürücü sürenin son günü 01.07.2027 Perşembe günü mesai bitimidir.",
            "legal_basis": ["TMK m.301", "TMK m.303"],
            "reference_text": "TMK Madde 303 - ... Bir yıllık süre geçtikten sonra gecikmeyi haklı kılan sebepler varsa süre bunların ortadan kalktığı tarihten itibaren işlemeye başlar. Ancak çocuğa kayyım atanmışsa bir yıllık süre tebliğle başlar.",
            "rubric_type": "sure_hesabi",
            "rubric": {
                "sure_hesabi_isabeti": 50,
                "hukuki_dayanak": 30,
                "gerekce_ve_hesap_yolu": 20
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["babalik_davasi", "zamanasimi", "sure_hesabi"]
        },
        {
            "id": "diger_009",
            "area": "aile_miras_hukuku",
            "task_type": "somut_olay_analizi",
            "difficulty": "L3",
            "question": "Müvekkilin kardeşi, alkol bağımlılığı ve malvarlığını kötü yönetmesi nedeniyle ailesine zarar vermektedir. Aile, kardeşin kısıtlanarak kendisine vasi tayin edilmesini istemektedir. Vesayet davası hangi mahkemede açılmalıdır? Kısıtlanma nedenleri ve kanuni usul nedir?",
            "expected_answer": "1. Vesayet davalarında görevli mahkeme Sulh Hukuk Mahkemesidir (TMK m. 397).\n2. TMK m. 406 uyarınca savurganlık, alkol veya uyuşturucu madde bağımlılığı, kötü yaşama tarzı veya malvarlığını kötü yönetmesi nedeniyle kendisini veya ailesini darlık veya yoksulluğa düşürme tehlikesine yol açan ve bu yüzden sürekli korunmaya ve bakıma muhtaç olan ya da başkalarının güvenliğini tehdit eden her ergin kısıtlanır.\n3. Mahkeme savurganlık veya bağımlılık nedeniyle kısıtlama kararı vermeden önce ilgili kişiyi dinlemek zorundadır.",
            "legal_basis": ["TMK m.397", "TMK m.406"],
            "reference_text": "TMK Madde 406 - Savurganlığı, alkol veya uyuşturucu madde bağımlılığı, kötü yaşama tarzı veya malvarlığını kötü yönetmesi sebebiyle kendisini veya ailesini darlık veya yoksulluğa düşürme tehlikesine yol açan... her ergin kısıtlanır.",
            "rubric_type": "somut_olay_analizi",
            "rubric": {
                "hukuki_dogruluk": 35,
                "somut_olaya_uygulama": 20,
                "usul_ve_sureler": 15,
                "stratejik_yol_haritasi": 20,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["vesayet", "vasi_tayin", "somut_olay"]
        },
        {
            "id": "diger_010",
            "area": "aile_miras_hukuku",
            "task_type": "belge_uretimi",
            "difficulty": "L3",
            "question": "Muris Mustafa Yılmaz vefat etmiştir. Yasal mirasçısı olan oğlu Ahmet Yılmaz, mirasçılık sıfatını gösterir veraset ilamının (mirasçılık belgesi) verilmesi talebiyle Sulh Hukuk Mahkemesine başvuracaktır. Mahkemeye sunulacak veraset ilamı istemli tevzi dilekçesi taslağını hazırlayınız.",
            "expected_answer": "Dilekçe Başlığı: ANKARA NÖBETÇİ SULH HUKUK MAHKEMESİNE\nDavacı (İstem Sahibi): Ahmet Yılmaz (TCKN, Adres)\nVekili: Av. ...\nKonu: Mirasçılık belgesi (veraset ilamı) verilmesi talebimizdir.\nAçıklamalar: Müvekkilin babası Mustafa Yılmaz ... tarihinde vefat etmiştir. Müvekkil yasal mirasçısıdır. İlgili kurum ve kuruluşlarda işlem yapabilmek için mirasçılık oranlarını gösterir veraset ilamının düzenlenmesi gerekmektedir.\nNetice-i Talep: Murisin mirasçılarını ve miras paylarını gösterir mirasçılık belgesinin verilmesini talep ederiz.",
            "legal_basis": ["TMK m.598"],
            "reference_text": "TMK Madde 598 - Başvurusu üzerine yasal mirasçılara, mirasçı olduklarını gösteren bir belge verilir.",
            "rubric_type": "belge_uretimi",
            "rubric": {
                "hukuki_gecerlilik_ve_eksiksizlik": 30,
                "turkce_hukuk_dili_ve_uyap_uygunlugu": 25,
                "somut_olaya_uygunluk_ve_ozellestirme": 20,
                "format_ve_kullanilabilirlik": 15,
                "halusinasyon_yoklugu": 10
            },
            "trap_type": None,
            "trap_details": "",
            "tags": ["veraset_ilami", "mirascilik_belgesi", "belge_uretimi"]
        }
    ]

    with open("data/questions/diger.jsonl", "w", encoding="utf-8") as f:
        for q in diger_questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print("Success: Generated all 8 JSONL files with 10 questions each (total 80 questions) under data/questions/")

if __name__ == "__main__":
    seed()
