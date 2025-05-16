from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from controller.izinler_controller import (
    izinleri_getir,
    departmanlari_getir,
    calisanlari_getir,
    izin_ekle,
    izin_guncelle,
    izin_ara,
    izin_sil,
)
from db.database import connect

class IzinlerView:
    def __init__(self, ui):
        self.ui = ui
        self.conn = connect()

        # Onay durumu dropdown'u hazırlama
        self.ui.onayDurumu.clear()
        self.ui.onayDurumu.addItem("Seçiniz", -1)
        self.ui.onayDurumu.addItem("Onaylandı", 1)
        self.ui.onayDurumu.addItem("Reddedildi", 0)

        # Departman, çalışan ve izin verilerini yükle
        self.departmanlari_yukle()
        self.calisanlari_yukle()
        self.izinleri_yukle()

        self.ui.izinBasTarihi.setDate(QDate(2000, 1, 1))
        self.ui.izinBitTarihi.setDate(QDate(2000, 1, 1))

        # Sinyaller (event) bağlantıları
        self.ui.tblzin.itemSelectionChanged.connect(self.selection_changed)
        self.ui.tblzin.cellDoubleClicked.connect(self.formu_doldur)
        self.ui.departmanSecimi.currentIndexChanged.connect(self.departmanSecimi_changed)
        self.ui.izinOnay.clicked.connect(self.kaydet)
        self.ui.izinSil.clicked.connect(self.izin_sil)
        self.ui.izinGuncelle.clicked.connect(self.guncelle)
        self.ui.alanTemizle.clicked.connect(self.temizle)
        self.ui.izinAra.clicked.connect(self.izin_ara)

    def departmanlari_yukle(self):
        self.ui.departmanSecimi.clear()
        self.ui.departmanSecimi.addItem("Tüm Departmanlar", 0)
        for id_, ad in departmanlari_getir(self.conn):
            self.ui.departmanSecimi.addItem(ad, id_)

    def departmanSecimi_changed(self):
        departman_id = self.ui.departmanSecimi.currentData()

        if departman_id == 0:
            self.ui.calisanSecimi.clear()
            self.ui.calisanSecimi.addItem("Önce departman seçin", 0)
            return

        self.calisanlari_yukle(departman_id)
        self.ui.izinTuru.clear()
        self.ui.onayDurumu.setCurrentIndex(0)
        self.ui.calisanSecimi.setCurrentIndex(0)

    def calisanlari_yukle(self, departman_id=0):
        self.ui.calisanSecimi.clear()

        if departman_id == 0:
            self.ui.calisanSecimi.addItem("Önce departman seçin", 0)
            return

        calisanlar = calisanlari_getir(self.conn, departman_id)
        self.ui.calisanSecimi.addItem("Seçiniz", 0)
        for calisan_id, ad, soyad in calisanlar:
            self.ui.calisanSecimi.addItem(f"{ad} {soyad}", calisan_id)

    def izinleri_yukle(self):
        veriler = izinleri_getir(self.conn)

        self.ui.tblzin.clear()
        self.ui.tblzin.setRowCount(0)
        self.ui.tblzin.setColumnCount(8)

        headers = [
            "İzin ID",
            "Çalışan Ad Soyad",
            "İzin Başlangıç",
            "İzin Bitiş",
            "İzin Türü",
            "Onay Durumu",
            "Departman ID",
            "Çalışan ID"
        ]
        self.ui.tblzin.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(veriler):
            self.ui.tblzin.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.ui.tblzin.setItem(row_idx, col_idx, item)

        # Gizli sütunlar
        self.ui.tblzin.setColumnHidden(0, True)
        self.ui.tblzin.setColumnHidden(6, True)
        self.ui.tblzin.setColumnHidden(7, True)

    def selection_changed(self):
        selected_ranges = self.ui.tblzin.selectedRanges()
        if not selected_ranges:
            return
        row = selected_ranges[0].topRow()
        self.formu_doldur(row, 0)

    def formu_doldur(self, row, column):
        col_count = self.ui.tblzin.columnCount()
        items = []
        for col in range(col_count):
            item = self.ui.tblzin.item(row, col)
            if item is None:
                return
            items.append(item.text())

        if len(items) < 8:
            return

        izin_id = int(items[0])
        calisan_ad = items[1]
        izin_baslangic = items[2]
        izin_bitis = items[3]
        izin_turu = items[4]
        onay_durumu = items[5]
        departman_id = int(items[6])
        calisan_id = int(items[7])

        self.ui.departmanSecimi.setCurrentIndex(self.ui.departmanSecimi.findData(departman_id))
        self.calisanlari_yukle(departman_id)
        self.ui.calisanSecimi.setCurrentIndex(self.ui.calisanSecimi.findData(calisan_id))

        self.ui.izinTuru.setText(izin_turu)
        self.ui.izinBasTarihi.setDate(QDate.fromString(izin_baslangic, "yyyy-MM-dd"))
        self.ui.izinBitTarihi.setDate(QDate.fromString(izin_bitis, "yyyy-MM-dd"))
        self.ui.onayDurumu.setCurrentIndex(self.ui.onayDurumu.findText(onay_durumu))

    def temizle(self):
        self.ui.departmanSecimi.setCurrentIndex(0)
        self.ui.calisanSecimi.setCurrentIndex(0)
        self.ui.onayDurumu.setCurrentIndex(0)
        self.ui.izinTuru.clear()
        self.ui.tblzin.clearSelection()
        self.izinleri_yukle()

    def kaydet(self):
        calisan_id = self.ui.calisanSecimi.currentData()
        onay = self.ui.onayDurumu.currentData()
        izin_turu = self.ui.izinTuru.text()
        bas_tarih = self.ui.izinBasTarihi.date().toString("yyyy-MM-dd")
        bit_tarih = self.ui.izinBitTarihi.date().toString("yyyy-MM-dd")

        if calisan_id == 0 or onay == -1 or not izin_turu:
            QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurunuz.")
            return

        izin_ekle(self.conn, calisan_id, bas_tarih, bit_tarih, izin_turu, onay)
        self.izinleri_yukle()
        self.temizle()

    def guncelle(self):
        selected_items = self.ui.tblzin.selectedItems()
        if not selected_items:
            QMessageBox.warning(None, "Seçim Yok", "Lütfen güncellenecek bir kayıt seçiniz.")
            return

        izin_id = int(self.ui.tblzin.item(selected_items[0].row(), 0).text())
        calisan_id = self.ui.calisanSecimi.currentData()
        onay = self.ui.onayDurumu.currentData()
        izin_turu = self.ui.izinTuru.text()
        bas_tarih = self.ui.izinBasTarihi.date().toString("yyyy-MM-dd")
        bit_tarih = self.ui.izinBitTarihi.date().toString("yyyy-MM-dd")

        if calisan_id == 0 or onay == -1 or not izin_turu:
            QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurunuz.")
            return

        izin_guncelle(self.conn, izin_id, calisan_id, bas_tarih, bit_tarih, izin_turu, onay)
        self.izinleri_yukle()
        self.temizle()

    def izin_sil(self):
        secili_satir = self.ui.tblzin.currentRow()
        if secili_satir < 0:
            QMessageBox.warning(None, "Uyarı", "Lütfen silmek istediğiniz bir izin satırını seçiniz.")
            return

        izin_id_item = self.ui.tblzin.item(secili_satir, 0)
        if izin_id_item is None:
            QMessageBox.warning(None, "Hata", "Seçilen satırda izin ID'si bulunamadı.")
            return

        izin_id = int(izin_id_item.text())

        cevap = QMessageBox.question(
            None,
            "İzni Sil",
            "Seçili izin kaydını silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if cevap == QMessageBox.Yes:
            izin_sil(self.conn, izin_id)
            self.izinleri_yukle()
            QMessageBox.information(None, "Başarılı", "İzin başarıyla silindi.")

    def izin_ara(self):
        departman_id = self.ui.departmanSecimi.currentData()
        calisan_id = self.ui.calisanSecimi.currentData()
        baslangic = self.ui.izinBasTarihi.date().toString("yyyy-MM-dd")
        bitis = self.ui.izinBitTarihi.date().toString("yyyy-MM-dd")
        izin_turu = self.ui.izinTuru.text().strip()
        onay_durumu = self.ui.onayDurumu.currentData()

        varsayilan_tarih = QDate(2000, 1, 1).toString("yyyy-MM-dd")
        if baslangic == varsayilan_tarih:
            baslangic = None
        if bitis == varsayilan_tarih:
            bitis = None

        if departman_id == 0:
            departman_id = None
        if onay_durumu == -1:
            onay_durumu = None

        veriler = izin_ara(
            self.conn,
            departman_id=departman_id,
            calisan_id=calisan_id,
            izin_turu=izin_turu,
            izin_baslangic=baslangic,
            izin_bitis=bitis,
            onay_durumu=onay_durumu
        )

        self.ui.tblzin.clearContents()
        self.ui.tblzin.setRowCount(0)

        for row_idx, satir in enumerate(veriler):
            self.ui.tblzin.insertRow(row_idx)
            for col_idx, deger in enumerate(satir):
                item = QTableWidgetItem(str(deger))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.ui.tblzin.setItem(row_idx, col_idx, item)

        self.ui.tblzin.setColumnHidden(0, True)
        self.ui.tblzin.setColumnHidden(6, True)
        self.ui.tblzin.setColumnHidden(7, True)
