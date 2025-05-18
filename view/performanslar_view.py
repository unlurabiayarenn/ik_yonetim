from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QTableWidgetItem
from controller.performanslar_controller import (
    performansları_getir, departmanlari_getir, calisanlari_getir, performans_ekle as kaydet, performans_sil,
    performans_guncelle as guncelle, performans_ara as ara
)

class PerformanslarView:
    def __init__(self, ui):
        self.ui = ui
        self.veritabani_baglantisi()

        self.calisan_map = {}
        self.performansları_yukle()
        self.departmanlari_yukle()

        self.ui.departmanSecimi_3.currentIndexChanged.connect(self.departmanSecimi_changed)
        self.ui.tblPerf.cellDoubleClicked.connect(self.formu_doldur)
        self.ui.yorumEkle.clicked.connect(self.performans_ekle)
        self.ui.yorumSil.clicked.connect(self.performans_sil)
        self.ui.yorumGuncelle.clicked.connect(self.performans_guncelle)
        self.ui.perfAra.clicked.connect(self.performans_ara)

        self.departmanlari_yukle()
        self.calisanlari_yukle(0)

    def veritabani_baglantisi(self):
        from db.database import connect
        self.conn = connect()

    def performansları_yukle(self):
        veriler = performansları_getir(self.conn)

        self.ui.tblPerf.setColumnCount(7)
        self.ui.tblPerf.setHorizontalHeaderLabels([
            "ID", "Çalışan", "Tarih", "Puan", "Yorum", "Departman ID", "Çalışan ID"
        ])
        self.ui.tblPerf.setRowCount(0)

        for row_idx, row_data in enumerate(veriler):
            self.ui.tblPerf.insertRow(row_idx)
            for col_idx, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.ui.tblPerf.setItem(row_idx, col_idx, item)

        # Gizli sütunlar
        self.ui.tblPerf.setColumnHidden(0, True)  # ID
        self.ui.tblPerf.setColumnHidden(5, True)  # Departman ID
        self.ui.tblPerf.setColumnHidden(6, True)  # Çalışan ID

    def departmanlari_yukle(self):
        self.ui.departmanSecimi_3.clear()
        self.ui.departmanSecimi_3.addItem("Tüm Departmanlar", 0)
        for id_, ad in departmanlari_getir(self.conn):
            self.ui.departmanSecimi_3.addItem(ad, id_)

    def departmanSecimi_changed(self):
        departman_id = self.ui.departmanSecimi_3.currentData()
        if departman_id == 0:
            self.ui.calisanSecimi_perf.clear()
            self.ui.calisanSecimi_perf.addItem("Önce departman seçin", 0)
            return

        self.calisanlari_yukle(departman_id)
        self.ui.calisanSecimi_perf.setCurrentIndex(0)
        self.ui.perfTarih.clear()
        self.ui.puanPerf.setValue(0)
        self.ui.yorum_perf.clear()

    def calisanlari_yukle(self, departman_id=0):
        self.ui.calisanSecimi_perf.clear()

        if departman_id == 0:
            self.ui.calisanSecimi_perf.addItem("Önce departman seçin", 0)
            return

        calisanlar = calisanlari_getir(self.conn, departman_id)
        self.ui.calisanSecimi_perf.addItem("Seçiniz", 0)
        for calisan_id, ad, soyad in calisanlar:
            self.ui.calisanSecimi_perf.addItem(f"{ad} {soyad}", calisan_id)

    def formu_doldur(self, row, column):
        # Verileri tabloda satırdan oku
        tarih_item = self.ui.tblPerf.item(row, 2)
        puan_item = self.ui.tblPerf.item(row, 3)
        yorum_item = self.ui.tblPerf.item(row, 4)
        departman_id_item = self.ui.tblPerf.item(row, 5)
        calisan_id_item = self.ui.tblPerf.item(row, 6)

        if None in (tarih_item, puan_item, yorum_item, departman_id_item, calisan_id_item):
            return

        perf_tarih = tarih_item.text()
        perf_puan = puan_item.text()
        perf_yorum = yorum_item.text()
        departman_id = int(departman_id_item.text())
        calisan_id = int(calisan_id_item.text())

        # Combobox'ları güncelle
        self.ui.departmanSecimi_3.setCurrentIndex(
            self.ui.departmanSecimi_3.findData(departman_id)
        )
        self.calisanlari_yukle(departman_id)
        self.ui.calisanSecimi_perf.setCurrentIndex(
            self.ui.calisanSecimi_perf.findData(calisan_id)
        )

        # Diğer alanları doldur
        self.ui.yorum_perf.setText(perf_yorum)
        try:
            self.ui.perfTarih.setDate(QDate.fromString(perf_tarih, "yyyy-MM"))
        except:
            pass
        self.ui.puanPerf.setValue(int(perf_puan))

    def performans_ekle(self):
        try:
            calisan_id = self.ui.calisanSecimi_perf.currentData()
            tarih = self.ui.perfTarih.date().toString("yyyy-MM")
            puan = int(self.ui.puanPerf.text())
            yorum = self.ui.yorum_perf.toPlainText()

        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Hata", "Tüm maaş alanlarına geçerli sayılar giriniz.")
            return

        if calisan_id is None or not tarih:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        kaydet(self.conn, calisan_id, tarih, puan, yorum)
        self.performansları_yukle()
        self.formu_temizle()

    def performans_sil(self):
        secili_satir = self.ui.tblPerf.currentRow()
        if secili_satir < 0:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Lütfen silmek için bir maaş seçin.")
            return

        perf_id = int(self.ui.tblPerf.item(secili_satir, 0).text())
        cevap = QtWidgets.QMessageBox.question(None, "Silme Onayı", "Maaşı silmek istiyor musunuz?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if cevap == QtWidgets.QMessageBox.Yes:
            performans_sil(self.conn, perf_id)
            self.performansları_yukle()
            self.formu_temizle()

    def performans_guncelle(self):
        secili_satir = self.ui.tblPerf.currentRow()
        if secili_satir < 0:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Lütfen güncellemek için bir maaş seçin.")
            return

        perf_id = int(self.ui.tblPerf.item(secili_satir, 0).text())
        calisan_id = self.ui.calisanSecimi_perf.currentData()
        degerlendirme_tarihi = self.ui.perfTarih.date().toString("yyyy-MM")
        puan = int(self.ui.puanPerf.text())
        yorum = self.ui.yorum_perf.toPlainText()

        if calisan_id is None or not degerlendirme_tarihi:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        guncelle(self.conn, perf_id, calisan_id, degerlendirme_tarihi, puan, yorum)
        self.performansları_yukle()
        self.formu_temizle()

    def performans_ara(self):
        departman_id = self.ui.departmanSecimi_3.currentData()
        calisan_id = self.ui.calisanSecimi_perf.currentData()
        tarih = self.ui.perfTarih.date().toString("yyyy-MM")
        puan = self.ui.puanPerf.value()

        if tarih == "2000-01":
            tarih = None
        if departman_id == 0:
            departman_id = None
        if calisan_id == 0:
            calisan_id = None
        if puan == 0:
            puan = None

        veriler = ara(
            self.conn,
            departman_id=departman_id,
            calisan_id=calisan_id,
            degerlendirme_tarihi=tarih,
            puan=puan
        )

        print("Gelen tüm veriler:")
        for v in veriler:
            print(v)

        self.ui.tblPerf.clearContents()
        self.ui.tblPerf.setRowCount(0)
        self.ui.tblPerf.setColumnCount(4)
        self.ui.tblPerf.setHorizontalHeaderLabels(["Çalışan", "Tarih", "Puan", "Yorum"])

        for row_idx, satir in enumerate(veriler):
            print(f"Satır {row_idx} verileri: {satir}")

            self.ui.tblPerf.insertRow(row_idx)

            # Çalışan
            calisan_item = QTableWidgetItem(str(satir[0]))
            calisan_item.setFlags(calisan_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tblPerf.setItem(row_idx, 0, calisan_item)
            print(f"Çalışan: {satir[0]}")

            # Tarih
            tarih_item = QTableWidgetItem(str(satir[2]))
            tarih_item.setFlags(tarih_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tblPerf.setItem(row_idx, 1, tarih_item)

            # Puan
            puan_item = QTableWidgetItem(str(satir[3]))
            puan_item.setFlags(puan_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tblPerf.setItem(row_idx, 2, puan_item)

            # Yorum
            yorum_item = QTableWidgetItem(str(satir[4]))
            yorum_item.setFlags(yorum_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.ui.tblPerf.setItem(row_idx, 3, yorum_item)

        self.ui.tblPerf.resizeColumnsToContents()
        self.ui.tblPerf.showColumn(0)

    def formu_temizle(self):
        self.ui.departmanSecimi_3.setCurrentIndex(0)
        self.ui.calisanSecimi_perf.setCurrentIndex(0)
        self.ui.perfTarih.setDate(QDate.currentDate())
        self.ui.puanPerf.clear()
        self.ui.yorum_perf.clear()
        self.ui.tblMaas.clearSelection()
        self.performansları_yukle()

