import os
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox

from ui.login import LoginWindow
from ui.register import RegisterWindow
from ui.account import AccountWindow
from ui.policies import PoliciesWindow
from ui.insurer_policies import InsurerPoliciesWindow
from ui.policyholder_policies import PolicyholderPoliciesWindow
from ui.transactions import TransactionsWindow

from source.api import API
from source.utils import *
from source.types import User
from source.config import RPC_URL, CONTRACT_ADDRESS

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stacked_widget = QStackedWidget()

        self.api = None
        error = self.api_connect()
        if error is not None:
            QMessageBox.critical(
                None,
                "Ошибка подключения",
                f"{error}"
        )

        # Создаем все окна
        self.login_window = LoginWindow()
        self.register_window = RegisterWindow()
        self.account_window = AccountWindow()
        self.policies_window = PoliciesWindow(self.api)
        self.insurer_policies_window = InsurerPoliciesWindow(self.api)
        self.policyholder_policies_window = PolicyholderPoliciesWindow(self.api)
        self.transactions_window = TransactionsWindow(self.api)

        # Добавляем окна в стек
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.register_window)
        self.stacked_widget.addWidget(self.account_window)
        self.stacked_widget.addWidget(self.policies_window)
        self.stacked_widget.addWidget(self.insurer_policies_window)
        self.stacked_widget.addWidget(self.policyholder_policies_window)
        self.stacked_widget.addWidget(self.transactions_window)

        self.current_user = User(
            role="",
            address="",
            policies=[],
            transactions=[],
        )

        self.win_connect()

        self.stacked_widget.setFixedSize(1280, 800)
        self.stacked_widget.setWindowTitle("Insurance Platform")

        self.show_login()
# Настройки
    def api_connect(self):

        curr_dir = os.path.dirname(os.path.abspath(__file__))

        contract_abi = load_abi_from_file(curr_dir + "/source/insurance_abi.json")
        token_abi = load_abi_from_file(curr_dir + "/source/token_abi.json")

        if not contract_abi:
            return "Contract ABI not found"


        if not token_abi:
            return "Token ABI not found"

        try:
            self.api = API(RPC_URL, CONTRACT_ADDRESS, contract_abi, token_abi)
        except Exception as e:
            return e

    def win_connect(self):
        # LoginWindow
        self.login_window.register_clicked.connect(self.show_register)
        self.login_window.login_successful.connect(self.login_click)

        # RegisterWindow
        self.register_window.back_to_login_clicked.connect(self.show_login)
        self.register_window.registration_complete.connect(self.registration_click)

        # AccountWindow
        self.account_window.policies_clicked.connect(self.show_policies)
        self.account_window.transaction_history_clicked.connect(self.show_transactions)
        self.account_window.insurance_products_clicked.connect(self.show_insurance_products)
        self.account_window.logout_clicked.connect(self.logout)

        # PoliciesWindow
        self.policies_window.back_clicked.connect(self.show_account)
        self.policies_window.purchase_policy_clicked.connect(self.policies_window.policy_details_clicked)

        # InsurerPoliciesWindow
        self.insurer_policies_window.policy_details_clicked.connect(
            self.insurer_policies_window.policy_details_clicked)
        self.insurer_policies_window.back_clicked.connect(self.show_account)
        self.insurer_policies_window.add_policy_clicked.connect(
            self.insurer_policies_window.on_add_policy_clicked
        )

        # PolicyholderPoliciesWindow
        self.policyholder_policies_window.back_clicked.connect(self.show_account)

        # TransactionsWindow
        self.transactions_window.back_clicked.connect(self.show_account)

    # Основные окна
    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.login_window.clear_fields()

    def show_register(self):
        self.stacked_widget.setCurrentWidget(self.register_window)

    def show_account(self):
        balance = self.api.get_user_balance()
        self.account_window.set_user_info(
            role=self.current_user.role,
            address=self.current_user.address,
            balance=balance
        )
        self.stacked_widget.setCurrentWidget(self.account_window)

    def show_policies(self):
        self.policies_window.set_user_role(self.current_user.role)
        self.policies_window.load_policies()
        self.stacked_widget.setCurrentWidget(self.policies_window)

    def show_insurance_products(self):
        if self.current_user.role == "Страховщик":
            self.insurer_policies_window.load_policies()
            self.stacked_widget.setCurrentWidget(self.insurer_policies_window)
        else:
            self.policyholder_policies_window.load_policies()
            self.stacked_widget.setCurrentWidget(self.policyholder_policies_window)

    def show_transactions(self):
        try:
            self.transactions_window.load_transactions()
            self.stacked_widget.setCurrentWidget(self.transactions_window)
        except Exception as e:
            print(f"Ошибка при загрузке транзакций: {e}")
            QMessageBox.critical(self.stacked_widget, "Ошибка", f"Не удалось загрузить транзакции: {e}")


    def login_click(self, data):
        private_key = data['private_key']
        password = data['password']
        try:
            self.current_user = self.api.login(private_key=private_key, password=password)
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка входа",
                f"{e}"
            )
            self.current_user = User(
                role="",
                address="",
                policies=[],
                transactions=[],

            )
            self.login_window.clear_fields()
        self.show_account()
        self.stacked_widget.setCurrentWidget(self.account_window)

    def registration_click(self, registration_data):
        private_key = registration_data['private_key']
        password = registration_data['password']
        role = registration_data['role']
        try:
            self.current_user = self.api.registration(
                role=role,
                private_key=private_key,
                password=password
            )
        except Exception as e:
            QMessageBox.critical(
                None,
                "Ошибка регистрации",
                f"{e}"
            )
            self.current_user = User(
                role="",
                address="",
                policies=[],
                transactions=[],

            )
        self.show_account()
        self.stacked_widget.setCurrentWidget(self.account_window)

    def logout(self):
        self.current_user = User(
            role="",
            address="",
            policies=[],
            transactions=[],
        )
        self.api.logout()
        self.login_window.clear_fields()
        self.show_login()

    def run(self):
        self.stacked_widget.show()
        return self.app.exec()


if __name__ == "__main__":
    app = MainApp()
    sys.exit(app.run())