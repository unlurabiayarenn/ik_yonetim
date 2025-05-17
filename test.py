from db.database import connect

conn = connect()
cursor = conn.cursor()

# Maaslar tablosu
cursor.execute("""
        SELECT 
            m.id, 
            c.ad || ' ' || c.soyad AS calisan, 
            d.ad AS departman, 
            m.ay, 
            m.brut_maas, 
            m.kesinti, 
            m.prim, 
            m.net_maas
        FROM maaslar m
        JOIN calisanlar c ON m.calisan_id = c.id
        JOIN departmanlar d ON c.departman_id = d.id
        WHERE 1=1
    """)
maaslar = cursor.fetchall()
print("Maaslar tablosu:", maaslar)


