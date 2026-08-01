import sys
import os
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QFrame, QMessageBox, QApplication, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QPainter, QPainterPath, QBrush, QColor


class EllipseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1325, 1007)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(QColor(18, 159, 73, 100)))
        painter.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.drawPath(path)


class RegisterWindow(QWidget):

    back_to_login_clicked = pyqtSignal()
    registration_complete = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(1280, 800)
        self.load_fonts()
        self.init_ui()
        self.setup_connections()

    def load_fonts(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        kantumruy_path = os.path.join(base_dir, "templates", "font", "Kantumruy-Regular.ttf")
        kameron_path = os.path.join(base_dir, "templates", "font", "Kameron-Regular.ttf")
        font_paths = {
            "Kantumruy": kantumruy_path,
            "Kameron": kameron_path
        }

        self.fonts_loaded = {}
        for font_name, font_path in font_paths.items():
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.fonts_loaded[font_name] = families[0]
            else:
                print(f"Файл шрифта не найден: {font_path}")

    def init_ui(self):
        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, 1280, 800)
        main_frame.setStyleSheet("background-color: rgba(189, 241, 202, 1);")

        # Эллипс
        ellipse = EllipseWidget(self)
        ellipse.move(293, -89)

        # Заголовок
        title_label = QLabel("Зарегистрироваться", self)
        title_label.setGeometry(450, 56, 868, 76)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            title_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            title_font.setFamily("Arial")

        title_font.setPointSize(45)
        title_font.setWeight(400)
        title_label.setFont(title_font)

        title_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 1);
                background-color: transparent;
                letter-spacing: 2px;
            }
        """)

        # Ввод приватного ключа
        private_key_label = QLabel("Введите приватный ключ:", self)
        private_key_label.setGeometry(470, 200, 533, 61)

        private_key_label_font = QFont()
        if "Kameron" in self.fonts_loaded:
            private_key_label_font.setFamily(self.fonts_loaded["Kameron"])
        else:
            private_key_label_font.setFamily("Georgia")

        private_key_label_font.setPointSize(25)
        private_key_label.setFont(private_key_label_font)

        private_key_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 1);
                background-color: transparent;
            }
        """)

        self.private_key_input = QLineEdit(self)
        self.private_key_input.setGeometry(522, 281, 738, 61)
        self.private_key_input.setPlaceholderText("Введите приватный ключ")

        private_key_input_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            private_key_input_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            private_key_input_font.setFamily("Arial")

        private_key_input_font.setPointSize(15)
        private_key_input_font.setWeight(400)
        self.private_key_input.setFont(private_key_input_font)

        self.private_key_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 252, 252, 1);
                border: none;
                border-radius: 0px;
                padding: 0px 20px;
                color: rgba(0, 0, 0, 1);
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
            }
        """)

        # Выбор роли
        role_label = QLabel("Выберите роль:", self)
        role_label.setGeometry(470, 392, 482, 61)

        role_label_font = QFont()
        if "Kameron" in self.fonts_loaded:
            role_label_font.setFamily(self.fonts_loaded["Kameron"])
        else:
            role_label_font.setFamily("Georgia")

        role_label_font.setPointSize(25)
        role_label.setFont(role_label_font)

        role_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 1);
                background-color: transparent;
            }
        """)

        self.role_combo = QComboBox(self)
        self.role_combo.setGeometry(834, 392, 426, 61)

        combo_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            combo_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            combo_font.setFamily("Arial")

        combo_font.setPointSize(15)
        combo_font.setWeight(400)
        self.role_combo.setFont(combo_font)

        self.role_combo.addItem("Выберите роль")
        self.role_combo.addItem("Страховщик")
        self.role_combo.addItem("Страхователь")

        self.role_combo.model().item(0).setEnabled(False)

        self.role_combo.setCurrentIndex(0)

        self.role_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 252, 252, 1);
                border: none;
                border-radius: 0px;
                padding: 0px 20px;
                color: rgba(0, 0, 0, 1);
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 10px solid rgba(0, 0, 0, 1);
                width: 0;
                height: 0;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: rgba(189, 241, 202, 1);
                color: rgba(0, 0, 0, 1);
                font-size: 25px;
                padding: 10px;
            }
        """)

        # Ввод пароля
        password_label = QLabel("Придумайте пароль :", self)
        password_label.setGeometry(470, 494, 482, 61)

        password_label_font = QFont()
        if "Kameron" in self.fonts_loaded:
            password_label_font.setFamily(self.fonts_loaded["Kameron"])
        else:
            password_label_font.setFamily("Georgia")

        password_label_font.setPointSize(25)
        password_label.setFont(password_label_font)

        password_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 1);
                background-color: transparent;
            }
        """)

        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(522, 575, 738, 61)
        self.password_input.setPlaceholderText("Придумайте пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        password_input_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            password_input_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            password_input_font.setFamily("Arial")

        password_input_font.setPointSize(15)
        password_input_font.setWeight(400)
        self.password_input.setFont(password_input_font)

        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 252, 252, 1);
                border: none;
                border-radius: 0px;
                padding: 0px 20px;
                color: rgba(0, 0, 0, 1);
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
            }
        """)

        # Кнопка "Зарегистрироваться"
        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.setGeometry(680, 690, 400, 60)

        button_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            button_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            button_font.setFamily("Arial")

        button_font.setPointSize(25)
        button_font.setWeight(400)
        self.register_button.setFont(button_font)

        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.8);
                border: none;
                border-radius: 15px;
                color: black;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 1);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(18, 159, 73, 0.4);
            }
        """)

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад", self)
        self.back_button.setGeometry(20, 20, 100, 40)

        back_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            back_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            back_font.setFamily("Arial")

        back_font.setPointSize(16)
        self.back_button.setFont(back_font)

        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(18, 159, 73, 0.8);
                border-radius: 8px;
                color: rgba(0, 0, 0, 1);
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 0.2);
            }
        """)

        self.title_label = title_label
        self.private_key_label = private_key_label
        self.role_label = role_label
        self.password_label = password_label
        self.main_frame = main_frame

    def setup_connections(self):
        self.register_button.clicked.connect(self.register)
        self.back_button.clicked.connect(self.back_to_login_clicked.emit)
        self.private_key_input.returnPressed.connect(self.register)
        self.password_input.returnPressed.connect(self.register)

        self.role_combo.currentIndexChanged.connect(self.validate_role_selection)

    def validate_role_selection(self, index):
        if index == 0:
            self.register_button.setEnabled(False)
        else:
            self.register_button.setEnabled(True)

    def register(self):
        private_key = self.private_key_input.text()
        password = self.password_input.text()
        role_index = self.role_combo.currentIndex()

        if not private_key:
            QMessageBox.warning(self, "Ошибка", "Введите приватный ключ")
            return
        if not password:
            QMessageBox.warning(self, "Ошибка", "Придумайте пароль")
            return
        if role_index == 0:
            QMessageBox.warning(self, "Ошибка", "Выберите роль")
            return

        role = self.role_combo.currentText()

        if len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 4 символа")
            return

        # Отправляем данные через сигнал
        self.registration_complete.emit({
            'private_key': private_key,
            'password': password,
            'role': role
        })

        self.private_key_input.clear()
        self.password_input.clear()
        self.role_combo.setCurrentIndex(0)

    def get_registration_data(self):
        return {
            'private_key': self.private_key_input.text(),
            'password': self.password_input.text(),
            'role': self.role_combo.currentText() if self.role_combo.currentIndex() > 0 else ""
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RegisterWindow()
    window.show()

    sys.exit(app.exec())