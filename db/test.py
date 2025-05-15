# test.py
from db.database import connect

def test_baglanti():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablolar = cursor.fetchall()

    print("📋 Veritabanındaki tablolar:")
    for tablo in tablolar:
        print(f"- {tablo[0]}")

    conn.close()

if __name__ == "__main__":
    test_baglanti()
