def izinleri_getir(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            i.id,
            cal.ad || ' ' || cal.soyad AS calisan,
            i.izin_bas_tarihi,
            i.izin_bit_tarihi,
            i.izin_turu,
            CASE i.onay_durumu
                WHEN 1 THEN 'Onaylandı'
                WHEN 0 THEN 'Reddedildi'
                ELSE 'Bilinmiyor'
            END AS onay_durumu,
            cal.departman_id,
            cal.id  -- çalışan_id sütunu burada eklendi
        FROM Izinler i
        JOIN Calisanlar cal ON i.calisan_id = cal.id    
    """)
    return cursor.fetchall()


def departmanlari_getir(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad FROM Departmanlar")
    return cursor.fetchall()

def calisanlari_getir(conn, departman_id=0):
    cursor = conn.cursor()
    try:
        departman_id = int(departman_id)
    except:
        departman_id = 0

    if departman_id == 0:
        cursor.execute("SELECT id, ad, soyad FROM calisanlar")
    else:
        cursor.execute("SELECT id, ad, soyad FROM calisanlar WHERE departman_id = ?", (departman_id,))
    return cursor.fetchall()

def izin_ekle(conn, calisan_id, bas_tarih, bit_tarih, izin_turu, onay):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO izinler (calisan_id, izin_bas_tarihi, izin_bit_tarihi, izin_turu, onay_durumu)
        VALUES (?, ?, ?, ?, ?)
    """, (calisan_id, bas_tarih, bit_tarih, izin_turu, onay))
    conn.commit()

def izin_sil(conn, izin_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Izinler WHERE id = ?", (izin_id,))
    conn.commit()

def izin_guncelle(conn, izin_id, calisan_id, bas_tarih, bit_tarih, izin_turu, onay):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE izinler
        SET calisan_id=?, izin_bas_tarihi=?, izin_bit_tarihi=?, izin_turu=?, onay_durumu=?
        WHERE id=?
    """, (calisan_id, bas_tarih, bit_tarih, izin_turu, onay, izin_id))
    conn.commit()

def izin_ara(conn, departman_id="", calisan_id="", izin_turu="", izin_baslangic="", izin_bitis="", onay_durumu=""):
    sorgu = """
        SELECT i.id, c.ad || ' ' || c.soyad AS calisan, d.ad, i.izin_turu, i.izin_bas_tarihi, i.izin_bit_tarihi, i.onay_durumu
        FROM izinler i
        JOIN calisanlar c ON i.calisan_id = c.id
        JOIN departmanlar d ON c.departman_id = d.id
        WHERE 1=1
    """
    degerler = []

    if departman_id and departman_id != "0":
        sorgu += " AND c.departman_id = ?"
        degerler.append(departman_id)

    if calisan_id:
        sorgu += " AND c.id = ?"
        degerler.append(calisan_id)

    if izin_turu:
        sorgu += " AND i.izin_turu = ?"
        degerler.append(izin_turu)

    if izin_baslangic:
        sorgu += " AND i.izin_bas_tarihi >= ?"
        degerler.append(izin_baslangic)

    if izin_bitis:
        sorgu += " AND i.izin_bit_tarihi <= ?"
        degerler.append(izin_bitis)

    if onay_durumu:
        sorgu += " AND i.onay_durumu = ?"
        degerler.append(onay_durumu)

    cursor = conn.cursor()
    cursor.execute(sorgu, degerler)
    return cursor.fetchall()
