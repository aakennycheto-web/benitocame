import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel

class Ventana(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Nivel 1 - Saludo")
        self.setGeometry(200, 200, 350, 200)

        # Texto
        self.etiqueta = QLabel("Haz clic para saludar", self)
        self.etiqueta.move(100, 50)

        # Botón
        self.boton = QPushButton("Saludar", self)
        self.boton.move(130, 100)

        # Evento: cuando dan clic
        self.boton.clicked.connect(self.saludar)

    def saludar(self):
        self.etiqueta.setText("¡Hola! 👋")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec_())