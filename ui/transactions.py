import os

from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QHBoxLayout, QHeaderView, QApplication,
                             QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QFontDatabase

from source.utils import Transaction, format_date, format_address

class TransactionsWindow(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, api):
        super().__init__()
        self.setWindowTitle("Мои транзакции")
        self.setFixedSize(1280, 800)
        self.load_fonts()
        self.init_ui()
        self.setup_connections()
        self.api = api
        self.load_transactions()

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

        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, 1280, 800)
        main_frame.setStyleSheet("background-color: rgba(189, 241, 202, 1);")

        # Шапка
        header_panel = QFrame(main_frame)
        header_panel.setGeometry(32, 22, 1231, 76)  # left: 32px, top: 22px
        header_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 159, 73, 0.44);
                border-radius: 0px 0px 46px 46px;
                opacity: 0.89;
            }
        """)

        title_label = QLabel("Транзакции", main_frame)
        title_label.setGeometry(97, 22, 1136, 76)  # left: 97px, top: 22px
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        if "Inter" in self.fonts_loaded:
            title_font.setFamily(self.fonts_loaded["Inter"])
        else:
            title_font.setFamily("Arial")
            print("Используется шрифт по умолчанию для заголовка")

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

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад", main_frame)
        self.back_button.setGeometry(50, 35, 120, 50)

        back_font = QFont()
        if "Inter" in self.fonts_loaded:
            back_font.setFamily(self.fonts_loaded["Inter"])
        else:
            back_font.setFamily("Arial")

        back_font.setPointSize(18)
        self.back_button.setFont(back_font)

        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(18, 159, 73, 0.8);
                border-radius: 12px;
                color: rgba(0, 0, 0, 1);
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.7);
            }
        """)

        scroll_area = QScrollArea(main_frame)
        scroll_area.setGeometry(40, 120, 1200, 650)  # left: 40px, top: 120px
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid rgba(18, 159, 73, 0.3);
                border-radius: 15px;
                background-color: rgba(255, 255, 255, 0.1);
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

        # Таблица
        self.table_container = QWidget()
        self.table_container.setStyleSheet("background-color: transparent;")

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(["Тип", "От кого", "Кому", "ID полиса", "Сумма", "Время"])

        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: none;
                border-radius: 15px;
                gridline-color: rgba(18, 159, 73, 0.3);
                alternate-background-color: rgba(189, 241, 202, 0.3);
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(80, 166, 163, 1);
            }
            QTableWidget::item:selected {
                background-color: rgba(80, 166, 163, 1);
                color: black;
            }
            QHeaderView::section {
                background-color: rgba(18, 159, 73, 0.7);
                color: white;
                padding: 12px;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                margin: 2px;
            }
        """)

        self.transactions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.transactions_table.setColumnWidth(0, 200)  # Type

        self.transactions_table.horizontalHeader().setSectionResizeMode(1,
                                                                        QHeaderView.ResizeMode.Stretch)  # Address From

        self.transactions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Address To

        self.transactions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Policy ID
        self.transactions_table.setColumnWidth(3, 120)

        self.transactions_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Amount
        self.transactions_table.setColumnWidth(4, 120)

        self.transactions_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Timestamp
        self.transactions_table.setColumnWidth(5, 120)


        self.transactions_table.verticalHeader().setDefaultSectionSize(55)
        self.transactions_table.verticalHeader().setVisible(False)

        self.transactions_table.setAlternatingRowColors(True)

        self.transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        table_font = QFont()
        if "Inter" in self.fonts_loaded:
            table_font.setFamily(self.fonts_loaded["Inter"])
        else:
            table_font.setFamily("Arial")
        table_font.setPointSize(14)
        self.transactions_table.setFont(table_font)

        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout = QVBoxLayout(self.table_container)
        layout.addWidget(self.transactions_table)
        layout.setContentsMargins(10, 10, 10, 10)

        self.table_container.setMinimumSize(QSize(1160, 600))
        scroll_area.setWidget(self.table_container)

    def setup_connections(self):
        self.back_button.clicked.connect(self.back_clicked.emit)

    def format_amount(self, amount):
        return f"{amount / 10**18:,} BLY"

    def load_transactions(self):
        try:
            transactions_data = self.api.loadTransactions()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Ошибка загрузки данных:\n{e}"
            )
            transactions_data = []

        if len(transactions_data) == 0:
            self.transactions_table.setRowCount(1)

            space = QTableWidgetItem("-")
            space.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(0, 0, space)
            self.transactions_table.setItem(0, 3, space)
            self.transactions_table.setItem(0, 4, space)
            self.transactions_table.setItem(0, 5, space)

            info_part1 = QTableWidgetItem("У вас пока ")
            info_part1.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(0, 1, info_part1)
            info_part2 = QTableWidgetItem("нет транзакций")
            info_part2.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(0, 2, info_part2)
            self.transactions_table.resizeRowsToContents()
            return

        self.transactions_table.setRowCount(0)
        self.transactions_table.setRowCount(len(transactions_data))

        for i in range(0, len(transactions_data)):
            type = QTableWidgetItem(transactions_data[i].transactionType)
            type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(i, 0, type)

            from_item = QTableWidgetItem(format_address(transactions_data[i].addressFrom))
            from_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(i, 1, from_item)

            to_item = QTableWidgetItem(format_address(transactions_data[i].addressTo))
            to_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(i, 2, to_item)

            policy_id = QTableWidgetItem(str(transactions_data[i].policyId))
            policy_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(i, 3, policy_id)

            amount = QTableWidgetItem(self.format_amount(transactions_data[i].amount))
            amount.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if transactions_data[i].transactionType == "Создание полиса":
                amount.setForeground(Qt.GlobalColor.black)
            elif transactions_data[i].addressFrom == self.api._session_wallet.address:
                # Исходящая транзакция - красный цвет
                amount.setForeground(Qt.GlobalColor.red)
            else:
                # Входящая транзакция - зеленый цвет
                amount.setForeground(Qt.GlobalColor.green)

            self.transactions_table.setItem(i, 4, amount)

            timestamp = QTableWidgetItem(format_date(transactions_data[i].unixTime))
            timestamp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(i, 5, timestamp)

        self.transactions_table.resizeRowsToContents()