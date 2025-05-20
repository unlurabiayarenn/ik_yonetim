from PyQt5 import QtWidgets, QtCore
from controller.egitimler_controller import (
    get_egitimler, egitim_ekle as ekle, get_egitimKatilim, get_egitimListesi, departmanlari_getir,
    calisanlari_getir, egitimKatilimEkle
)

class EgitimlerView:
    def __init__(self, ui):
        self.ui = ui
        self.veritabani_baglantisi()
        self.egitimleri_yukle()
        self.egitimKatilim_yukle()
        self.egitim_listele()
        self.departmanlari_yukle()
        self.calisanlari_yukle()

        #self.ui.tblEgitimler.itemSelectionChanged.connect(self.formu_doldur)
        self.ui.btnEgitimKaydet.clicked.connect(self.egitim_ekle)
        self.ui.departmanSecimi_Egitim.currentIndexChanged.connect(self.departmanSecimi_changed)
        self.ui.btnKatilimEkle.clicked.connect(self.egitimKatilimEkle)

    def veritabani_baglantisi(self):
        from db.database import connect
        self.conn = connect()

    def egitimleri_yukle(self):
        veriler = get_egitimler(self.conn)
        self.ui.tblEgitimler.setRowCount(0)
        for row_index, row_data in enumerate(veriler):
            self.ui.tblEgitimler.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.tblEgitimler.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(data)))
            self.ui.tblEgitimler.setRowHidden(row_index, False)  #Satırı görünür hale getir
        self.ui.tblEgitimler.setColumnHidden(0, True)

    def egitim_ekle(self):
        egitim_adi = self.ui.EgitimAdi.text().strip()
        egitmen = self.ui.EgitmenAdi.text().strip()
        tarih = self.ui.EgitimTarihi.date().toString("yyyy-MM-dd")

        if not egitim_adi or not egitmen or not tarih:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        ekle(self.conn, egitim_adi, egitmen, tarih)

        self.egitimleri_yukle()
        self.formu_temizle()

    def formu_temizle(self ):
        self.ui.EgitimAdi.clear()
        self.ui.EgitmenAdi.clear()
        self.ui.EgitimTarihi.setDate(QtCore.QDate(2000, 1, 1))
        self.egitimleri_yukle()

    def egitimKatilim_yukle(self):
        veriler = get_egitimKatilim(self.conn)
        self.ui.tblKatilimListesi.setRowCount(0)
        for row_index, row_data in enumerate(veriler):
            self.ui.tblKatilimListesi.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.tblKatilimListesi.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(data)))
            self.ui.tblKatilimListesi.setRowHidden(row_index, False)  #Satırı görünür hale getir
        self.ui.tblKatilimListesi.setColumnHidden(0, True)

    def egitim_listele(self):
        self.ui.EgitimSecimi.clear()
        self.ui.EgitimSecimi.addItem("Eğitimler", 0)
        for id_, ad in get_egitimListesi(self.conn):
            self.ui.EgitimSecimi.addItem(ad, id_)

    def departmanlari_yukle(self):
        self.ui.departmanSecimi_Egitim.clear()
        self.ui.departmanSecimi_Egitim.addItem("Tüm Departmanlar", 0)
        for id_, ad in departmanlari_getir(self.conn):
            self.ui.departmanSecimi_Egitim.addItem(ad, id_)

    def departmanSecimi_changed(self):
        departman_id = self.ui.departmanSecimi_Egitim.currentData()
        if departman_id == 0:
            self.ui.CalisanSecimi.clear()
            self.ui.CalisanSecimi.addItem("Önce departman seçin", 0)
            return

        self.calisanlari_yukle(departman_id)
        self.ui.CalisanSecimi.setCurrentIndex(0)

    def calisanlari_yukle(self, departman_id=0):
        self.ui.CalisanSecimi.clear()

        if departman_id == 0:
            self.ui.CalisanSecimi.addItem("Önce departman seçin", 0)
            return

        calisanlar = calisanlari_getir(self.conn, departman_id)
        self.ui.CalisanSecimi.addItem("Seçiniz", 0)
        for calisan_id, ad, soyad in calisanlar:
            self.ui.CalisanSecimi.addItem(f"{ad} {soyad}", calisan_id)

    def egitimKatilimEkle(self):
        egitim= self.ui.EgitimSecimi.currentData()
        departman = self.ui.departmanSecimi_Egitim.currentData()
        calisan = self.ui.CalisanSecimi.currentData()

        if not egitim or not departman or not calisan:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        egitimKatilimEkle(self.conn, calisan, egitim)

        self.egitimKatilim_yukle()
        self.formu_temizle()
