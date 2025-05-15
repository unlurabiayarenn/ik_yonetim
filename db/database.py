# db/database.py
import sqlite3
import os

def connect():
    db_yolu = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ik_veritabani.db")
    return sqlite3.connect(db_yolu)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departmanlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT NOT NULL,
        yonetici_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Calisanlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad TEXT,
        soyad TEXT,
        pozisyon TEXT,
        ise_giris DATE,
        departman_id INTEGER,
        FOREIGN KEY(departman_id) REFERENCES Departmanlar(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Izinler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calisan_id INTEGER,
        izin_bas_tarihi DATE,
        izin_bit_tarihi DATE,
        izin_turu TEXT,
        onay_durumu BOOLEAN,
        FOREIGN KEY(calisan_id) REFERENCES Calisanlar(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Maaslar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calisan_id INTEGER,
        ay DATE,
        net_maas REAL,
        brut_maas REAL,
        kesinti REAL,
        prim REAL,
        FOREIGN KEY(calisan_id) REFERENCES Calisanlar(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Egitimler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        egitim_adi TEXT,
        tarih DATE,
        egitmen TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Egitim_Katilim (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        egitim_id INTEGER,
        calisan_id INTEGER,
        FOREIGN KEY(egitim_id) REFERENCES Egitimler(id),
        FOREIGN KEY(calisan_id) REFERENCES Calisanlar(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Performans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calisan_id INTEGER,
        degerlendirme_tarihi DATE,
        puan INTEGER,
        yorum TEXT,
        FOREIGN KEY(calisan_id) REFERENCES Calisanlar(id)
    )
    """)

    conn.commit()
    conn.close()


