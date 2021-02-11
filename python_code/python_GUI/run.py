import sys 
import os
import time
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QMainWindow, QWidget
from PyQt5.QtCore import QCoreApplication, Qt


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setGeometry(500, 300, 400, 200)
        self.setWindowTitle("Course Selection")
        horizontalLayout = QHBoxLayout()
        self.button1 = QPushButton("ProCon",self)
        self.button1.setFixedSize(100,100)
        self.button1.clicked.connect(self.proconPress)
        self.button2 = QPushButton("Drones",self)
        self.button2.setFixedSize(100,100)
        self.button2.clicked.connect(self.dronesPress)
        horizontalLayout.addWidget(self.button1)
        horizontalLayout.addWidget(self.button2)
        widget = QWidget()
        widget.setLayout(horizontalLayout)
        self.setCentralWidget(widget)


    def proconPress(self):
        from procon import Window
        
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        self.final = Window()
        self.final.show()
        self.showMinimized()
        self.button1.clicked.disconnect(self.proconPress)
        self.button2.clicked.connect(self.dronesPress)

    def dronesPress(self):
        from drones import Window

        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        self.final = Window()
        self.final.show()
        self.showMinimized()
        self.button2.clicked.disconnect(self.dronesPress)
        self.button1.clicked.connect(self.proconPress)



def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

