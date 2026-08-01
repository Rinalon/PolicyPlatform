import sys
import os
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QFrame, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase


class LoginWindow(QWidget):

    register_clicked = pyqtSignal()
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
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
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(189, 241, 202, 1);
            }
        """)

        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, 1280, 800)
        main_frame.setStyleSheet("background-color: rgba(189, 241, 202, 1);")

        card = QFrame(main_frame)
        card.setGeometry(329, 135, 625, 530)  # left: 329px, top: 135px
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 159, 73, 0.44);
                border-radius: 46px;
            }
        """)

        # Заголовок
        title_label = QLabel("Войти", main_frame)
        title_label.setGeometry(327, 170, 625, 76)  # left: 327px, top: 210px
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
                letter-spacing: 5px;
            }
        """)

        # Поле ввода приватного ключа
        key_label = QLabel("Приватный ключ", main_frame)
        key_label.setGeometry(329, 265, 625, 43)  # left: 329px, top: 349px
        key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        key_label_font = QFont()
        if "Kameron" in self.fonts_loaded:
            key_label_font.setFamily(self.fonts_loaded["Kameron"])
        else:
            key_label_font.setFamily("Georgia")

        key_label_font.setPointSize(25)
        key_label.setFont(key_label_font)

        key_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 1);
                background-color: transparent;
                letter-spacing: 2px;
            }
        """)

        self.key_input = QLineEdit(main_frame)
        self.key_input.setGeometry(354, 325, 575, 50)
        self.key_input.setPlaceholderText("Введите приватный ключ")

        key_input_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            key_input_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            key_input_font.setFamily("Arial")

        key_input_font.setPointSize(15)
        key_input_font.setWeight(400)
        self.key_input.setFont(key_input_font)

        self.key_input.setStyleSheet("""
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

        # Поле ввода пароля
        password_label = QLabel("Пароль", main_frame)
        password_label.setGeometry(329, 390, 625, 43)  # left: 329px, top: 492px
        password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
                letter-spacing: 2px;
            }
        """)

        self.password_input = QLineEdit(main_frame)
        self.password_input.setGeometry(354, 440, 575, 50)  # left: 354px, top: 553px
        self.password_input.setPlaceholderText("Введите пароль")
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

        # Кнопка "Войти"
        self.login_button = QPushButton("Войти", main_frame)
        self.login_button.setGeometry(492, 520, 295, 60)

        button_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            button_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            button_font.setFamily("Arial")

        button_font.setPointSize(30)
        button_font.setWeight(400)
        self.login_button.setFont(button_font)

        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.9);
                border: none;
                border-radius: 25px;
                color: white;
                padding: 10px;
                font-size: 25px;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 1);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 0.8);
                padding: 11px 9px 9px 11px;
            }
            QPushButton:disabled {
                background-color: rgba(18, 159, 73, 0.4);
                color: rgba(255, 255, 255, 0.6);
            }
        """)

        # Кнопка "Зарегистрироваться"
        self.register_link = QPushButton("Зарегистрироваться", main_frame)
        self.register_link.setGeometry(327, 600, 625, 32)  # left: 327px, top: 620px

        link_font = QFont()
        if "Kantumruy" in self.fonts_loaded:
            link_font.setFamily(self.fonts_loaded["Kantumruy"])
        else:
            link_font.setFamily("Arial")

        link_font.setPointSize(15)
        link_font.setWeight(400)
        self.register_link.setFont(link_font)

        self.register_link.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgba(0, 0, 0, 1);
                text-decoration: none;
                text-align: center;
                padding: 0px;
            }
            QPushButton:hover {
                color: rgba(0, 0, 0, 0.7);
                cursor: pointer;
            }
            QPushButton:pressed {
                color: rgba(0, 0, 0, 0.5);
            }
        """)

        self.title_label = title_label
        self.key_label = key_label
        self.password_label = password_label
        self.card = card
        self.main_frame = main_frame

    def setup_connections(self):
        self.register_link.clicked.connect(self.register_clicked.emit)
        self.login_button.clicked.connect(self.login)
        self.key_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

    def login(self):
        private_key = self.key_input.text()
        password = self.password_input.text()

        if not private_key:
            QMessageBox.warning(self, "Ошибка", "Введите приватный ключ")
            self.key_input.setFocus()
            return
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            self.password_input.setFocus()
            return

        if len(password) >= 4:
            self.login_successful.emit({
                'private_key': private_key,
                'password': password
            })
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные данные")
            self.password_input.clear()
            self.password_input.setFocus()

    def get_credentials(self):
        return {
            'private_key': self.key_input.text(),
            'password': self.password_input.text()
        }

    def clear_fields(self):
        self.key_input.clear()
        self.password_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())