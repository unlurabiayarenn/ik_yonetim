from PyQt5 import QtWidgets
from ui.ana_pencere import Ui_MainWindow
from view.calisanlar_view import CalisanlarView

class AnaPencere(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Çalışanlar sekmesini başlat
        self.calisanlar_view = CalisanlarView(self.ui)
        self.ui.tblCalisanlar.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) #tablo üzerinden veri üzerinde değişiklik yapılamayacak


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())
