import sys
import os
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QHBoxLayout, QHeaderView, QApplication,
                             QScrollArea, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QFontDatabase

from ui.dialog import PolicyDialog, PremiumDialog
from source.utils import PolicyData, format_duration

class PoliciesWindow(QWidget):
    back_clicked = pyqtSignal()
    policy_details_clicked = pyqtSignal(int)
    create_policy_clicked = pyqtSignal(dict)
    purchase_policy_clicked = pyqtSignal(int)

    def __init__(self, api = None):
        super().__init__()
        self.api = api
        self.setWindowTitle("Страховые полисы")
        self.setFixedSize(1280, 800)
        self.load_fonts()
        self.init_ui()
        self.setup_connections()
        self.load_policies()
        self.current_user_role = None

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
        header_panel.setGeometry(32, 22, 1231, 76)
        header_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(18, 159, 73, 0.44);
                border-radius: 0px 0px 46px 46px;
                opacity: 0.89;
            }
        """)

        title_label = QLabel("Страховые полисы", main_frame)
        title_label.setGeometry(97, 22, 1136, 76)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_font = QFont()
        if "Inter" in self.fonts_loaded:
            title_font.setFamily(self.fonts_loaded["Inter"])
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

        self.scroll_area = QScrollArea(main_frame)
        self.scroll_area.setGeometry(40, 120, 1200, 650)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
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

        # Настройки таблицы
        self.table_container = QWidget()
        self.table_container.setStyleSheet("background-color: transparent;")

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Срок действия", "Действия"])

        self.table.setStyleSheet("""
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

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        self.table.setColumnWidth(0, 100)  # Ширина колонки ID

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Info
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Duration

        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Details
        self.table.setColumnWidth(3, 150)  # Ширина колонки с кнопкой

        self.table.verticalHeader().setDefaultSectionSize(65)
        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        table_font = QFont()
        if "Inter" in self.fonts_loaded:
            table_font.setFamily(self.fonts_loaded["Inter"])
        else:
            table_font.setFamily("Arial")
        table_font.setPointSize(16)
        self.table.setFont(table_font)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout = QVBoxLayout(self.table_container)
        layout.addWidget(self.table)
        layout.setContentsMargins(15, 15, 15, 15)

        self.table_container.setMinimumSize(QSize(1160, 600))

        self.scroll_area.setWidget(self.table_container)

    def setup_connections(self):
        self.back_button.clicked.connect(self.back_clicked.emit)

    def set_user_role(self, role):
        self.current_user_role = role

    def load_policies(self):
        try:
            policies_data = self.api.loadPolicies(PolicyData(
                    id=-1,
                    name="",
                    conditions="",
                    payoutAmount=-1,
                    durationWork=-1,
                    startDate=0,
                    endDate=0,
                    status="Доступен",
                    insurer="",
                    policyholder="",
                    sumDeposits=-1,
                    countOfPayout=-1,
                    proofs="",
            ))
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Ошибка загрузки данных:\n{e}"
            )
            policies_data = []

        if len(policies_data) == 0:
            self.table.setRowCount(1)

            id_item = QTableWidgetItem("0")
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, id_item)

            info_item = QTableWidgetItem("Нет доступных полисов")
            info_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, 1, info_item)

            space = QTableWidgetItem("—")
            space.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, 2, space)
            self.table.setItem(0, 3, space)
            self.table.resizeRowsToContents()
            return

        self.table.setRowCount(0)
        self.table.setRowCount(len(policies_data))

        for i in range(0, len(policies_data)):
            id = policies_data[i].id
            name = policies_data[i].name

            id_item = QTableWidgetItem(str(id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, id_item)

            # Название
            info_item = QTableWidgetItem(str(name))
            info_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 1, info_item)

            duration_text = format_duration(policies_data[i].durationWork)
            duration_item = QTableWidgetItem(duration_text)
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 2, duration_item)

            # Кнопка "Подробнее"
            details_button = QPushButton("Подробнее")
            details_button.setCursor(Qt.CursorShape.PointingHandCursor)

            # Шрифт для кнопки
            button_font = QFont()
            if "Inter" in self.fonts_loaded:
                button_font.setFamily(self.fonts_loaded["Inter"])
            else:
                button_font.setFamily("Arial")
            button_font.setPointSize(14)
            details_button.setFont(button_font)

            details_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(18, 159, 73, 0.7);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    padding: 8px 15px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: rgba(18, 159, 73, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(18, 159, 73, 1);
                    padding: 9px 14px 7px 16px;
                }
            """)

            details_button.setProperty("policy", policies_data[i])
            details_button.clicked.connect(self.on_details_clicked)

            self.table.setCellWidget(i, 3, details_button)

        self.table.resizeRowsToContents()

    def on_details_clicked(self):
        button = self.sender()
        if button:
            dialog = PolicyDialog(
                policy=button.property("policy"),
                user_role=self.current_user_role,
                parent=self
            )

            dialog.contract_requested.connect(self.on_contract_requested)

            dialog.exec()

    def on_contract_requested(self, policy_id):
        premium_dialog = PremiumDialog(
            policy_id=policy_id,
            min_premium=10.0,
            parent=self
        )

        premium_dialog.premium_submitted.connect(self.on_premium_submitted)

        premium_dialog.exec()

    def on_premium_submitted(self, policy_id, premium_amount):
        try:
            self.api.concludePolicy(policyId=policy_id, premium=int(premium_amount * 10**18))
            QMessageBox.information(
                self,
                "Успех",
                f"Премия {premium_amount} BLY успешно внесена!\nКонтракт заключен."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка!",
                f"Ошибка заключения контракта:\n{e}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoliciesWindow()
    window.show()

    sys.exit(app.exec())