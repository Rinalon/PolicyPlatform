from dataclasses import dataclass
from hexbytes import HexBytes
from typing import Dict, Any, Optional

PolicyStatus = {
    0: "Не существует",
    1: "Доступен",
    2: "Активен",
    3: "Завершён",
    4: "Расторгнут",
    5: "На рассмотрении",
    6: "Ожидает расторжения",
}

IntToRole = {
    0: "Не зарегистрирован",
    1: "Страховщик",
    2: "Страхователь"
}

@dataclass
class Wallet:
    address: str
    private_key: HexBytes

@dataclass
class PolicyData:
    startDate: int
    endDate: int
    durationWork: int
    countOfPayout: int
    hasPendingClaim: bool

    insurer: str
    policyholder: str
    payoutAmount: int
    sumDeposits: int

    name: str
    conditions: str
    status: str

@dataclass
class User:
    role: str
    policies: list[int]
    transactions: list[int]
    address: str

@dataclass
class Transaction:
    tx_hash: str
    block_number: int
    timestamp: int
    event_type: str
    policy_id: int
    from_address: str
    to_address: str
    amount: int
    data: Dict[str, Any]
