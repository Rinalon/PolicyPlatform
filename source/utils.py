import json
from datetime import datetime

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