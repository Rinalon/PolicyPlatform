import os
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QHBoxLayout, QHeaderView, QApplication,
                             QScrollArea, QTextEdit, QScrollBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QFontDatabase
from ui.dialog import AddedDialog, DetailsDialog
from source.utils import PolicyData, format_date

class InsurerPoliciesWindow(QWidget):
    back_clicked = pyqtSignal()
    policy_details_clicked = pyqtSignal(int)
    add_policy_clicked = pyqtSignal()

    def __init__(self, api):
        super().__init__()
        self.setWindowTitle("Мои полисы")
        self.setFixedSize(1280, 800)
        self.load_fonts()
        self.init_ui()
        self.setup_connections()
        self.api = api
        self.load_policies()

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

        title_label = QLabel("Мои полисы", main_frame)
        title_label.setGeometry(97, 22, 1136, 76)  # left: 97px, top: 22px
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

        # Область для скроллинга для таблицы
        scroll_area = QScrollArea(main_frame)
        scroll_area.setGeometry(40, 160, 1200, 500)
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

        self.table_container = QWidget()
        self.table_container.setStyleSheet("background-color: transparent;")

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Начало", "Окончание", "Статус", ""])

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
        self.table.setColumnWidth(0, 80)

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name

        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Start Date
        self.table.setColumnWidth(2, 120)

        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # End Date
        self.table.setColumnWidth(3, 150)

        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Status
        self.table.setColumnWidth(4, 150)

        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Details
        self.table.setColumnWidth(5, 120)

        self.table.verticalHeader().setDefaultSectionSize(200)
        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        table_font = QFont()
        if "Inter" in self.fonts_loaded:
            table_font.setFamily(self.fonts_loaded["Inter"])
        else:
            table_font.setFamily("Arial")
        table_font.setPointSize(15)
        self.table.setFont(table_font)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout = QVBoxLayout(self.table_container)
        layout.addWidget(self.table)
        layout.setContentsMargins(10, 10, 10, 10)

        self.table_container.setMinimumSize(QSize(1160, 500))

        scroll_area.setWidget(self.table_container)

        # Кнопка "Добавить полис"
        self.add_policy_button = QPushButton("Добавить полис", main_frame)
        self.add_policy_button.setGeometry(940, 670, 300, 60)

        add_button_font = QFont()
        if "Inter" in self.fonts_loaded:
            add_button_font.setFamily(self.fonts_loaded["Inter"])
        else:
            add_button_font.setFamily("Arial")

        add_button_font.setPointSize(18)
        add_button_font.setWeight(600)
        self.add_policy_button.setFont(add_button_font)

        self.add_policy_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(18, 159, 73, 0.8);
                border: none;
                border-radius: 12px;
                color: white;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(18, 159, 73, 1);
            }
            QPushButton:pressed {
                background-color: rgba(18, 159, 73, 0.9);
                padding: 11px 9px 9px 11px;
            }
        """)

    def setup_connections(self):
        self.back_button.clicked.connect(self.back_clicked.emit)
        self.add_policy_button.clicked.connect(self.add_policy_clicked.emit)

    def load_policies(self):
        try:
            if self.api._session_wallet.address != "0x00000000000000000000000000000":
                policies_data = self.api.loadPolicies(PolicyData(
                        id=-1,
                        name="",
                        conditions="",
                        payoutAmount=-1,
                        durationWork=-1,
                        startDate=0,
                        endDate=0,
                        status="",
                        insurer=self.api._session_wallet.address,
                        policyholder="",
                        sumDeposits=-1,
                        countOfPayout=-1,
                        proofs="",
                ))
            else:
                policies_data = []
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

            info_item = QTableWidgetItem("У вас пока нет полисов")
            info_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, 1, info_item)

            space = QTableWidgetItem("—")
            space.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, 2, space)
            self.table.setItem(0, 3, space)
            self.table.setItem(0, 4, space)
            self.table.resizeRowsToContents()
            return

        self.table.setRowCount(0)
        self.table.setRowCount(len(policies_data))

        for i in range(0, len(policies_data)):
            id = QTableWidgetItem(str(policies_data[i].id))
            id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, id)

            name = QTableWidgetItem(policies_data[i].name)
            name.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 1, name)

            if policies_data[i].status == "Доступен":
                start_item = QTableWidgetItem("—")
            else:
                start_item = QTableWidgetItem(format_date(policies_data[i].startDate))
            start_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, start_item)

            if policies_data[i].status == "Доступен":
                end_item = QTableWidgetItem("—")
            else:
                end_item = QTableWidgetItem(format_date(policies_data[i].endDate))
            end_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, end_item)

            # Статус
            status = QTableWidgetItem(policies_data[i].status)
            status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Цвет статуса
            if policies_data[i].status == "Активен":
                status.setBackground(Qt.GlobalColor.white)
                status.setForeground(Qt.GlobalColor.darkGreen)
            elif policies_data[i].status == "Завершен" or policies_data[i].status == "Расторгнут":
                status.setBackground(Qt.GlobalColor.white)
                status.setForeground(Qt.GlobalColor.gray)
            elif policies_data[i].status == "На рассмотрении" or policies_data[i].status == "Ожидает расторжения":
                status.setBackground(Qt.GlobalColor.white)
                status.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(i, 4, status)

            details_button = QPushButton("Детали")
            details_button.setCursor(Qt.CursorShape.PointingHandCursor)

            button_font = QFont()
            if "Inter" in self.fonts_loaded:
                button_font.setFamily(self.fonts_loaded["Inter"])
            else:
                button_font.setFamily("Arial")
            button_font.setPointSize(13)
            details_button.setFont(button_font)

            details_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(18, 159, 73, 0.7);
                    border: none;
                    border-radius: 6px;
                    color: white;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: rgba(18, 159, 73, 0.9);
                }
                QPushButton:pressed {
                    background-color: rgba(18, 159, 73, 1);
                    padding: 7px 11px 5px 13px;
                }
            """)

            details_button.setProperty("policy", policies_data[i])
            details_button.clicked.connect(self.on_details_clicked)

            self.table.setCellWidget(i, 5, details_button)

        self.table.resizeRowsToContents()

    def on_details_clicked(self):
        button = self.sender()
        if button:
            policy = button.property("policy")
            button_func = {
                'terminate': self.terminate_policy,
                'approve': self.approve_payout,
                'reject': self.reject_payout,
            }
            dialog = DetailsDialog(
                policy = policy,
                user_role ="Страховщик",
                button_func=button_func,
                parent = self
            )

            dialog.exec()

    def approve_payout(self, policy_id):
        reply = QMessageBox.question(
            self,
            "Подтверждение выплаты",
            f"Вы уверены, что хотите выплатить страховое возмещение по полису #{policy_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api.approved(policyId=policy_id)
                QMessageBox.information(
                    self,
                    "Успех!",
                    "Страховое возмещение отправлено страхователю"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка!",
                    f"Ошибка перевода:\n{e}"
                )

    def reject_payout(self, policy_id):
        reply = QMessageBox.question(
            self,
            "Подтверждение отверждения",
            f"Вы уверены, что страхователь предоставил недостаточно\nдоказательств страхового случая по полису #{policy_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api.rejected(policyId=policy_id)
                QMessageBox.information(
                    self,
                    "Успех!",
                    "Отказ в страховой выплате прошёл успешно."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка!",
                    f"Ошибка отверждения:\n{e}"
                )

    def terminate_policy(self, policy_id):

        reply = QMessageBox.question(
            self,
            "Подтверждение расторжения",
            f"Вы уверены, что хотите расторгнуть полис #{policy_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api.terminatePolicy(policyId=policy_id)
                QMessageBox.information(
                    self,
                    "Полис расторгнут",
                    f"Полис #{policy_id} успешно расторгнут"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка!",
                    f"Ошибка расторжения:\n{e}"
                )

    def on_add_policy_clicked(self):
        dialog = AddedDialog(parent=self)

        dialog.policy_data_submitted.connect(self.create_policy)

        dialog.exec()

    def create_policy(self, policy_data):
        try:
            self.api.createPolicy(
                name=policy_data['name'],
                conditions=policy_data['conditions'],
                payoutAmount=int(policy_data['payout_amount'] * 10**18),
                durationWork=policy_data['duration'],
                countOfPayout=policy_data['payout_count']
            )
            QMessageBox.information(
                self,
                "Успешное создание полиса!",
                f"Полис \"{policy_data['name']}\" создан."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка!",
                f"Ошибка создания полиса:\n{e}"
            )