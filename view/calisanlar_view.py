from PyQt5 import QtWidgets, QtCore  # QtCore eklendi
from controller.calisanlar_controller import calisanlari_getir, departmanlari_getir

class CalisanlarView:
    def __init__(self, ui):
        self.ui = ui
        self.departmanlar_map = {}

        self.veritabani_baglantisi()
        self.departmanlari_yukle()
        self.calisanlari_yukle()

        self.ui.calisanEkle.clicked.connect(self.calisan_ekle)
        self.ui.calisanSil.clicked.connect(self.calisan_sil)
        self.ui.calisanGuncelle.clicked.connect(self.calisan_guncelle)
        self.ui.calisanAra.clicked.connect(self.ara_calisan)
        self.ui.calisanTemizle.clicked.connect(self.formu_temizle)

        self.ui.tblCalisanlar.itemSelectionChanged.connect(self.formu_doldur)

        # Otomatik filtreleme sinyalleri
        self.ui.calisanAd.textChanged.connect(self.ara_calisan)
        self.ui.calisanSoyadi.textChanged.connect(self.ara_calisan)
        self.ui.calisanPozisyon.textChanged.connect(self.ara_calisan)
        self.ui.calisanGirisTarihi.dateChanged.connect(self.ara_calisan)
        self.ui.calisanDepartman.currentIndexChanged.connect(self.ara_calisan)

    def veritabani_baglantisi(self):
        from db.database import connect
        self.conn = connect()

    def calisanlari_yukle(self):
        veriler = calisanlari_getir(self.conn)
        self.ui.tblCalisanlar.setRowCount(0)
        for row_index, row_data in enumerate(veriler):
            self.ui.tblCalisanlar.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.tblCalisanlar.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(data)))
            self.ui.tblCalisanlar.setRowHidden(row_index, False)  # ⭐ Satırı görünür hale getir
        self.ui.tblCalisanlar.setColumnHidden(0, True)

    def departmanlari_yukle(self):
        departmanlar = departmanlari_getir(self.conn)
        self.ui.calisanDepartman.clear()

        self.ui.calisanDepartman.addItem("Seçiniz", None)

        for id_, ad in departmanlar:
            self.ui.calisanDepartman.addItem(ad, id_)
            self.departmanlar_map[ad] = id_

    def calisan_ekle(self):
        ad = self.ui.calisanAd.text().strip()
        soyad = self.ui.calisanSoyadi.text().strip()
        pozisyon = self.ui.calisanPozisyon.text().strip()
        giris_tarihi = self.ui.calisanGirisTarihi.date().toString("yyyy-MM-dd")
        departman_id = self.ui.calisanDepartman.currentData()

        # ✅ Form doğrulama
        if not ad or not soyad or not pozisyon or departman_id is None:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        from controller.calisanlar_controller import calisan_ekle
        calisan_ekle(self.conn, ad, soyad, pozisyon, giris_tarihi, departman_id)

        self.calisanlari_yukle()
        self.formu_temizle()

    def formu_doldur(self):
        secili_satir = self.ui.tblCalisanlar.currentRow()
        if secili_satir < 0:
            return

        ad_item = self.ui.tblCalisanlar.item(secili_satir, 1)
        soyad_item = self.ui.tblCalisanlar.item(secili_satir, 2)
        pozisyon_item = self.ui.tblCalisanlar.item(secili_satir, 3)
        giris_item = self.ui.tblCalisanlar.item(secili_satir, 4)
        departman_item = self.ui.tblCalisanlar.item(secili_satir, 5)

        ad = ad_item.text() if ad_item else ""
        soyad = soyad_item.text() if soyad_item else ""
        pozisyon = pozisyon_item.text() if pozisyon_item else ""
        giris = giris_item.text() if giris_item else ""
        departman_adi = departman_item.text() if departman_item else ""

        self.ui.calisanAd.setText(ad)
        self.ui.calisanSoyadi.setText(soyad)
        self.ui.calisanPozisyon.setText(pozisyon)

        from PyQt5.QtCore import QDate
        tarih = QDate.fromString(giris, "yyyy-MM-dd")
        if tarih.isValid():
            self.ui.calisanGirisTarihi.setDate(tarih)

        index = self.ui.calisanDepartman.findText(departman_adi)
        if index >= 0:
            self.ui.calisanDepartman.setCurrentIndex(index)

    def formu_temizle(self):
        self.ui.calisanAd.clear()
        self.ui.calisanSoyadi.clear()
        self.ui.calisanPozisyon.clear()
        self.ui.calisanGirisTarihi.setSpecialValueText("Tarih Seçilmedi")
        self.ui.calisanGirisTarihi.setDate(QtCore.QDate(2000, 1, 1))
        self.ui.calisanDepartman.setCurrentIndex(0)
        self.calisanlari_yukle()

    def calisan_sil(self):
        secili_satir = self.ui.tblCalisanlar.currentRow()
        if secili_satir < 0:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Lütfen silmek için bir çalışan seçin.")
            return

        # Tablodan hücreleri alırken None kontrolü
        id_item = self.ui.tblCalisanlar.item(secili_satir, 0)
        if id_item is None:
            QtWidgets.QMessageBox.critical(None, "Hata", "Seçilen satırda ID bilgisi bulunamadı.")
            return

        try:
            calisan_id = int(id_item.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Hata", "Geçersiz ID.")
            return

        ad_item = self.ui.tblCalisanlar.item(secili_satir, 1)
        soyad_item = self.ui.tblCalisanlar.item(secili_satir, 2)

        ad = ad_item.text().strip() if ad_item else ""
        soyad = soyad_item.text().strip() if soyad_item else ""

        if not ad or not soyad:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Boş bir çalışan kaydı silinemez.")
            return

        cevap = QtWidgets.QMessageBox.question(
            None, "Silme Onayı",
            f"{ad} {soyad} adlı çalışanı silmek istiyor musunuz?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if cevap == QtWidgets.QMessageBox.Yes:
            from controller.calisanlar_controller import calisan_sil
            calisan_sil(self.conn, calisan_id)
            self.calisanlari_yukle()
            self.formu_temizle()

    def calisan_guncelle(self):
        secili_satir = self.ui.tblCalisanlar.currentRow()
        if secili_satir < 0:
            QtWidgets.QMessageBox.warning(None, "Uyarı", "Lütfen güncellemek için bir çalışan seçin.")
            return

        id_item = self.ui.tblCalisanlar.item(secili_satir, 0)
        if id_item is None:
            QtWidgets.QMessageBox.critical(None, "Hata", "Seçilen satırda ID bilgisi bulunamadı.")
            return

        try:
            calisan_id = int(id_item.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(None, "Hata", "Geçersiz ID.")
            return

        ad = self.ui.calisanAd.text().strip()
        soyad = self.ui.calisanSoyadi.text().strip()
        pozisyon = self.ui.calisanPozisyon.text().strip()
        giris_tarihi = self.ui.calisanGirisTarihi.date().toString("yyyy-MM-dd")
        departman_id = self.ui.calisanDepartman.currentData()

        if not ad or not soyad or not pozisyon or departman_id is None:
            QtWidgets.QMessageBox.warning(None, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        from controller.calisanlar_controller import calisan_guncelle
        calisan_guncelle(self.conn, calisan_id, ad, soyad, pozisyon, giris_tarihi, departman_id)

        self.calisanlari_yukle()
        self.formu_temizle()
        QtWidgets.QMessageBox.information(None, "Başarılı", "Çalışan bilgisi güncellendi.")

    def ara_calisan(self):
        ad = self.ui.calisanAd.text().strip().lower()
        soyad = self.ui.calisanSoyadi.text().strip().lower()
        pozisyon = self.ui.calisanPozisyon.text().strip().lower()
        giris_tarihi = self.ui.calisanGirisTarihi.date().toString("yyyy-MM-dd")
        departman_adi = self.ui.calisanDepartman.currentText().strip().lower()

        # Eğer tüm filtreler boşsa tabloyu sıfırdan yükle
        if not ad and not soyad and not pozisyon and departman_adi in ["", "seçiniz"] and not giris_tarihi:
            self.calisanlari_yukle()
            return

        if giris_tarihi == "2000-01-01":
            giris_tarihi = ""  # Arama filtresine dahil etme

        for satir in range(self.ui.tblCalisanlar.rowCount()):
            ad_item = self.ui.tblCalisanlar.item(satir, 1)
            soyad_item = self.ui.tblCalisanlar.item(satir, 2)
            pozisyon_item = self.ui.tblCalisanlar.item(satir, 3)
            giris_item = self.ui.tblCalisanlar.item(satir, 4)
            departman_item = self.ui.tblCalisanlar.item(satir, 5)

            # Satırdaki metinleri kontrol et
            satir_ad = ad_item.text().strip().lower() if ad_item else ""
            satir_soyad = soyad_item.text().strip().lower() if soyad_item else ""
            satir_pozisyon = pozisyon_item.text().strip().lower() if pozisyon_item else ""
            satir_giris = giris_item.text().strip() if giris_item else ""
            satir_departman = departman_item.text().strip().lower() if departman_item else ""

            # Tüm eşleşme kriterleri
            goster = True
            if ad and ad not in satir_ad:
                goster = False
            if soyad and soyad not in satir_soyad:
                goster = False
            if pozisyon and pozisyon not in satir_pozisyon:
                goster = False
            if giris_tarihi and giris_tarihi != satir_giris:
                goster = False
            if departman_adi and departman_adi != "seçiniz" and departman_adi not in satir_departman:
                goster = False

            self.ui.tblCalisanlar.setRowHidden(satir, not goster)


