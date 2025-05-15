# test_izinler.py gibi bir dosya aç
from controller.izinler_controller import izinleri_getir
from db.database import connect

conn = connect()
veriler = izinleri_getir(conn)

print(">>> Gelen izin verileri:")
for v in veriler:
    print(v)

