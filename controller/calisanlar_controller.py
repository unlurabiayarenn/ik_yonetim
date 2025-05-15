def calisanlari_getir(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.ad, c.soyad, c.pozisyon, c.ise_giris, d.ad as departman 
        FROM Calisanlar c 
        LEFT JOIN Departmanlar d ON c.departman_id = d.id
    """)
    return cursor.fetchall()

def departmanlari_getir(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad FROM Departmanlar")
    return cursor.fetchall()

def calisan_ekle(conn, ad, soyad, pozisyon, giris_tarihi, departman_id):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Calisanlar (ad, soyad, pozisyon, ise_giris, departman_id)
        VALUES (?, ?, ?, ?, ?)
    """, (ad, soyad, pozisyon, giris_tarihi, departman_id))
    conn.commit()

def calisan_sil(conn, calisan_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Calisanlar WHERE id = ?", (calisan_id,))
    conn.commit()

def calisan_guncelle(conn, calisan_id, ad, soyad, pozisyon, ise_giris, departman_id):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE calisanlar
        SET ad = ?, soyad = ?, pozisyon = ?, ise_giris = ?, departman_id = ?
        WHERE id = ?
    """, (ad, soyad, pozisyon, ise_giris, departman_id, calisan_id))
    conn.commit()