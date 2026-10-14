from legaluga_bench.scoring.citations import (
    case_key,
    extract_case_citations,
    extract_statute_citations,
    match_case,
    norm_article,
    norm_chamber,
    norm_court,
    norm_date,
    norm_law_no,
    norm_number,
)


def test_numbers_and_dates():
    assert norm_number("E. 2019/01234") == "2019/1234"
    assert norm_number("2019 / 7") == "2019/7"
    assert norm_number("2013/7-591") == "2013/7-591"
    assert norm_number("yok") is None
    assert norm_date("12.03.2020") == "2020-03-12"
    assert norm_date("12/3/2020") == "2020-03-12"
    assert norm_date("2020-03-12") == "2020-03-12"
    assert norm_date("12 Mart 2020") == "2020-03-12"
    assert norm_date("31.02.2020") is None


def test_courts_and_chambers():
    assert norm_court("Yargıtay") == "yargitay"
    assert norm_court("Danıştay") == "danistay"
    assert norm_court("Anayasa Mahkemesi") == "aym"
    assert norm_court("Ankara Bölge Adliye Mahkemesi") == "bam"
    assert norm_chamber("yargitay", "9. HD") == "H9"
    assert norm_chamber("yargitay", "12. Ceza Dairesi") == "C12"
    assert norm_chamber("yargitay", "Hukuk Genel Kurulu") == "HGK"
    assert norm_chamber("yargitay", "H23") == "H23"
    assert norm_chamber("danistay", "5. Daire") == "D5"
    assert norm_chamber("danistay", "İDDK") == "IDDK"
    assert norm_chamber("bam", "Ankara Bölge Adliye Mahkemesi 25. Hukuk Dairesi") == "ANKARA-H25"


def test_case_key_and_match():
    gold = {"court": "Yargıtay", "chamber": "3. Hukuk Dairesi", "esas": "2010/119", "karar": "2010/478",
            "date": "2010-01-21"}
    k = case_key(gold)
    assert (k.court, k.chamber, k.esas, k.karar) == ("yargitay", "H3", "2010/119", "2010/478")
    m = match_case({"court": "Y.", "chamber": "3. HD", "esas": "2010/119", "karar": "2010/478",
                    "date": "21.01.2010"}, gold)
    assert m.exact and m.date
    wrong_chamber = match_case({"court": "Yargıtay", "chamber": "9. HD", "esas": "2010/119",
                                "karar": "2010/478"}, gold)
    assert not wrong_chamber.exact
    no_chamber = match_case({"esas": "2010/119", "karar": "2010/478"}, gold)
    assert no_chamber.exact  # daire belirtilmemişse numaralar yeterli
    assert not match_case({"esas": "2010/119", "karar": "2010/479"}, gold).exact


def test_bam_city_optional():
    gold = {"court": "Bölge Adliye Mahkemesi", "chamber": "Ankara Bölge Adliye Mahkemesi 25. Hukuk Dairesi",
            "esas": "2024/796", "karar": "2024/1075"}
    assert match_case({"court": "BAM", "chamber": "25. Hukuk Dairesi", "esas": "2024/796",
                       "karar": "2024/1075"}, gold).exact
    assert not match_case({"court": "BAM", "chamber": "İstanbul BAM 25. HD", "esas": "2024/796",
                           "karar": "2024/1075"}, gold).exact


def test_aym_individual_application():
    gold = {"court": "Anayasa Mahkemesi", "basvuru_no": "2014/12345"}
    assert match_case({"court": "AYM", "basvuru_no": "2014/12345"}, gold).exact
    assert not match_case({"court": "AYM", "basvuru_no": "2014/12346"}, gold).exact


def test_extract_case_citations_free_text():
    text = (
        "Yargıtay 3. Hukuk Dairesi'nin 21.01.2010 tarihli, 2010/119 E., 2010/478 K. sayılı kararında ... "
        "Yargıtay HGK E. 2017/990, K. 2017/954, T. 10.05.2017. Danıştay 5. Daire E:2018/10 K:2021/55."
    )
    keys = {case_key(c).short() for c in extract_case_citations(text)}
    assert "yargitay|H3|E.2010/119|K.2010/478" in keys
    assert "yargitay|HGK|E.2017/990|K.2017/954" in keys
    assert "danistay|D5|E.2018/10|K.2021/55" in keys


def test_statutes():
    assert norm_law_no("TBK") == "6098"
    assert norm_law_no("6098 sayılı Türk Borçlar Kanunu") == "6098"
    assert norm_law_no("Hukuk Muhakemeleri Kanunu") == "6100"
    assert norm_article("m.344/1") == "344"
    assert norm_article("Geçici Madde 2") == "gecici-2"
    assert norm_article("183/A") == "183/A"
    found = extract_statute_citations("TBK m.344/1 ve 6100 sayılı Hukuk Muhakemeleri Kanunu'nun 119. maddesi, İİK 62")
    assert {(c["law_no"], c["article"]) for c in found} == {("6098", "344"), ("6100", "119"), ("2004", "62")}
