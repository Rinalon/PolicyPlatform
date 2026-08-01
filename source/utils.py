import json
from dataclasses import dataclass
from datetime import datetime
from hexbytes import HexBytes

PolicyStatus = {
    0: "Доступен",
    1: "Активен",
    2: "Завершён",
    3: "Расторгнут",
    4: "На рассмотрении",
    5: "Ожидает расторжения",
}

IntToRole = {
    0: "Не зарегистрирован",
    1: "Страховщик",
    2: "Страхователь"
}

RoleEnum = {
    "Не зарегистрирован" : 0,
     "Страховщик" : 1,
     "Страхователь" : 2
}

TransactionType = {
    0: "Неизвестный статус",
    1: "Создание полиса",
    2: "Заключение полиса",
    3: "Внесение депозита",
    4: "Выплата",
    5: "Отказ",
    6: "Завершение",
    7: "Расторжение",
    8: "Запрос выплаты",
    9: "Запрос на расторжение"
}

@dataclass()
class Wallet:
    address: str
    private_key: HexBytes

@dataclass()
class PolicyData:
    id: int
    name: str
    conditions: str
    payoutAmount: int
    durationWork: int
    startDate: int
    endDate: int
    status: str
    insurer: str
    policyholder: str
    sumDeposits: int
    countOfPayout: int
    proofs: str

@dataclass()
class Transaction:
    transactionType: str
    addressFrom: str
    addressTo: str
    policyId: int
    amount: int
    unixTime: int

@dataclass()
class User:
    role: str
    policies: list[int]
    transactions: list[int]
    address: str

def load_abi_from_file(filepath: str):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ABI file {filepath} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}.")
        return []

def format_duration(duration_sec) -> str:
    durationDays = duration_sec // 86400
    years = durationDays // 365
    months = (durationDays % 365) // 30
    days = (durationDays % 365) % 30
    duration_parts = []
    if years > 0:
        if years == 1:
            years_text = "1 год"
        elif 2 <= years <= 4:
            years_text = f"{years} года"
        else:
            years_text = f"{years} лет"
        duration_parts.append(years_text)

    if months > 0:
        if months == 1:
            months_text = "1 месяц"
        elif 2 <= months <= 4:
            months_text = f"{months} месяца"
        else:
            months_text = f"{months} месяцев"
        duration_parts.append(months_text)

    if days > 0:
        if days == 1:
            days_text = "1 день"
        elif 2 <= days <= 4:
            days_text = f"{days} дня"
        else:
            days_text = f"{days} дней"
        duration_parts.append(days_text)
    return ", ".join(duration_parts)

def format_date(unix_time) -> str:
    if unix_time == 0:
        return "Не установлено"

    try:
        dt = datetime.fromtimestamp(unix_time)
        return dt.strftime("%d/%m/%Y")
    except Exception as e:
        return f"Ошибка даты: {e}"

def format_address(address) -> str:
    if not address or address == "0x0000000000000000000000000000000000000000":
        return "Не указан"

    if len(address) > 20:
        return f"{address[:10]}...{address[-8:]}"

    return address