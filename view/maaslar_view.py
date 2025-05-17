from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QTableWidgetItem
from datetime import datetime
from controller.maaslar_controller import (
    departmanlari_getir,
    calisan_bilgilerini_getir,
    maaslari_getir,
    calisanlari_getir,
    maas_ekle,
    maas_sil,
    maas_guncelle, maas_ara
)

class MaaslarView:
    def __init__(self, ui):
        self.ui = ui
        self.veritabani_baglantisi()

        self.calisan_map = {}
        self.departmanlari_yukle()
        self.calisanlari_yukle()
        self.maaslari_yukle()

        self.ui.departmanSecimi_2.currentIndexChanged.connect(self.departmanSecimi_changed)
        self.ui.maasOnay.clicked.connect(self.maas_ekle)
        self.ui.maasSil.clicked.connect(self.maas_sil)
        self.ui.maasGuncelle.clicked.connect(self.maas_guncelle)
        self.ui.maasTemizle.clicked.connect(self.formu_temizle)
        self.ui.maasAra.clicked.connect(self.maas_ara)
        self.ui.tblMaas.itemSelectionChanged.connect(self.formu_doldur)

    def veritabani_baglantisi(self):
        from db.database import connect
        self.conn = connect()

    def departmanlari_yukle(self):
        self.ui.departmanSecimi_2.clear()
        self.ui.departmanSecimi_2.addItem("Tüm Departmanlar", 0)
        for id_, ad in departmanlari_getir(self.conn):
            self.ui.departmanSecimi_2.addItem(ad, id_)

    def departmanSecimi_changed(self):
        departman_id = self.ui.departmanSecimi_2.currentData()
        if departman_id == 0:
            self.ui.calisanSecimi_Maas.clear()
            self.ui.calisanSecimi_Maas.addItem("Önce departman seçin", 0)
            return

        self.calisanlari_yukle(departman_id)
        self.ui.calisanSecimi_Maas.setCurrentIndex(0)
        self.ui.maasAy.setDate(QDate.currentDate())
        self.ui.netMaas.setText("0.0")
        self.ui.brutMaas.setText("0.0")
        self.ui.kesintiMaas.setText("0.0")
        self.ui.maasPrim.setText("0.0")

    def calisanlari_yukle(self, departman_id=0):
        self.ui.calisanSecimi_Maas.clear()

        if departman_id == 0:
            self.ui.calisanSecimi_Maas.addItem("Önce departman seçin", 0)
            return

        calisanlar = calisanlari_getir(self.conn, departman_id)
        self.ui.calisanSecimi_Maas.addItem("Seçiniz", 0)
        for calisan_id, ad, soyad in calisanlar:
            self.ui.calisanSecimi_Maas.addItem(f"{ad} {soyad}", calisan_id)

    def maaslari_yukle(self):
        veriler = maaslari_getir(self.conn)

        self.ui.tblMaas.setColumnCount(7)
        self.ui.tblMaas.setHorizontalHeaderLabels([
            "ID", "Çalışan", "Tarih", "Brüt Maaş", "Kesinti", "Prim", "Net Maaş"
        ])
        self.ui.tblMaas.setRowCount(0)

        for row_index, row_data in enumerate(veriler):
            self.ui.tblMaas.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                if col_index == 2 and data:
                    try:
                        tarih = datetime.strptime(data, "%Y-%m-%d")
                        data = tarih.strftime("%Y-%m")
                    except ValueError:
                        pass
                self.ui.tblMaas.setItem(
                    row_index, col_index, QTableWidgetItem(str(data))
                )

        self.ui.tblMaas.setColumnHidden(0, True)

    def maas_ekle(self):
        try:
            calisan_id = self.ui.calisanSecimi_Maas.currentData()
            tarih = self.ui.maasAy.date().toString("yyyy-MM-dd")
            brut_maas = float(self.ui.brutMaas.text())
            kesinti = float(self.ui.kesintiMaas.text())
            prim = float(self.ui.maasPrim.text())
            net_maas = float(self.ui.netMaas.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Hata", "Tüm maaş alanlarına geçerli sayılar giriniz.")
            return

        if calisan_id is None or not tarih:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        maas_ekle(self.conn, calisan_id, tarih, net_maas, brut_maas, kesinti, prim)
        self.maaslari_yukle()
        self.formu_temizle()

    def maas_sil(self):
        secili_satir = self.ui.tblMaas.currentRow()
        if secili_satir < 0:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Lütfen silmek için bir maaş seçin.")
            return

        maas_id = int(self.ui.tblMaas.item(secili_satir, 0).text())
        cevap = QtWidgets.QMessageBox.question(None, "Silme Onayı", "Maaşı silmek istiyor musunuz?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if cevap == QtWidgets.QMessageBox.Yes:
            maas_sil(self.conn, maas_id)
            self.maaslari_yukle()
            self.formu_temizle()

    def maas_guncelle(self):
        secili_satir = self.ui.tblMaas.currentRow()
        if secili_satir < 0:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Lütfen güncellemek için bir maaş seçin.")
            return

        maas_id = int(self.ui.tblMaas.item(secili_satir, 0).text())
        calisan_id = self.ui.calisanSecimi_Maas.currentData()
        ay = self.ui.maasAy.date().toString("yyyy-MM-dd")
        try:
            net_maas = float(self.ui.netMaas.text())
            brut_maas = float(self.ui.brutMaas.text())
            kesinti = float(self.ui.kesintiMaas.text())
            prim = float(self.ui.maasPrim.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(None, "Hata", "Geçersiz maaş bilgileri.")
            return

        if calisan_id is None or not ay:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        maas_guncelle(self.conn, maas_id, calisan_id, ay, net_maas, brut_maas, kesinti, prim)
        self.maaslari_yukle()
        self.formu_temizle()

    def formu_doldur(self):
        secili = self.ui.tblMaas.currentRow()
        if secili < 0:
            return

        calisan_adi = self.ui.tblMaas.item(secili, 1).text()
        tarih = self.ui.tblMaas.item(secili, 2).text()
        brut_maas = float(self.ui.tblMaas.item(secili, 3).text())
        kesinti = float(self.ui.tblMaas.item(secili, 4).text())
        prim = float(self.ui.tblMaas.item(secili, 5).text())
        net_maas = float(self.ui.tblMaas.item(secili, 6).text())

        calisan_bilgisi = calisan_bilgilerini_getir(self.conn, calisan_adi)
        if calisan_bilgisi:
            departman_adi, calisan_id = calisan_bilgisi

            index = self.ui.departmanSecimi_2.findText(departman_adi)
            if index >= 0:
                self.ui.departmanSecimi_2.setCurrentIndex(index)

            index_c = self.ui.calisanSecimi_Maas.findData(calisan_id)
            if index_c >= 0:
                self.ui.calisanSecimi_Maas.setCurrentIndex(index_c)

        self.ui.maasAy.setDate(QDate.fromString(tarih, "yyyy-MM"))
        self.ui.brutMaas.setText(str(brut_maas))
        self.ui.kesintiMaas.setText(str(kesinti))
        self.ui.maasPrim.setText(str(prim))
        self.ui.netMaas.setText(str(net_maas))

    def formu_temizle(self):
        self.ui.departmanSecimi_2.setCurrentIndex(0)
        self.ui.calisanSecimi_Maas.setCurrentIndex(0)
        self.ui.maasAy.setDate(QDate.currentDate())
        self.ui.netMaas.setText("0.0")
        self.ui.brutMaas.setText("0.0")
        self.ui.kesintiMaas.setText("0.0")
        self.ui.maasPrim.setText("0.0")
        self.ui.tblMaas.clearSelection()
        self.maaslari_yukle()

    def maas_ara(self):
        departman_id = self.ui.departmanSecimi.currentData()
        calisan_id = self.ui.calisanSecimi.currentData()
        ay = self.ui.maasAy.date().toString("yyyy-MM")

        if ay == "2000-01":
            ay = None
        if departman_id == 0:
            departman_id = None
        if calisan_id == 0:
            calisan_id = None

        veriler = maas_ara(
            self.conn,
            departman_id=departman_id,
            calisan_id=calisan_id,
            ay=ay
        )

        self.ui.tblMaas.clearContents()
        self.ui.tblMaas.setRowCount(0)
        self.ui.tblMaas.setColumnCount(7)
        self.ui.tblMaas.setHorizontalHeaderLabels([
            "Çalışan", "Departman", "Ay", "Brüt Maaş", "Kesinti", "Prim", "Net Maaş"
        ])

        self.ui.tblMaas.setColumnHidden(0, False)

        for row_idx, satir in enumerate(veriler):
            print("Satır verisi:", satir)
            self.ui.tblMaas.insertRow(row_idx)

            kolon_veriler = [
                satir[0],  # Çalışan adı
                satir[1],  # Departman
                satir[2],  # Ay
                satir[3],  # Brüt maaş
                satir[4],  # Kesinti
                satir[5],  # Prim
                satir[6],  # Net maaş
            ]

            for col_idx, deger in enumerate(kolon_veriler):
                item = QTableWidgetItem(str(deger))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.ui.tblMaas.setItem(row_idx, col_idx, item)

