from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from controller.rapor_controller import (
    departmanlari_getir, calisanlari_getir, get_rapor_verisi
)

class RaporView:
    def __init__(self, ui):
        self.ui = ui
        self.veritabani_baglantisi()
        self.departmanlari_yukle()
        self.calisanlari_yukle()

        self.ui.departmanSecimi_4.currentIndexChanged.connect(self.departmanSecimi_changed)
        self.ui.btnRaporOlustur.clicked.connect(self.rapor_olustur)

    def veritabani_baglantisi(self):
        from db.database import connect
        self.conn = connect()

    def departmanlari_yukle(self):
        self.ui.departmanSecimi_4.clear()
        self.ui.departmanSecimi_4.addItem("Tüm Departmanlar", 0)
        for id_, ad in departmanlari_getir(self.conn):
            self.ui.departmanSecimi_4.addItem(ad, id_)

    def departmanSecimi_changed(self):
        departman_id = self.ui.departmanSecimi_4.currentData()
        self.ui.calisanSecimi_2.clear()

        self.ui.calisanSecimi_2.addItem("Tüm Çalışanlar", 0)
        if departman_id != 0:
            calisanlar = calisanlari_getir(self.conn, departman_id)
            for calisan_id, ad, soyad in calisanlar:
                self.ui.calisanSecimi_2.addItem(f"{ad} {soyad}", calisan_id)

    def calisanlari_yukle(self, departman_id=0):
        self.ui.calisanSecimi_2.clear()
        self.ui.calisanSecimi_2.addItem("Tüm Çalışanlar", 0)
        if departman_id != 0:
            calisanlar = calisanlari_getir(self.conn, departman_id)
            for calisan_id, ad, soyad in calisanlar:
                self.ui.calisanSecimi_2.addItem(f"{ad} {soyad}", calisan_id)

    def rapor_olustur(self):
        secilen_departman_id = self.ui.departmanSecimi_4.currentData()
        secilen_calisan_id = self.ui.calisanSecimi_2.currentData()

        secilen_sayfalar = []
        if self.ui.izinCB.isChecked():
            secilen_sayfalar.append("İzinler")
        if self.ui.maasCB.isChecked():
            secilen_sayfalar.append("Maaşlar")
        if self.ui.performansCB.isChecked():
            secilen_sayfalar.append("Performans")
        if self.ui.egitimveKatilmaCB.isChecked():
            secilen_sayfalar.append("Eğitimler")

        if not secilen_sayfalar:
            QMessageBox.warning(self.ui, "Uyarı", "Lütfen en az bir sayfa seçiniz.")
            return

        # Departman seçili ama tüm çalışanlar seçilmişse çalışan seçimi zorunlu değil, ama eğer departman seçili ve çalışan 0 değilse sorun yok
        if secilen_departman_id != 0 and secilen_calisan_id == 0 and len(secilen_sayfalar) > 0:
            # Eğer rapor kapsamını departmana göre görmek istiyorsan burayı yoruma alabilirsin.
            # QMessageBox.warning(self.ui, "Uyarı", "Lütfen bir çalışan seçiniz.")
            # return
            pass

        tum_basliklar, tum_satirlar = get_rapor_verisi(
            self.conn,
            calisan_id=secilen_calisan_id,
            secilen_sayfalar=secilen_sayfalar,
            departman_id=secilen_departman_id
        )
        self.tblRaporu_doldur(tum_basliklar, tum_satirlar)

    def tblRaporu_doldur(self, basliklar, satirlar):
        self.ui.tblRapor.clear()
        self.ui.tblRapor.setRowCount(0)
        self.ui.tblRapor.setColumnCount(0)

        if not satirlar:
            QMessageBox.information(self.ui, "Bilgi", "Seçilen kriterlere ait veri bulunamadı.")
            return

        self.ui.tblRapor.setColumnCount(len(basliklar))
        self.ui.tblRapor.setHorizontalHeaderLabels(basliklar)

        for satir in satirlar:
            # Satır eksikse boş string ile tamamla
            if len(satir) < len(basliklar):
                satir = list(satir) + [""] * (len(basliklar) - len(satir))

            satir_indeksi = self.ui.tblRapor.rowCount()
            self.ui.tblRapor.insertRow(satir_indeksi)
            for i, hucre in enumerate(satir):
                self.ui.tblRapor.setItem(satir_indeksi, i, QTableWidgetItem(str(hucre)))
