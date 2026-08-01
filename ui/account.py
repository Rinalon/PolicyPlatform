import sys
import os
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame,
                             QVBoxLayout, QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QPainter

from source.utils import User

class AccountWindow(QWidget):
    policies_clicked = pyqtSignal()
    insurance_products_clicked = pyqtSignal()
    transaction_history_clicked = pyqtSignal()
    logout_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Аккаунт")
        self.setFixedSize(1280, 800)
        self.load_fonts()
        self.init_ui()
        self.setup_connections()

    def load_fonts(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        inter_path = os.path.join(base_dir, "templates", "font", "Inter_1.ttf")
        font_paths = {"Inter": inter_path}

        self.fonts_loaded = {}
        for font_name, font_path in font_paths.items():
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        self.fonts_loaded[font_name] = families[0]
            else:
                print(f"Файл шрифта Inter не найден: {font_path}")

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(189, 241, 202, 1);
            }
        """)

        # Основной контейнер
        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, 1280, 800)
        main_frame.setStyleSheet("background-color: rgba(189, 241, 202, 1);")

        # Шапка
        self.header_background = QLabel(main_frame)
        self.header_background.setGeometry(352, 30, 577, 76)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        hat_path = os.path.join(base_dir, "templates", "image", "block.png")

        if os.path.exists(hat_path):
            pixmap = QPixmap(hat_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(577, 76,
                                              Qt.AspectRatioMode.IgnoreAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.header_background.setPixmap(scaled_pixmap)
                self.header_background.setScaledContents(True)
            else:
                print(f"Не удалось загрузить изображение: {hat_path}")
                self.header_background.setStyleSheet("""
                           QLabel {
                               background-color: rgba(18, 159, 73, 0.44);
                               border-radius: 46px;
                               opacity: 0.89;
                           }
                       """)
        else:
            print(f"Файл изображения не найден: {hat_path}")
            self.header_background.setStyleSheet("""
                       QLabel {
                           background-color: rgba(18, 159, 73, 0.44);
                           border-radius: 46px;
                           opacity: 0.89;
                       }
                   """)

        self.header_background.setStyleSheet("""
            QLabel {
                border-radius: 46px;
            }
        """)

        title_label = QLabel("Аккаунт", main_frame)
        title_label.setGeometry(352, 30, 577, 76)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        if "Inter" in self.fonts_loaded:
            title_font.setFamily(self.fonts_loaded["Inter"])
        else:
            title_font.setFamily("Arial")

        title_font.setPointSize(40)
        title_font.setWeight(400)
        title_label.setFont(title_font)

        title_label.setStyleSheet("""
            QLabel {
                color: rgba(0, 0, 0, 1);
                background-color: transparent;
                letter-spacing: 5px;
            }
        """)

        # Кнопка основной страницы полисов
        self.policies_button = QPushButton(main_frame)
        self.policies_button.setGeometry(29, 30, 70, 70)
        self.policies_button.setCursor(Qt.CursorShape.PointingHandCursor)

        icon_path = os.path.join(base_dir, "templates", "image", "policies.png")
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path)
            self.policies_button.setIcon(QIcon(icon_pixmap))
            self.policies_button.setIconSize(self.policies_button.size())
            self.policies_button.setText("")
        else:
            print(f"Файл иконки не найден: {icon_path}")
            self.policies_button.setText("≡")
            font = QFont()
            font.setPointSize(20)
            self.policies_button.setFont(font)

        self.policies_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)

        # Информационная панель
        info_panel = QFrame(main_frame)
        info_panel.setGeometry(50, 220, 865, 111)
        info_panel.setStyleSheet("""
                    QFrame {
                        background-color: rgba(18, 159, 73, 0.44);
                        border-radius: 0px;
                        opacity: 0.89;
                    }
                """)

        self.role_label = QLabel("Роль:", main_frame)
        self.role_label.setGeometry(61, 229, 865, 47)

        self.address_label = QLabel("Адрес:", main_frame)
        self.address_label.setGeometry(61, 276, 865, 47)


        info_font = QFont()
        if "Inter" in self.fonts_loaded:
            info_font.setFamily(self.fonts_loaded["Inter"])
        else:
            info_font.setFamily("Arial")

        info_font.setPointSize(15)
        info_font.setWeight(400)

        for label in [self.role_label, self.address_label]:
            label.setFont(info_font)
            label.setStyleSheet("""
                QLabel {
                    color: rgba(0, 0, 0, 1);
                    background-color: transparent;
                    letter-spacing: 5px;
                }
            """)

        wallet_path = os.path.join(base_dir, "templates", "image", "wallet_icon.png")
        self.wallet_icon = QLabel(main_frame)
        self.wallet_icon.setGeometry(908, 220, 120, 111)
        if os.path.exists(wallet_path):
            pixmap = QPixmap(wallet_path)
            if not pixmap.isNull():
                self.wallet_icon.setPixmap(pixmap)
                self.wallet_icon.setScaledContents(True)
            else:
                print(f"Не удалось загрузить изображение: {wallet_path}")
        else:
            print(f"Файл изображения не найден: {wallet_path}")

        self.balance_label = QLabel("0", main_frame)
        self.balance_label.setGeometry(1040, 220, 140, 130)
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        balance_font = QFont()
        if "Inter" in self.fonts_loaded:
            balance_font.setFamily(self.fonts_loaded["Inter"])
        else:
            balance_font.setFamily("Arial")

        balance_font.setPointSize(26)
        balance_font.setWeight(500)
        self.balance_label.setFont(balance_font)

        # Кнопка "Мои страховые продукты"
        self.insurance_button = QPushButton("Мои\nстраховые продукты", main_frame)
        self.insurance_button.setGeometry(50, 467, 553, 185)
        self.insurance_button.setCursor(Qt.CursorShape.PointingHandCursor)

        button_font = QFont()
        if "Inter" in self.fonts_loaded:
            button_font.setFamily(self.fonts_loaded["Inter"])
        else:
            button_font.setFamily("Arial")

        button_font.setPointSize(25)
        button_font.setWeight(400)
        self.insurance_button.setFont(button_font)

        self.insurance_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(18, 159, 73, 0.44);
                        border: none;
                        border-radius: 0px;
                        color: rgba(0, 0, 0, 1);
                        letter-spacing: 5px;
                        opacity: 0.89;
                        text-align: center;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgba(18, 159, 73, 0.6);
                        opacity: 1;
                    }
                    QPushButton:pressed {
                        background-color: rgba(18, 159, 73, 0.7);
                        padding: 12px 8px 8px 12px;
                    }
                """)

        # Кнопка "История транзакций"
        self.transaction_button = QPushButton("История\nтранзакций", main_frame)
        self.transaction_button.setGeometry(677, 467, 553, 185)  # left: 677px, top: 467px
        self.transaction_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.transaction_button.setFont(button_font)

        self.transaction_button.setStyleSheet("""
                   QPushButton {
                       background-color: rgba(18, 159, 73, 0.44);
                       border: none;
                       border-radius: 0px;
                       color: rgba(0, 0, 0, 1);
                       letter-spacing: 5px;
                       opacity: 0.89;
                       text-align: center;
                       padding: 10px;
                   }
                   QPushButton:hover {
                       background-color: rgba(18, 159, 73, 0.6);
                       opacity: 1;
                   }
                   QPushButton:pressed {
                       background-color: rgba(18, 159, 73, 0.7);
                       padding: 12px 8px 8px 12px;
                   }
               """)

        # Кнопка "Выйти"
        self.logout_button = QPushButton("Выйти", main_frame)
        self.logout_button.setGeometry(1150, 30, 100, 40)

        logout_font = QFont()
        if "Inter" in self.fonts_loaded:
            logout_font.setFamily(self.fonts_loaded["Inter"])
        else:
            logout_font.setFamily("Arial")

        logout_font.setPointSize(16)
        self.logout_button.setFont(logout_font)

        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(18, 159, 73, 0.8);
                border-radius: 8px;
                color: rgba(0, 0, 0, 1);
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.7);
            }
        """)

        self.title_label = title_label

    def setup_connections(self):
        self.policies_button.clicked.connect(self.policies_clicked.emit)
        self.insurance_button.clicked.connect(self.insurance_products_clicked.emit)
        self.transaction_button.clicked.connect(self.transaction_history_clicked.emit)
        self.logout_button.clicked.connect(self.logout_clicked.emit)

    def set_user_info(self, role: str, address: str, balance: int):
        self.role_label.setText(f"Роль: {role}")
        self.address_label.setText(f"Адрес: {address}")
        self.balance_label.setText(f"{balance / 10**18}")

    def set_insurance_button_text(self, text):
        self.insurance_button.setText(text)

    def set_transaction_button_text(self, text):
        self.transaction_button.setText(text)