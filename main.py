from PyQt5 import QtWidgets
from ui.ana_pencere4 import Ui_MainWindow
from view.calisanlar_view import CalisanlarView
from view.izinler_view import IzinlerView
from view.maaslar_view import MaaslarView
from view.performanslar_view import PerformanslarView


class AnaPencere(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Çalışanlar sekmesini başlat
        self.calisanlar_view = CalisanlarView(self.ui)
        self.ui.tblCalisanlar.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) #tablo üzerinden veri üzerinde değişiklik yapılamayacak

        # izinler sekmesini başlat
        self.izinler_view = IzinlerView(self.ui)
        self.ui.tblzin.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) #tablo üzerinden veri üzerinde değişiklik yapılamayacak

        self.maaslar_view = MaaslarView(self.ui)
        self.ui.tblMaas.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)  # tablo üzerinden veri üzerinde değişiklik yapılamayacak

        self.performanslar_view = PerformanslarView(self.ui)
        self.ui.tblPerf.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)  # tablo üzerinden veri üzerinde değişiklik yapılamayacak


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())
