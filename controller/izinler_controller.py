def izinleri_getir(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            i.id, 
            c.ad || ' ' || c.soyad AS calisan, 
            i.izin_bas_tarihi, 
            i.izin_bit_tarihi,
            i.izin_turu, 
            CASE i.onay_durumu 
                WHEN 1 THEN 'Onaylandı' 
                WHEN 0 THEN 'Reddedildi' 
                ELSE 'Bilinmiyor' 
            END AS onay_durumu,
            c.departman_id
        FROM Izinler i
        LEFT JOIN Calisanlar c ON i.calisan_id = c.id
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
        INSERT INTO izinler (calisan_id, baslangic_tarihi, bitis_tarihi, izin_turu, onay_durumu)
        VALUES (?, ?, ?, ?, ?)
    """, (calisan_id, bas_tarih, bit_tarih, izin_turu, onay))
    conn.commit()

def izin_guncelle(conn, izin_id, calisan_id, bas_tarih, bit_tarih, izin_turu, onay):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE izinler
        SET calisan_id=?, baslangic_tarihi=?, bitis_tarihi=?, izin_turu=?, onay_durumu=?
        WHERE id=?
    """, (calisan_id, bas_tarih, bit_tarih, izin_turu, onay, izin_id))
    conn.commit()

