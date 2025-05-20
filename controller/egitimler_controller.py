def get_egitimler(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.egitim_adi, e.egitmen, e.tarih from Egitimler e
    """)
    return cursor.fetchall()

def egitim_ekle(conn, egitim_adi, egitmen, tarih):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Egitimler (egitim_adi, egitmen, tarih)
        VALUES (?, ?, ?)
    """, (egitim_adi, egitmen, tarih))
    conn.commit()

def get_egitimKatilim(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ek.id, c.ad || ' ' || c.soyad AS calisan_ad_soyad, e.egitim_adi AS egitim_ad
        FROM Egitim_Katilim ek
        JOIN calisanlar c ON ek.calisan_id = c.id
        JOIN Egitimler e ON ek.egitim_id = e.id;
    """)
    return cursor.fetchall()

def get_egitimListesi(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.egitim_adi from Egitimler e
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

def egitimKatilimEkle(conn, calisan_id, egitim_id):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Egitim_Katilim (calisan_id, egitim_id)
        VALUES (?, ?)
    """, (calisan_id, egitim_id))
    conn.commit()
