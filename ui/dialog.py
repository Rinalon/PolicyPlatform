import sys
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QMessageBox, QLineEdit, QScrollArea,
                             QFormLayout, QWidget, QTextEdit, QSpinBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase

from source.utils import PolicyData, format_duration, format_date, format_address

class PolicyDialog(QDialog):

    contract_requested = pyqtSignal(int)  # ID полиса

    def __init__(self, policy=None, user_role=None, parent=None):
        super().__init__(parent)
        self.policy = policy
        self.user_role = user_role

        self.setWindowTitle(f"Полис #{policy.id}")
        self.setFixedSize(1000, 800)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(18, 159, 73, 0.2);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(18, 159, 73, 0.6);
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(18, 159, 73, 0.8);
            }
        """)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Заголовок
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 159, 73, 0.44);
                border-radius: 20px;
                padding: 20px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)

        title_label = QLabel(f"Полис #{self.policy.id}")
        title_font = QFont()
        title_font.setFamily("Inter")
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #000000; 
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        main_layout.addWidget(header_frame)

        # Информационная карточка
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                border: 2px solid rgba(18, 159, 73, 0.3);
                padding: 25px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)

        status = self.policy.status

        fields = [
            ("Статус", status),
            ("Условия страхования",  self.policy.conditions),
            ("Сумма выплаты", f"{self.policy.payoutAmount / 10**18:,} BLY"),
            ("Срок действия", format_duration(self.policy.durationWork)),
            ("Страховщик", format_address(self.policy.insurer))
        ]

        for label_text, value_text in fields:
            field_layout = QHBoxLayout()

            label = QLabel(label_text)
            label_font = QFont()
            label_font.setFamily("Arial")
            label_font.setPointSize(13)
            label_font.setBold(True)
            label.setFont(label_font)
            label.setStyleSheet("""
                QLabel {
                    color: #000000;
                    background-color: transparent;
                }
            """)
            label.setFixedWidth(200)

            value = QLabel(str(value_text))
            value_font = QFont()
            value_font.setFamily("Arial")
            value_font.setPointSize(13)
            value.setFont(value_font)

            value.setStyleSheet("""
                QLabel {
                    color: #333333;
                    background-color: transparent;
                }
            """)

            value.setWordWrap(True)

            field_layout.addWidget(label)
            field_layout.addWidget(value, 1)
            info_layout.addLayout(field_layout)

            field_layout.addWidget(label)
            field_layout.addWidget(value, 1)
            info_layout.addLayout(field_layout)

        main_layout.addWidget(info_frame)

        # Кнопки
        buttons_layout = QHBoxLayout()

        # Кнопка "Закрыть"
        self.close_button = QPushButton("Закрыть")
        self.close_button.setFixedSize(150, 40)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.7);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 1);
            }
        """)

        # Кнопка "Заключить контракт" (только для Страхователя с доступными полисами)
        self.contract_button = None

        button_rols = ["Страхователь", "Policyholder", "страхователь", "policyholder"]
        is_avail = status == "Доступен" or status == "Available"

        if self.user_role in button_rols and is_avail:
            self.contract_button = QPushButton("Заключить контракт")
            self.contract_button.setFixedSize(200, 40)
            self.contract_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(18, 159, 73, 0.7);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(18, 159, 73, 0.9);
                }
                QPushButton:disabled {
                    background-color: rgba(18, 159, 73, 0.3);
                    color: rgba(255, 255, 255, 0.5);
                }
            """)

        if self.contract_button:
            buttons_layout.addWidget(self.contract_button)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)

        main_layout.addLayout(buttons_layout)

        scroll_area.setWidget(container)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)

    def setup_connections(self):
        self.close_button.clicked.connect(self.reject)

        if self.contract_button:
            self.contract_button.clicked.connect(self.request_contract_directly)

    def request_contract_directly(self):
        if self.policy.id:
            self.contract_requested.emit(self.policy.id)
            self.accept()


class PremiumDialog(QDialog):

    premium_submitted = pyqtSignal(int, float)

    def __init__(self, policy_id, min_premium=10.0, parent=None):
        super().__init__(parent)
        self.policy_id = policy_id
        self.MIN_PREMIUM = min_premium

        self.setWindowTitle(f"Ввод суммы премии - Полис #{policy_id}")
        self.setFixedSize(600, 450)

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 255, 255, 1);
            }

            QLabel {
                color: #000000;
                background-color: transparent;
            }
        """)

        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, 600, 450)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 1);
            }
        """)

        # Заголовок
        title_label = QLabel("Ввод суммы премии", main_frame)
        title_label.setGeometry(50, 40, 500, 50)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        title_font.setFamily("Arial")

        title_font.setPointSize(28)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        # Подзаголовок
        policy_label = QLabel(f"Для полиса #{self.policy_id}", main_frame)
        policy_label.setGeometry(50, 100, 500, 30)
        policy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        policy_font = QFont()
        policy_font.setFamily("Arial")

        policy_font.setPointSize(16)
        policy_font.setWeight(QFont.Weight.Normal)
        policy_label.setFont(policy_font)
        policy_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        # Метки

        instruction = QLabel("Введите сумму первоначального взноса (BLY):", main_frame)
        instruction.setGeometry(70, 160, 460, 30)

        inst_font = QFont()
        inst_font.setFamily("Arial")

        inst_font.setPointSize(14)
        inst_font.setWeight(QFont.Weight.Bold)
        instruction.setFont(inst_font)
        instruction.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        amount_label = QLabel("Сумма (BLY):", main_frame)
        amount_label.setGeometry(70, 210, 200, 30)

        amount_font = QFont()
        amount_font.setFamily("Arial")

        amount_font.setPointSize(13)
        amount_label.setFont(amount_font)
        amount_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        # Поле ввода суммы
        self.premium_input = QLineEdit(main_frame)
        self.premium_input.setGeometry(280, 205, 250, 40)
        self.premium_input.setPlaceholderText(f"Минимум: {self.MIN_PREMIUM} BLY")

        input_font = QFont()
        input_font.setFamily("Arial")

        input_font.setPointSize(14)
        self.premium_input.setFont(input_font)

        self.premium_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid rgba(18, 159, 73, 0.5);
                border-radius: 10px;
                padding: 0px 15px;
                color: #000000;
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid rgba(18, 159, 73, 1);
            }
        """)

        min_label = QLabel(f"* Минимальная сумма взноса: {self.MIN_PREMIUM} BLY", main_frame)
        min_label.setGeometry(70, 260, 460, 25)

        min_font = QFont()
        min_font.setFamily("Arial")

        min_font.setPointSize(11)
        min_label.setFont(min_font)
        min_label.setStyleSheet("""
            QLabel { 
                color: #666666; 
                background-color: transparent; 
                font-style: italic; 
            }
        """)

        # Метка валидации
        self.validation = QLabel("", main_frame)
        self.validation.setGeometry(70, 290, 460, 30)

        valid_font = QFont()
        valid_font.setFamily("Arial")

        valid_font.setPointSize(12)
        valid_font.setWeight(QFont.Weight.Bold)
        self.validation.setFont(valid_font)
        self.validation.setStyleSheet("""
            QLabel { 
                background-color: transparent; 
                color: #000000;
            }
        """)

        # Кнопка "Отмена"
        self.cancel_button = QPushButton("Отмена", main_frame)
        self.cancel_button.setGeometry(210, 350, 120, 45)

        cancel_font = QFont()
        cancel_font.setFamily("Arial")

        cancel_font.setPointSize(16)
        cancel_font.setWeight(QFont.Weight.Bold)
        self.cancel_button.setFont(cancel_font)

        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 53, 69, 0.8);
                border: none;
                border-radius: 15px;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 1);
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.9);
            }
        """)

        # Кнопка "Подтвердить"
        self.confirm_button = QPushButton("Подтвердить", main_frame)
        self.confirm_button.setGeometry(380, 350, 200, 45)
        self.confirm_button.setEnabled(False)

        confirm_font = QFont()
        confirm_font.setFamily("Arial")

        confirm_font.setPointSize(16)
        confirm_font.setWeight(QFont.Weight.Bold)
        self.confirm_button.setFont(confirm_font)

        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.8);
                border: none;
                border-radius: 15px;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 1);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(18, 159, 73, 0.3);
                color: rgba(255, 255, 255, 0.5);
            }
        """)

    def setup_connections(self):
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.submit_premium)
        self.premium_input.textChanged.connect(self.validate_premium)
        self.premium_input.returnPressed.connect(self.submit_premium)

    def validate_premium(self):
        premium_text = self.premium_input.text().strip()

        if not premium_text:
            self.confirm_button.setEnabled(False)
            self.validation.setText("Введите сумму премии")
            self.validation.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)
            return

        try:
            premium = float(premium_text)
            if premium >= self.MIN_PREMIUM:
                self.confirm_button.setEnabled(True)
                self.validation.setText("Сумма соответствует требованиям")
                self.validation.setStyleSheet("""
                    QLabel { 
                        color: #28a745; 
                        background-color: transparent; 
                        font-weight: bold;
                    }
                """)
            else:
                self.confirm_button.setEnabled(False)
                self.validation.setText(f"Минимальная сумма: {self.MIN_PREMIUM} BLY!")
                self.validation.setStyleSheet("""
                    QLabel { 
                        color: #dc3545; 
                        background-color: transparent; 
                        font-weight: bold;
                """)
        except ValueError:
            self.confirm_button.setEnabled(False)
            self.validation.setText("Введите корректное число!")
            self.validation.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)

    def submit_premium(self):
        if not self.confirm_button.isEnabled():
            return

        premium_text = self.premium_input.text().strip()

        try:
            premium = float(premium_text)

            if premium < self.MIN_PREMIUM:
                QMessageBox.warning(self, "Ошибка", f"Минимальная сумма премии: {self.MIN_PREMIUM} BLY")
                return

            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите внести премию {premium:.2f} BLY\nдля полиса #{self.policy_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.premium_submitted.emit(self.policy_id, premium)
                self.accept()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректную сумму")

    def showEvent(self, event):
        super().showEvent(event)
        self.premium_input.setFocus()

class AddedDialog(QDialog):
    policy_data_submitted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        title = "Создание нового полиса"
        self.setWindowTitle(title)
        self.setFixedSize(800, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(18, 159, 73, 0.2);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(18, 159, 73, 0.6);
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(18, 159, 73, 0.8);
            }
        """)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 159, 73, 0.44);
                border-radius: 20px;
                padding: 15px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)

        title = "Создание нового полиса"
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setFamily("Inter")
        title_font.setPointSize(22)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #000000; 
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        main_layout.addWidget(header_frame)

        # Форма
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                border: 2px solid rgba(18, 159, 73, 0.3);
                padding: 20px;
            }
        """)

        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)

        # Поле "Название полиса"
        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)
        name_label = QLabel("Название полиса:")
        name_label.setFixedWidth(200)
        name_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-weight: bold;
                font-size: 14px;
                padding: 5px 0px;
            }
        """)

        self.name_input = QLineEdit()
        self.name_input.setMaxLength(40)
        self.name_input.setPlaceholderText("Введите название полиса (до 40 символов)")
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
                background-color: #fff;
            }
        """)

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input, 1)
        form_layout.addLayout(name_layout)

        # Поле "Размер выплаты"
        payout_layout = QHBoxLayout()
        payout_layout.setSpacing(10)
        payout_label = QLabel("Размер выплаты (BLY):")
        payout_label.setFixedWidth(200)
        payout_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-weight: bold;
                font-size: 14px;
                padding: 5px 0px;
            }
        """)

        self.payout_input = QLineEdit()
        self.payout_input.setPlaceholderText("Введите размер выплаты в BLY")
        self.payout_input.setText("100.0")
        self.payout_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
                background-color: #fff;
            }
        """)

        payout_layout.addWidget(payout_label)
        payout_layout.addWidget(self.payout_input, 1)
        form_layout.addLayout(payout_layout)

        # Поле "Условия страхования"
        conditions_layout = QVBoxLayout()
        conditions_layout.setSpacing(5)
        conditions_label = QLabel("Условия страхования:")
        conditions_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-weight: bold;
                font-size: 14px;
                padding: 5px 0px;
            }
        """)

        self.conditions_input = QTextEdit()
        self.conditions_input.setPlaceholderText("Введите условия страхования...")
        self.conditions_input.setMaximumHeight(100)
        self.conditions_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: white;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
                background-color: #fff;
            }
        """)

        self.conditions_input.textChanged.connect(self.limit_conditions_length)
        conditions_layout.addWidget(conditions_label)
        conditions_layout.addWidget(self.conditions_input)
        form_layout.addLayout(conditions_layout)

        # Поле "Продолжительность"
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(10)
        duration_label = QLabel("Продолжительность:")
        duration_label.setFixedWidth(200)
        duration_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-weight: bold;
                font-size: 14px;
                padding: 5px 0px;
            }
        """)

        duration_fields_layout = QHBoxLayout()
        duration_fields_layout.setSpacing(15)

        # Годы
        years_layout = QVBoxLayout()
        years_layout.setSpacing(5)
        years_label = QLabel("Лет:")
        years_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        years_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-size: 13px;
            }
        """)

        self.years_input = QSpinBox()
        self.years_input.setRange(0, 100)
        self.years_input.setValue(1)
        self.years_input.setSuffix(" год")
        self.years_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: rgba(18, 159, 73, 0.2);
                border-radius: 4px;
            }
        """)

        years_layout.addWidget(years_label)
        years_layout.addWidget(self.years_input)

        # Месяцы
        months_layout = QVBoxLayout()
        months_layout.setSpacing(5)
        months_label = QLabel("Месяцы:")
        months_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        months_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-size: 13px;
            }
        """)

        self.months_input = QSpinBox()
        self.months_input.setRange(0, 11)
        self.months_input.setValue(0)
        self.months_input.setSuffix(" мес.")
        self.months_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: rgba(18, 159, 73, 0.2);
                border-radius: 4px;
            }
        """)

        months_layout.addWidget(months_label)
        months_layout.addWidget(self.months_input)

        # Дни
        days_layout = QVBoxLayout()
        days_layout.setSpacing(5)
        days_label = QLabel("Дни:")
        days_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        days_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-size: 13px;
            }
        """)

        self.days_input = QSpinBox()
        self.days_input.setRange(0, 30)
        self.days_input.setValue(0)
        self.days_input.setSuffix(" дней")
        self.days_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: rgba(18, 159, 73, 0.2);
                border-radius: 4px;
            }
        """)

        days_layout.addWidget(days_label)
        days_layout.addWidget(self.days_input)

        duration_fields_layout.addLayout(years_layout)
        duration_fields_layout.addLayout(months_layout)
        duration_fields_layout.addLayout(days_layout)

        duration_layout.addWidget(duration_label)
        duration_layout.addLayout(duration_fields_layout, 1)
        form_layout.addLayout(duration_layout)

        # Поле "Количество выплат"
        payout_count_layout = QHBoxLayout()
        payout_count_layout.setSpacing(10)
        payout_count_label = QLabel("Количество выплат:")
        payout_count_label.setFixedWidth(200)
        payout_count_label.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: transparent;
                font-weight: bold;
                font-size: 14px;
                padding: 5px 0px;
            }
        """)

        self.payout_count_input = QSpinBox()
        self.payout_count_input.setRange(1, 100)
        self.payout_count_input.setValue(1)
        self.payout_count_input.setSuffix(" выплат")
        self.payout_count_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 120px;
            }
            QSpinBox:focus {
                border: 2px solid rgba(18, 159, 73, 0.6);
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: rgba(18, 159, 73, 0.2);
                border-radius: 4px;
            }
        """)

        payout_count_layout.addWidget(payout_count_label)
        payout_count_layout.addWidget(self.payout_count_input)
        form_layout.addLayout(payout_count_layout)

        main_layout.addWidget(form_frame)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        # Кнопка "Отмена"
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setFixedSize(150, 45)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 53, 69, 0.8);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 1);
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.9);
            }
        """)

        # Кнопка "Создать"
        button_text = "Создать"
        self.save_button = QPushButton(button_text)
        self.save_button.setFixedSize(180, 45)
        self.save_button.setEnabled(True)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.9);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 1);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 0.8);
            }
            QPushButton:disabled {
                background-color: rgba(18, 159, 73, 0.3);
                color: rgba(255, 255, 255, 0.7);
            }
        """)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

        scroll_area.setWidget(container)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)

    def setup_connections(self):
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.submit_policy_data)
        self.name_input.textChanged.connect(self.validate_form)
        self.conditions_input.textChanged.connect(self.validate_form)
        self.years_input.valueChanged.connect(self.validate_form)
        self.months_input.valueChanged.connect(self.validate_form)
        self.days_input.valueChanged.connect(self.validate_form)
        self.payout_count_input.valueChanged.connect(self.validate_form)
        self.payout_input.textChanged.connect(self.validate_form)

    def limit_conditions_length(self):
        text = self.conditions_input.toPlainText()
        max_length = 256

        if len(text) > max_length:
            cursor = self.conditions_input.textCursor()
            position = cursor.position()

            self.conditions_input.setPlainText(text[:max_length])
            cursor.setPosition(min(position, max_length))
            self.conditions_input.setTextCursor(cursor)

            self.conditions_input.setStyleSheet("""
                QTextEdit {
                    border: 2px solid rgba(220, 53, 69, 0.5);
                    border-radius: 8px;
                    padding: 10px;
                    background-color: #fff5f5;
                }
            """)
        else:
            self.conditions_input.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: white;
                }
                QTextEdit:focus {
                    border: 2px solid rgba(18, 159, 73, 0.6);
                    background-color: #fff;
                }
            """)

    def validate_form(self):
        name = self.name_input.text().strip()
        conditions = self.conditions_input.toPlainText().strip()
        payout_text = self.payout_input.text().strip()

        is_valid = bool(name) and bool(conditions) and bool(payout_text)

        if payout_text:
            try:
                payout = float(payout_text)
                if payout <= 0:
                    is_valid = False
            except ValueError:
                is_valid = False

        # Проверка продолжительности
        years = self.years_input.value()
        months = self.months_input.value()
        days = self.days_input.value()
        if years == 0 and months == 0 and days == 0:
            is_valid = False

        self.save_button.setEnabled(is_valid)

    def calculate_duration(self) -> int:
        years = self.years_input.value()
        months = self.months_input.value()
        days = self.days_input.value()

        total = ((years * 365) + (months * 30) + days) * 86400
        return total

    def submit_policy_data(self):
        name = self.name_input.text().strip()
        conditions = self.conditions_input.toPlainText().strip()
        payout_text = self.payout_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название полиса")
            return

        if not conditions:
            QMessageBox.warning(self, "Ошибка", "Введите условия страхования")
            return

        if not payout_text:
            QMessageBox.warning(self, "Ошибка", "Введите размер выплаты")
            return

        try:
            payout_amount = float(payout_text)
            if payout_amount <= 0:
                QMessageBox.warning(self, "Ошибка", "Размер выплаты должен быть положительным числом")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректный размер выплаты")
            return

        if len(conditions) > 256:
            QMessageBox.warning(self, "Ошибка", "Условия слишком длинные (максимум 256 символов)")
            return

        duration = self.calculate_duration()

        if duration <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите продолжительность полиса")
            return

        policy_data = {
            'name': name,
            'conditions': conditions,
            'payout_amount': payout_amount,
            'duration': duration,
            'payout_count': self.payout_count_input.value()
        }

        self.policy_data_submitted.emit(policy_data)
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.validate_form()
        self.name_input.setFocus()


class DepositDialog(QDialog):
    deposit_submitted = pyqtSignal(int, float)

    def __init__(self, policy_id, parent=None):
        super().__init__(parent)
        self.policy_id = policy_id

        self.setWindowTitle(f"Внесение депозита - Полис #{policy_id}")
        self.setFixedSize(600, 450)

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 255, 255, 1);
            }

            QLabel {
                color: #000000;
                background-color: transparent;
            }
        """)

        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, 600, 450)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 1);
            }
        """)

        # Заголовок
        title_label = QLabel("Внесение депозита", main_frame)
        title_label.setGeometry(50, 40, 500, 50)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        title_font.setFamily("Arial")

        title_font.setPointSize(28)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        # Подзаголовок "Для полиса #{policy_id}"
        policy_label = QLabel(f"Для полиса #{self.policy_id}", main_frame)
        policy_label.setGeometry(50, 100, 500, 30)
        policy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        policy_font = QFont()
        policy_font.setFamily("Arial")

        policy_font.setPointSize(16)
        policy_font.setWeight(QFont.Weight.Normal)
        policy_label.setFont(policy_font)
        policy_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        instruction_label = QLabel("Введите сумму депозита (BLY):", main_frame)
        instruction_label.setGeometry(70, 160, 460, 30)

        instruction_font = QFont()
        instruction_font.setFamily("Arial")

        instruction_font.setPointSize(14)
        instruction_font.setWeight(QFont.Weight.Bold)
        instruction_label.setFont(instruction_font)
        instruction_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        # Метка "Сумма (BLY):"
        amount_label = QLabel("Сумма (BLY):", main_frame)
        amount_label.setGeometry(70, 210, 200, 30)

        amount_font = QFont()
        amount_font.setFamily("Arial")

        amount_font.setPointSize(13)
        amount_label.setFont(amount_font)
        amount_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        self.deposit_input = QLineEdit(main_frame)
        self.deposit_input.setGeometry(280, 205, 250, 40)
        self.deposit_input.setPlaceholderText("Введите сумму депозита")

        input_font = QFont()
        input_font.setFamily("Arial")

        input_font.setPointSize(14)
        self.deposit_input.setFont(input_font)

        self.deposit_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid rgba(0, 123, 255, 0.5);
                border-radius: 10px;
                padding: 0px 15px;
                color: #000000;
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0, 123, 255, 1);
            }
        """)

        info_label = QLabel("* Депозит можно вносить в любой момент действия полиса", main_frame)
        info_label.setGeometry(70, 260, 460, 25)

        info_font = QFont()
        info_font.setFamily("Arial")

        info_font.setPointSize(11)
        info_label.setFont(info_font)
        info_label.setStyleSheet("""
            QLabel { 
                color: #666666; 
                background-color: transparent; 
                font-style: italic; 
            }
        """)

        self.validation_label = QLabel("", main_frame)
        self.validation_label.setGeometry(70, 290, 460, 30)

        validation_font = QFont()
        validation_font.setFamily("Arial")

        validation_font.setPointSize(12)
        validation_font.setWeight(QFont.Weight.Bold)
        self.validation_label.setFont(validation_font)
        self.validation_label.setStyleSheet("""
            QLabel { 
                background-color: transparent; 
                color: #000000;
            }
        """)

        # Кнопка "Отмена"
        self.cancel_button = QPushButton("Отмена", main_frame)
        self.cancel_button.setGeometry(210, 350, 120, 45)

        cancel_font = QFont()
        cancel_font.setFamily("Arial")

        cancel_font.setPointSize(16)
        cancel_font.setWeight(QFont.Weight.Bold)
        self.cancel_button.setFont(cancel_font)

        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 53, 69, 0.8);
                border: none;
                border-radius: 15px;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 1);
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.9);
            }
        """)

        # Кнопка "Внести"
        self.deposit_button = QPushButton("Внести", main_frame)
        self.deposit_button.setGeometry(380, 350, 200, 45)
        self.deposit_button.setEnabled(False)

        deposit_font = QFont()
        deposit_font.setFamily("Arial")

        deposit_font.setPointSize(16)
        deposit_font.setWeight(QFont.Weight.Bold)
        self.deposit_button.setFont(deposit_font)

        self.deposit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 123, 255, 0.8);
                border: none;
                border-radius: 15px;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 123, 255, 1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 123, 255, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(0, 123, 255, 0.3);
                color: rgba(255, 255, 255, 0.5);
            }
        """)

    def setup_connections(self):
        self.cancel_button.clicked.connect(self.reject)
        self.deposit_button.clicked.connect(self.submit_deposit)
        self.deposit_input.textChanged.connect(self.validate_deposit)
        self.deposit_input.returnPressed.connect(self.submit_deposit)

    def validate_deposit(self):
        deposit_text = self.deposit_input.text().strip()

        if not deposit_text:
            self.deposit_button.setEnabled(False)
            self.validation_label.setText("Введите сумму депозита")
            self.validation_label.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)
            return

        try:
            deposit = float(deposit_text)
            if deposit > 0:
                self.deposit_button.setEnabled(True)
                self.validation_label.setText(f"Депозит: {deposit:.2f} BLY")
                self.validation_label.setStyleSheet("""
                    QLabel { 
                        color: #28a745; 
                        background-color: transparent; 
                        font-weight: bold;
                    }
                """)
            else:
                self.deposit_button.setEnabled(False)
                self.validation_label.setText("Сумма должна быть больше 0")
                self.validation_label.setStyleSheet("""
                    QLabel { 
                        color: #dc3545; 
                        background-color: transparent; 
                        font-weight: bold;
                """)
        except ValueError:
            self.deposit_button.setEnabled(False)
            self.validation_label.setText("Введите корректное число!")
            self.validation_label.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)

    def submit_deposit(self):
        if not self.deposit_button.isEnabled():
            return

        deposit_text = self.deposit_input.text().strip()

        try:
            deposit = float(deposit_text)

            if deposit <= 0:
                QMessageBox.warning(self, "Ошибка", "Сумма депозита должна быть больше 0")
                return

            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите внести депозит {deposit:.2f} BLY\nдля полиса #{self.policy_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.deposit_submitted.emit(self.policy_id, deposit)
                self.accept()

        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректную сумму")

    def showEvent(self, event):
        super().showEvent(event)
        self.deposit_input.setFocus()


class DetailsDialog(QDialog):
    deposit_requested = pyqtSignal(int, float)  # ID полиса и сумма депозита
    payout_requested = pyqtSignal(int)  # ID полиса для запроса выплаты
    terminate_requested = pyqtSignal(int)  # ID полиса для расторжения
    approve_payout_requested = pyqtSignal(int)  # ID полиса для одобрения выплаты
    reject_payout_requested = pyqtSignal(int)  # ID полиса для отклонения выплаты

    def __init__(self, policy=None, user_role="", button_func={}, parent=None):
        super().__init__(parent)
        self.policy = policy
        self.user_role = user_role

        self.setWindowTitle(f"Детали полиса #{self.policy.id}")
        self.setFixedSize(900, 700)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        self.init_ui()
        self.setup_connections(button_func)

    def setup_connections(self, button_func: dict):
        self.close_button.clicked.connect(self.reject)

        if self.terminate_button and 'terminate' in button_func:
            self.terminate_button.clicked.connect(
                lambda: button_func['terminate'](self.policy.id)
            )

        if self.approve_button and 'approve' in button_func:
            self.approve_button.clicked.connect(
                lambda: button_func['approve'](self.policy.id)
            )

        if self.reject_button and 'reject' in button_func:
            self.reject_button.clicked.connect(
                   lambda: button_func['reject'](self.policy.id)
            )

    def init_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(18, 159, 73, 0.2);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(18, 159, 73, 0.6);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(18, 159, 73, 0.8);
            }
        """)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 159, 73, 0.44);
                border-radius: 20px;
                padding: 20px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)

        title_label = QLabel(
            f"Полис #{self.policy.id} - {self.policy.name}")
        title_font = QFont()
        title_font.setFamily("Inter")
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #000000; 
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        main_layout.addWidget(header_frame)

        # Информационная карточка
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                border: 2px solid rgba(18, 159, 73, 0.3);
                padding: 25px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(12)

        # Определяем данные для отображения
        start_date = format_date(self.policy.startDate)
        end_date = format_date(self.policy.endDate)
        policy_fields = [
            ("ID", str(self.policy.id)),
            ("Название", self.policy.name),
            ("Статус", self.policy.status),
            ("Условия", self.policy.conditions),
            ("Размер выплаты", f"{self.policy.payoutAmount / 10**18:,} BLY"),
            ("Дата начала", start_date),
            ("Дата окончания", end_date),
            ("Страховщик", format_address(self.policy.insurer)),
            ("Страхователь", format_address(self.policy.policyholder)),
            ("Сумма депозитов", f"{self.policy.sumDeposits / 10**18:,} BLY"),
            ("Количество выплат", f"{self.policy.countOfPayout}")
        ]

        for label_text, value_text in policy_fields:
            field_layout = QHBoxLayout()

            label = QLabel(label_text)
            label_font = QFont()
            label_font.setFamily("Arial")
            label_font.setPointSize(12)
            label_font.setBold(True)
            label.setFont(label_font)
            label.setStyleSheet("""
                QLabel {
                    color: #000000;
                    background-color: transparent;
                }
            """)
            label.setFixedWidth(220)

            value = QLabel(str(value_text))
            value_font = QFont()
            value_font.setFamily("Arial")
            value_font.setPointSize(12)
            value.setFont(value_font)

            if label_text == "Статус:":
                status = value_text
                status_style = self.get_status_style(status)
                value.setStyleSheet(status_style)
            else:
                value.setStyleSheet("""
                    QLabel {
                        color: #333333;
                        background-color: transparent;
                    }
                """)

            value.setWordWrap(True)

            field_layout.addWidget(label)
            field_layout.addWidget(value, 1)
            info_layout.addLayout(field_layout)

        main_layout.addWidget(info_frame)

        # Дополнительная секция в зависимости от роли пользователя
        if self.user_role == "Страховщик" and self.policy.status == "На рассмотрении":
            requests_frame = QFrame()
            requests_frame.setStyleSheet("""
                QFrame {
                    background-color: #e9ecef;
                    border-radius: 15px;
                    border: 2px solid rgba(0, 123, 255, 0.3);
                    padding: 20px;
                }
            """)

            requests_layout = QVBoxLayout(requests_frame)

            requests_label = QLabel("Есть запрос на выплату:")
            requests_label_font = QFont()
            requests_label_font.setFamily("Arial")
            requests_label_font.setPointSize(14)
            requests_label_font.setBold(True)
            requests_label.setFont(requests_label_font)
            requests_label.setStyleSheet("""
                QLabel {
                    color: #000000;
                    background-color: transparent;
                }
            """)
            requests_layout.addWidget(requests_label)

            self.requests_text = QTextEdit()
            self.requests_text.setReadOnly(True)
            self.requests_text.setMaximumHeight(120)
            self.requests_text.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 12px;
                }
            """)

            requests_info = self.policy.proofs
            self.requests_text.setText(requests_info)

            requests_layout.addWidget(self.requests_text)

            main_layout.addWidget(requests_frame)

        # Кнопки действий в зависимости от статуса и роли пользователя
        self.action_buttons_layout = QHBoxLayout()

        self.approve_button = None
        self.reject_button = None
        self.terminate_button = None

        self.create_action_buttons()

        if self.action_buttons_layout.count() > 0:
            main_layout.addLayout(self.action_buttons_layout)

        # Кнопка "Закрыть"
        buttons_layout = QHBoxLayout()

        self.close_button = QPushButton("Закрыть")
        self.close_button.setFixedSize(150, 40)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.7);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 1);
            }
        """)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)

        main_layout.addLayout(buttons_layout)

        scroll_area.setWidget(container)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(scroll_area)

    def get_status_style(self, status):
        status = str(status).lower()

        if status == "На рассмотрении":
            return """
                QLabel {
                    color: #ffc107;
                    background-color: rgba(255, 193, 7, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """
        elif status == "Ожидает расторжения":
            return """
                QLabel {
                    color: #dc3545;
                    background-color: rgba(220, 53, 69, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """
        elif status == "Aктивен":
            return """
                QLabel {
                    color: #28a745;
                    background-color: rgba(40, 167, 69, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """
        elif status == "Pавершен":
            return """
                QLabel {
                    color: #6c757d;
                    background-color: rgba(108, 117, 125, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """
        elif status == "Доступен":
            return """
                QLabel {
                    color: #007bff;
                    background-color: rgba(0, 123, 255, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """
        else:
            return """
                QLabel {
                    color: #333333;
                    background-color: rgba(51, 51, 51, 0.1);
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """

    def create_action_buttons(self):
        status = self.policy.status
        policy_id = self.policy.id

        self.clear_action_buttons()

        # Добавляем кнопки в зависимости от статуса
        if status == "На рассмотрении":
            # Кнопка "Одобрить выплату"
            self.approve_button = QPushButton("Одобрить выплату")
            self.approve_button.setFixedSize(180, 40)
            self.approve_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 123, 255, 0.8);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(0, 123, 255, 1);
                }
                QPushButton:pressed {
                    background-color: rgba(0, 123, 255, 0.9);
                }
            """)
            self.approve_button.setProperty("policy_id", policy_id)

            # Кнопка "Отвергнуть выплату"
            self.reject_button = QPushButton("Отвергнуть выплату")
            self.reject_button.setFixedSize(180, 40)
            self.reject_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(220, 53, 69, 0.8);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(220, 53, 69, 1);
                }
                QPushButton:pressed {
                    background-color: rgba(220, 53, 69, 0.9);
                }
            """)
            self.reject_button.setProperty("policy_id", policy_id)

            self.action_buttons_layout.addWidget(self.approve_button)
            self.action_buttons_layout.addWidget(self.reject_button)
            self.action_buttons_layout.addStretch()

        elif status == "Ожидает расторжения":
            # Кнопка "Расторгнуть"
            self.terminate_button = QPushButton("Расторгнуть")
            self.terminate_button.setFixedSize(180, 40)
            self.terminate_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(220, 53, 69, 0.8);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(220, 53, 69, 1);
                }
                QPushButton:pressed {
                    background-color: rgba(220, 53, 69, 0.9);
                }
            """)
            self.terminate_button.setProperty("policy_id", policy_id)

            self.action_buttons_layout.addWidget(self.terminate_button)
            self.action_buttons_layout.addStretch()

    def clear_action_buttons(self):
        if self.approve_button:
            try:
                self.approve_button.clicked.disconnect()
            except:
                pass
        if self.reject_button:
            try:
                self.reject_button.clicked.disconnect()
            except:
                pass
        if self.terminate_button:
            try:
                self.terminate_button.clicked.disconnect()
            except:
                pass

        for i in reversed(range(self.action_buttons_layout.count())):
            widget = self.action_buttons_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.approve_button = None
        self.reject_button = None
        self.terminate_button = None

    def showEvent(self, event):
        super().showEvent(event)

class ClaimDialog(QDialog):
    claim_submitted = pyqtSignal(str)

    def __init__(self, policy_id, parent=None):
        super().__init__(parent)
        self.policy_id = policy_id

        self.setWindowTitle(f"Заявление о страховом случае - Полис #{policy_id}")
        self.setFixedSize(600, 600)

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(255, 255, 255, 1);
            }

            QLabel {
                color: #000000;
                background-color: transparent;
            }
        """)

        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0,600, 600)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 1);
            }
        """)

        # Заголовок
        title_label = QLabel("Заявление\nо страховом случае", main_frame)
        title_label.setGeometry(50, 30, 500, 100)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        title_font.setFamily("Arial")

        title_font.setPointSize(26)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        policy_label = QLabel(f"Для полиса #{self.policy_id}", main_frame)
        policy_label.setGeometry(50, 130, 500, 30)
        policy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        policy_font = QFont()
        policy_font.setFamily("Arial")

        policy_font.setPointSize(14)
        policy_font.setWeight(QFont.Weight.Normal)
        policy_label.setFont(policy_font)
        policy_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        instruction_label = QLabel("Опишите страховой случай и приложите доказательства:", main_frame)
        instruction_label.setGeometry(50, 160, 500, 30)

        instruction_font = QFont()
        instruction_font.setFamily("Arial")

        instruction_font.setPointSize(13)
        instruction_font.setWeight(QFont.Weight.Bold)
        instruction_label.setFont(instruction_font)
        instruction_label.setStyleSheet("""
            QLabel { 
                color: #000000; 
                background-color: transparent; 
            }
        """)

        self.proofs_input = QTextEdit(main_frame)
        self.proofs_input.setGeometry(50, 210, 500, 220)
        self.proofs_input.setPlaceholderText(
            "Опишите подробно страховой случай:\n"
            "- Дата и время происшествия\n"
            "- Место происшествия\n"
            "- Описание повреждений/ущерба\n"
            "- Свидетели (если есть)\n"
            "- Другие важные детали\n\n"
            "Максимальная длина: 256 символов"
        )

        input_font = QFont()
        input_font.setFamily("Arial")

        input_font.setPointSize(12)
        self.proofs_input.setFont(input_font)

        self.proofs_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid rgba(220, 53, 69, 0.5);
                border-radius: 10px;
                padding: 10px;
                color: #000000;
                font-size: 12px;
            }
            QTextEdit::placeholder {
                color: rgba(0, 0, 0, 0.5);
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid rgba(220, 53, 69, 1);
            }
        """)

        self.char_counter_label = QLabel("Символов: 0/256", main_frame)
        self.char_counter_label.setGeometry(50, 435, 300, 25)

        counter_font = QFont()
        counter_font.setFamily("Arial")

        counter_font.setPointSize(11)
        self.char_counter_label.setFont(counter_font)
        self.char_counter_label.setStyleSheet("""
            QLabel { 
                color: #666666; 
                background-color: transparent; 
                font-style: italic; 
            }
        """)

        # Подсказка
        info_label = QLabel("* Будьте максимально подробны.", main_frame)
        info_label.setGeometry(50, 450, 500, 25)

        info_font = QFont()
        info_font.setFamily("Arial")

        info_font.setPointSize(11)
        info_label.setFont(info_font)
        info_label.setStyleSheet("""
            QLabel { 
                color: #666666; 
                background-color: transparent; 
                font-style: italic; 
            }
        """)

        self.validation_label = QLabel("", main_frame)
        self.validation_label.setGeometry(50, 475, 500, 30)

        validation_font = QFont()
        validation_font.setFamily("Arial")

        validation_font.setPointSize(12)
        validation_font.setWeight(QFont.Weight.Bold)
        self.validation_label.setFont(validation_font)
        self.validation_label.setStyleSheet("""
            QLabel { 
                background-color: transparent; 
                color: #000000;
            }
        """)

        # Кнопка "Отмена"
        self.cancel_button = QPushButton("Отмена", main_frame)
        self.cancel_button.setGeometry(180, 515, 120, 40)

        cancel_font = QFont()
        cancel_font.setFamily("Arial")

        cancel_font.setPointSize(16)
        cancel_font.setWeight(QFont.Weight.Bold)
        self.cancel_button.setFont(cancel_font)

        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(108, 117, 125, 0.8);
                border: none;
                border-radius: 10px;
                color: white;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(108, 117, 125, 1);
            }
            QPushButton:pressed {
                background-color: rgba(108, 117, 125, 0.9);
            }
        """)

        # Кнопка "Отправить"
        self.submit_button = QPushButton("Отправить", main_frame)
        self.submit_button.setGeometry(330, 515, 220, 40)
        self.submit_button.setEnabled(False)

        submit_font = QFont()
        submit_font.setFamily("Arial")

        submit_font.setPointSize(16)
        submit_font.setWeight(QFont.Weight.Bold)
        self.submit_button.setFont(submit_font)

        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 53, 69, 0.8);
                border: none;
                border-radius: 10px;
                color: white;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 1);
            }
            QPushButton:pressed {
                background-color: rgba(220, 53, 69, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(220, 53, 69, 0.3);
                color: rgba(255, 255, 255, 0.5);
            }
        """)

    def setup_connections(self):
        self.cancel_button.clicked.connect(self.reject)
        self.submit_button.clicked.connect(self.submit_claim)
        self.proofs_input.textChanged.connect(self.validate_claim)

    def validate_claim(self):
        proofs_text = self.proofs_input.toPlainText().strip()
        char_count = len(proofs_text)

        self.char_counter_label.setText(f"Символов: {char_count}/256")

        if not proofs_text:
            self.submit_button.setEnabled(False)
            self.validation_label.setText("Введите описание страхового случая")
            self.validation_label.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)
            return

        if char_count < 20:
            self.submit_button.setEnabled(False)
            self.validation_label.setText("Опишите случай подробнее (минимум 20 символов)")
            self.validation_label.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)
            return

        if char_count > 256:
            self.submit_button.setEnabled(False)
            self.validation_label.setText("Превышен лимит символов (256)")
            self.validation_label.setStyleSheet("""
                QLabel { 
                    color: #dc3545; 
                    background-color: transparent; 
                    font-weight: bold;
                }
            """)
            return

        self.submit_button.setEnabled(True)
        self.validation_label.setText("Готово к отправке")
        self.validation_label.setStyleSheet("""
            QLabel { 
                color: #28a745; 
                background-color: transparent; 
                font-weight: bold;
            }
        """)

    def submit_claim(self):
        if not self.submit_button.isEnabled():
            return

        proofs_text = self.proofs_input.toPlainText().strip()
        char_count = len(proofs_text)

        if char_count < 20:
            QMessageBox.warning(self, "Ошибка", "Опишите страховой случай подробнее (минимум 20 символов)")
            return

        if char_count > 256:
            QMessageBox.warning(self, "Ошибка", "Превышен лимит символов (256)")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение отправки",
            f"Вы уверены, что хотите отправить заявление о страховом случае?\n\n"
            f"Полис: #{self.policy_id}\n"
            f"Длина описания: {char_count} символов",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.claim_submitted.emit(proofs_text)
            self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.proofs_input.setFocus()