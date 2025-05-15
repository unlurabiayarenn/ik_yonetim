from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMessageBox
from controller.izinler_controller import (
    izinleri_getir,
    departmanlari_getir,
    calisanlari_getir,
    izin_ekle,
    izin_guncelle
)
from db.database import connect

class IzinlerView:
    def __init__(self, ui):
        self.ui = ui
        self.conn = connect()

        self.ui.onayDurumu.clear()
        self.ui.onayDurumu.addItem("Seçiniz", -1)
        self.ui.onayDurumu.addItem("Onaylandı", 1)
        self.ui.onayDurumu.addItem("Reddedildi", 0)

        self.departmanlari_yukle()
        self.calisanlari_yukle()
        self.izinleri_yukle()

        self.departman_id_list = []

        # Sinyaller
        self.ui.tblzin.itemSelectionChanged.connect(self.formu_doldur)
        self.ui.tblzin.cellDoubleClicked.connect(self.formu_doldur)
        self.ui.departmanSecimi.currentIndexChanged.connect(self.departman_degisti)
        self.ui.izinOnay.clicked.connect(self.kaydet)
        self.ui.izinGuncelle.clicked.connect(self.guncelle)
        self.ui.alanTemizle.clicked.connect(self.temizle)

    def departmanlari_yukle(self):
        self.ui.departmanSecimi.clear()
        self.ui.departmanSecimi.addItem("Tüm Departmanlar", 0)
        for id_, ad in departmanlari_getir(self.conn):
            self.ui.departmanSecimi.addItem(ad, id_)

    def calisanlari_yukle(self, departman_id=0):
        self.ui.calisanSecimi.clear()
        self.ui.calisanSecimi.addItem("Seçiniz", -1)
        for id_, ad, soyad in calisanlari_getir(self.conn, departman_id):
            self.ui.calisanSecimi.addItem(f"{ad} {soyad}", id_)

    def izinleri_yukle(self):
        veriler = izinleri_getir(self.conn)
        self.ui.tblzin.setRowCount(0)
        self.departman_id_list = []

        for row_index, row_data in enumerate(veriler):
            self.ui.tblzin.insertRow(row_index)
            self.departman_id_list.append(row_data[-1])  # departman_id

            for col_index, data in enumerate(row_data[:-1]):
                item = QtWidgets.QTableWidgetItem(str(data))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.ui.tblzin.setItem(row_index, col_index, item)

            self.ui.tblzin.setRowHidden(row_index, False)
        self.ui.tblzin.setColumnHidden(0, True)

    def formu_doldur(self, item=None):
        if item is None:
            selected_items = self.ui.tblzin.selectedItems()
            if not selected_items:
                return
            row = selected_items[0].row()
        else:
            row = item.row()

        if row < 0 or row >= self.ui.tblzin.rowCount():
            return

        # departman_id al
        departman_id = self.departman_id_list[row] if 0 <= row < len(self.departman_id_list) else 0

        # Departman combobox'ı güncelle
        index = self.ui.departmanSecimi.findData(departman_id)
        self.ui.departmanSecimi.setCurrentIndex(index if index >= 0 else 0)

        # Çalışanları yükle
        self.calisanlari_yukle(departman_id)

        # Diğer alanları doldur
        calisan = self.ui.tblzin.item(row, 1).text()
        izinBasTarihi = self.ui.tblzin.item(row, 2).text()
        izinBitTarihi = self.ui.tblzin.item(row, 3).text()
        izinTuru = self.ui.tblzin.item(row, 4).text()
        onayDurumu = self.ui.tblzin.item(row, 5).text()

        self.ui.izinTuru.setText(izinTuru)
        self.ui.izinBasTarihi.setDate(QDate.fromString(izinBasTarihi, "yyyy-MM-dd"))
        self.ui.izinBitTarihi.setDate(QDate.fromString(izinBitTarihi, "yyyy-MM-dd"))
        self.ui.onayDurumu.setCurrentIndex(self.ui.onayDurumu.findText(onayDurumu))
        self.ui.calisanSecimi.setCurrentIndex(self.ui.calisanSecimi.findText(calisan))

    def departman_degisti(self):
        secilen_departman_id = self.ui.departmanSecimi.currentData()
        self.calisanlari_yukle(secilen_departman_id)
        self.temizle()

    def temizle(self):
        self.ui.departmanSecimi.setCurrentIndex(0)
        self.ui.calisanSecimi.setCurrentIndex(0)
        self.ui.onayDurumu.setCurrentIndex(0)
        self.ui.izinTuru.clear()
        self.ui.izinBasTarihi.setDate(QDate.currentDate())
        self.ui.izinBitTarihi.setDate(QDate.currentDate())
        self.ui.tblzin.clearSelection()

    def kaydet(self):
        calisan_id = self.ui.calisanSecimi.currentData()
        onay = self.ui.onayDurumu.currentData()
        izin_turu = self.ui.izinTuru.text()
        bas_tarih = self.ui.izinBasTarihi.date().toString("yyyy-MM-dd")
        bit_tarih = self.ui.izinBitTarihi.date().toString("yyyy-MM-dd")

        if calisan_id == -1 or onay == -1 or not izin_turu:
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

        if calisan_id == -1 or onay == -1 or not izin_turu:
            QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurunuz.")
            return

        izin_guncelle(self.conn, izin_id, calisan_id, bas_tarih, bit_tarih, izin_turu, onay)
        self.izinleri_yukle()
        self.temizle()
