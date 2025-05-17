def maaslari_getir(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, c.ad || ' ' || c.soyad AS calisan_adi, m.ay, m.brut_maas, m.kesinti, m.prim, m.net_maas
        FROM Maaslar m
        LEFT JOIN Calisanlar c ON m.calisan_id = c.id
        ORDER BY m.id
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

def calisan_bilgilerini_getir(conn, ad_soyad):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.ad, c.id
        FROM calisanlar c
        JOIN Departmanlar d ON c.departman_id = d.id
        WHERE c.ad || ' ' || c.soyad = ?
    """, (ad_soyad,))
    sonuc = cursor.fetchone()
    return sonuc if sonuc else None

def maas_ekle(conn, calisan_id, ay, net_maas, brut_maas, kesinti, prim):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Maaslar (calisan_id, ay, net_maas, brut_maas, kesinti, prim)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (calisan_id, ay, net_maas, brut_maas, kesinti, prim))
    conn.commit()

def maas_sil(conn, maas_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Maaslar WHERE id = ?", (maas_id,))
    conn.commit()

def maas_guncelle(conn, maas_id, calisan_id, ay, net_maas, brut_maas, kesinti, prim):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Maaslar
        SET calisan_id=?, ay=?, net_maas=?, brut_maas=?, kesinti=?, prim=?
        WHERE id = ?
    """, (calisan_id, ay, net_maas, brut_maas, kesinti, prim, maas_id))
    conn.commit()

def maas_ara(conn, departman_id=None, calisan_id=None, ay=None):
    sorgu = """
        SELECT 
            c.ad || ' ' || c.soyad AS calisan_ad_soyad,
            d.ad AS departman_ad,
            m.ay,
            m.brut_maas,
            m.kesinti,
            m.prim,
            m.net_maas
        FROM maaslar m
        JOIN calisanlar c ON m.calisan_id = c.id
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
    if ay:
        sorgu += " AND strftime('%Y-%m', m.ay) = ?"
        degerler.append(ay)

    cursor = conn.cursor()
    cursor.execute(sorgu, degerler)
    return cursor.fetchall()
