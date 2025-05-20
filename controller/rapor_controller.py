# controller/rapor_controller.py

def departmanlari_getir(conn):
    sorgu = "SELECT id, ad FROM Departmanlar ORDER BY ad"
    return conn.execute(sorgu).fetchall()

def calisanlari_getir(conn, departman_id=0):
    if departman_id == 0:
        sorgu = "SELECT id, ad, soyad FROM calisanlar ORDER BY ad, soyad"
        return conn.execute(sorgu).fetchall()
    else:
        sorgu = "SELECT id, ad, soyad FROM calisanlar WHERE departman_id = ? ORDER BY ad, soyad"
        return conn.execute(sorgu, (departman_id,)).fetchall()


def get_rapor_verisi(conn, calisan_id=0, secilen_sayfalar=None, departman_id=0):
    if secilen_sayfalar is None:
        secilen_sayfalar = []

    tum_basliklar = []
    tum_satirlar = []

    for sayfa in secilen_sayfalar:
        if sayfa == "İzinler":
            basliklar = ["Çalışan Adı", "Başlangıç", "Bitiş", "İzin Türü", "Onay Durumu"]
            tum_basliklar.extend(basliklar)

            sorgu = """
                    SELECT c.ad || ' ' || c.soyad, i.izin_bas_tarihi, i.izin_bit_tarihi, i.izin_turu, i.onay_durumu
                    FROM izinler i
                             JOIN calisanlar c ON c.id = i.calisan_id \
                    """
            params = []
            if calisan_id:
                sorgu += " WHERE c.id = ?"
                params.append(calisan_id)
            elif departman_id:
                sorgu += " WHERE c.departman_id = ?"
                params.append(departman_id)
            sorgu += " ORDER BY i.izin_bas_tarihi DESC"
            veriler = conn.execute(sorgu, params).fetchall()
            tum_satirlar.extend(veriler)

        elif sayfa == "Maaşlar":
            basliklar = ["Çalışan Adı", "Dönem", "Net Maaş"]
            tum_basliklar.extend(basliklar)

            sorgu = """
                    SELECT c.ad || ' ' || c.soyad, m.ay, m.net_maas
                    FROM maaslar m
                             JOIN calisanlar c ON c.id = m.calisan_id \
                    """
            params = []
            if calisan_id:
                sorgu += " WHERE c.id = ?"
                params.append(calisan_id)
            elif departman_id:
                sorgu += " WHERE c.departman_id = ?"
                params.append(departman_id)
            sorgu += " ORDER BY m.ay DESC"
            veriler = conn.execute(sorgu, params).fetchall()
            tum_satirlar.extend(veriler)

        elif sayfa == "Performans":
            basliklar = ["Çalışan Adı", "Puan", "Yorum", "Tarih"]
            tum_basliklar.extend(basliklar)

            sorgu = """
                    SELECT c.ad || ' ' || c.soyad, p.puan, p.yorum, p.degerlendirme_tarihi
                    FROM performans p
                             JOIN calisanlar c ON c.id = p.calisan_id \
                    """
            params = []
            if calisan_id:
                sorgu += " WHERE c.id = ?"
                params.append(calisan_id)
            elif departman_id:
                sorgu += " WHERE c.departman_id = ?"
                params.append(departman_id)
            sorgu += " ORDER BY p.degerlendirme_tarihi DESC"
            veriler = conn.execute(sorgu, params).fetchall()
            tum_satirlar.extend(veriler)

        elif sayfa == "Eğitimler":
            basliklar = ["Çalışan Adı", "Eğitim Adı", "Tarih", "Katılım Durumu"]
            tum_basliklar.extend(basliklar)

            sorgu = """
                    SELECT c.ad || ' ' || c.soyad, \
                           e.egitim_adi, \
                           e.tarih,
                           CASE \
                               WHEN ek.calisan_id IS NOT NULL THEN '✔️ Katıldı' \
                               ELSE '❌ Katılmadı' END AS katilim_durumu
                    FROM egitimler e
                             JOIN (SELECT DISTINCT egitim_id \
                                   FROM egitim_katilim) katilim_var ON katilim_var.egitim_id = e.id
                             JOIN calisanlar c ON 1 = 1
                             LEFT JOIN egitim_katilim ek ON ek.egitim_id = e.id AND ek.calisan_id = c.id \
                    """
            params = []
            if calisan_id:
                sorgu += " WHERE c.id = ?"
                params.append(calisan_id)
            elif departman_id:
                sorgu += " WHERE c.departman_id = ?"
                params.append(departman_id)
            sorgu += " ORDER BY e.tarih DESC"
            veriler = conn.execute(sorgu, params).fetchall()
            tum_satirlar.extend(veriler)

    return tum_basliklar, tum_satirlar