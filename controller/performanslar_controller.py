def performansları_getir(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.id, 
            c.ad || ' ' || c.soyad AS calisan_adi, 
            p.degerlendirme_tarihi, 
            p.puan, 
            p.yorum,
            c.departman_id,      -- Departman ID
            c.id                 -- Çalışan ID
        FROM Performans p
        LEFT JOIN Calisanlar c ON p.calisan_id = c.id
        ORDER BY p.id
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

def performans_ekle(conn, calisan_id, degerlendirme_tarihi, puan, yorum):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Performans (calisan_id, degerlendirme_tarihi, puan, yorum)
        VALUES (?, ?, ?, ?)
    """, (calisan_id, degerlendirme_tarihi, puan, yorum))
    conn.commit()

def performans_sil(conn, performans_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Performans WHERE id = ?", (performans_id,))
    conn.commit()

def performans_guncelle(conn, perf_id, calisan_id, degerlendirme_tarihi, puan, yorum):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Performans
        SET calisan_id=?, degerlendirme_tarihi=?, puan=?, yorum=?
        WHERE id = ?
    """, (calisan_id, degerlendirme_tarihi, puan, yorum, perf_id))
    conn.commit()

def performans_ara(conn, departman_id = None, calisan_id=None, degerlendirme_tarihi=None, puan=None):
    sorgu = """
        SELECT 
            c.ad || ' ' || c.soyad AS calisan_ad_soyad,
            d.ad AS departman_ad,
            p.degerlendirme_tarihi,
            p.puan,
            p.yorum
        FROM performans p 
        JOIN calisanlar c ON p.calisan_id = c.id
        JOIN departmanlar d ON c.departman_id = d.id
        WHERE 1=1
    """
    degerler = []

    if departman_id:
        sorgu += " AND c.departman_id = ?"
        degerler.append(departman_id)
    if calisan_id:
        sorgu += " AND c.id = ?"
        degerler.append(calisan_id)
    if degerlendirme_tarihi:
        sorgu += " AND strftime('%Y-%m', p.degerlendirme_tarihi) = ?"
        degerler.append(degerlendirme_tarihi)
    if puan:
        sorgu += " AND p.puan = ?"
        degerler.append(puan)

    cursor = conn.cursor()
    cursor.execute(sorgu, degerler)
    return cursor.fetchall()


