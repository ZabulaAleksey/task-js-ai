#!/usr/bin/env python3
"""Проверка финансовых REST/JSON/JSONL payload и выпуск backend-отчёта."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

DECIMAL_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
CURRENCY_RE = re.compile(r"^[A-Za-z]{3}$")
FX_RE = re.compile(r"^[A-Za-z]{6}$")
CURRENCY_KEYS = {"currency", "base", "basecurrency", "quotecurrency", "settlementcurrency"}
DECIMAL_KEYS = {
    "amount", "rate", "bid", "ask", "open", "high", "low", "close",
    "volume", "available", "reserved", "convertedusd", "changepercent",
}
TIMESTAMP_KEYS = {"timestamp", "servertime", "publishedat", "scheduledat"}
SENSITIVE_RE = re.compile(r"(authorization|cookie|token|secret|password|api[-_]?key)", re.I)
ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_RU = {
    "critical": "Критический", "high": "Высокий", "medium": "Средний",
    "low": "Низкий", "info": "Инфо",
}


@dataclass
class Finding:
    id: str
    severity: str
    kind: str
    code: str
    path: str
    summary: str
    observed: str
    expected: str
    risk: str
    recommendation: str


class InputError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def safe_value(value: Any, key: str = "") -> str:
    if SENSITIVE_RE.search(key):
        return "[REDACTED]"
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    if isinstance(value, str):
        text = re.sub(r"\s+", " ", value).strip()
        return text[:117] + "..." if len(text) > 120 else text
    if isinstance(value, list):
        return f"array[{len(value)}]"
    if isinstance(value, dict):
        return f"object{{{len(value)} fields}}"
    return type(value).__name__


def child_path(parent: str, key: Any) -> str:
    if isinstance(key, int):
        return f"{parent}[{key}]"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(key)):
        return f"{parent}.{key}"
    escaped = str(key).replace("\\", "\\\\").replace("'", "\\'")
    return f"{parent}['{escaped}']"


def clean_url(value: str) -> str:
    parts = urlsplit(value)
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def load_codes(path: Path) -> tuple[set[str], str | None]:
    codes: set[str] = set()
    snapshot = None
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text.lower().startswith("# snapshot:"):
            snapshot = text.split(":", 1)[1].strip()
        elif text and not text.startswith("#"):
            codes.update(token.upper() for token in text.split())
    if not codes:
        raise InputError("reference.empty", f"В {path} нет ISO-кодов")
    return codes, snapshot


def auth_headers(env_name: str | None) -> dict[str, str]:
    if not env_name:
        return {}
    raw = os.environ.get(env_name)
    if raw is None:
        raise InputError("input.headers_env_missing", f"Нет env {env_name}")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise InputError("input.headers_env_invalid", f"{env_name}: {error.msg}") from error
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    ):
        raise InputError("input.headers_env_invalid", f"{env_name} должен быть JSON string map")
    return value


def load_payload(args: argparse.Namespace) -> tuple[Any, dict[str, Any]]:
    started = time.perf_counter()
    if args.url:
        request = Request(
            args.url,
            headers={
                "Accept": "application/json, application/x-ndjson",
                "User-Agent": "audit-financial-api/1.0",
                **auth_headers(args.headers_env),
            },
        )
        try:
            with urlopen(request, timeout=args.timeout_seconds) as response:
                body = response.read(args.max_bytes + 1)
                status = response.status
                content_type = response.headers.get("content-type", "")
                cache_control = response.headers.get("cache-control", "")
                source = response.geturl()
        except HTTPError as error:
            body = error.read(args.max_bytes + 1)
            status = error.code
            content_type = error.headers.get("content-type", "")
            cache_control = error.headers.get("cache-control", "")
            source = error.geturl()
        except URLError as error:
            raise InputError("http.unreachable", str(error.reason)) from error
        meta = {
            "source_type": "url", "source": clean_url(source), "http_status": status,
            "content_type": content_type, "cache_control": cache_control,
        }
    else:
        path = Path(args.input).resolve()
        body = path.read_bytes()
        meta = {
            "source_type": "file", "source": str(path), "http_status": None,
            "content_type": "application/x-ndjson" if path.suffix.lower() == ".jsonl"
            else "application/json", "cache_control": "",
        }

    meta["payload_bytes"] = len(body)
    meta["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 1)
    if len(body) > args.max_bytes:
        raise InputError("input.too_large", f"Payload больше {args.max_bytes} bytes")
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise InputError("json.encoding", "Payload не является UTF-8") from error

    is_jsonl = "ndjson" in meta["content_type"].lower() or (
        args.input and Path(args.input).suffix.lower() == ".jsonl"
    )
    try:
        if is_jsonl:
            payload = [json.loads(line) for line in text.splitlines() if line.strip()]
            meta["document_format"] = "jsonl"
            meta["record_count"] = len(payload)
        else:
            payload = json.loads(text)
            meta["document_format"] = "json"
            meta["record_count"] = len(payload) if isinstance(payload, list) else 1
    except json.JSONDecodeError as error:
        raise InputError(
            "json.invalid",
            f"JSON line {error.lineno}, column {error.colno}: {error.msg}",
        ) from error
    return payload, meta


class Auditor:
    def __init__(self, codes: set[str], allowed: set[str], profile: str, stale_days: int):
        self.codes = codes
        self.allowed = allowed
        self.profile = profile
        self.stale_days = stale_days
        self.findings: list[Finding] = []
        self.dedupe: set[tuple[str, str]] = set()
        self.seen_codes: set[str] = set()
        self.objects = 0
        self.arrays = 0
        self.decimals = 0

    def add(
        self, severity: str, kind: str, code: str, path: str, summary: str,
        observed: Any, expected: str, risk: str, recommendation: str,
    ) -> None:
        marker = (code, path)
        if marker in self.dedupe:
            return
        self.dedupe.add(marker)
        self.findings.append(Finding(
            "", severity, kind, code, path, summary, safe_value(observed, path),
            expected, risk, recommendation,
        ))

    def currency(self, value: Any, path: str) -> str | None:
        if not isinstance(value, str):
            self.add(
                "high", "payload", "currency.type", path,
                "Код валюты имеет неверный тип", value, "Строка из трёх букв",
                "Клиент не сможет однозначно обработать валюту",
                "Возвращать строковый код и валидировать его до ответа",
            )
            return None
        trimmed = value.strip()
        if trimmed != value:
            self.add(
                "medium", "payload", "currency.whitespace", path,
                "В коде валюты есть внешние пробелы", value,
                "Канонический код без пробелов",
                "Нормализация в разных клиентах даст разные ключи",
                "Удалить пробелы на сервере до сериализации",
            )
        if not CURRENCY_RE.fullmatch(trimmed):
            self.add(
                "high", "payload", "currency.format", path,
                "Код валюты не соответствует формату ISO 4217", value,
                "Ровно три латинские буквы",
                "Связанные курсы и форматирование могут не разрешиться",
                "Исправить mapping и отклонять неверный формат",
            )
            return None
        normalized = trimmed.upper()
        self.seen_codes.add(normalized)
        if trimmed != normalized:
            self.add(
                "medium", "payload", "currency.case", path,
                "Код валюты возвращён не в верхнем регистре", value,
                "Канонический uppercase ISO 4217 код",
                "После нормализации возможны дубликаты и расхождения ключей",
                "Сериализовать uppercase-код на сервере",
            )
        if normalized not in self.codes and normalized not in self.allowed:
            self.add(
                "high", "payload", "currency.not_active", path,
                "Код отсутствует в текущем ISO 4217 и allowlist", normalized,
                "Активный ISO 4217 код или документированный разрешённый актив",
                "Сумма или курс могут быть отнесены к несуществующей валюте",
                "Исправить upstream mapping либо документировать актив в allowlist",
            )
        if normalized in {"XXX", "XTS"}:
            self.add(
                "medium", "payload", "currency.sentinel", path,
                "Использован специальный ISO-код вместо расчётной валюты", normalized,
                "Реальная расчётная валюта",
                "Итоги нельзя корректно форматировать или конвертировать",
                "Использовать специальный код только в документированном контексте",
            )
        return normalized

    def decimal(self, value: Any, path: str, positive: bool = False) -> Decimal | None:
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            self.add(
                "high", "payload", "decimal.type", path,
                "Финансовое значение имеет неподдерживаемый тип", value,
                "Десятичная строка", "Расчёт может завершиться ошибкой",
                "Возвращать decimal строкой без экспоненты",
            )
            return None
        if isinstance(value, (int, float)):
            self.add(
                "medium", "payload", "decimal.json_number", path,
                "Финансовое значение передано JSON-числом",
                f"{type(value).__name__} (value redacted)", "Десятичная строка",
                "IEEE-754 может изменить точное денежное значение",
                "Сериализовать суммы и курсы строками",
            )
        raw = str(value)
        if len(raw) > 64 or not DECIMAL_RE.fullmatch(raw):
            self.add(
                "high", "payload", "decimal.format", path,
                "Значение не является канонической decimal-строкой",
                f"{type(value).__name__} format", "Не более 64 символов: -?digits[.digits]",
                "Парсинг и точный расчёт могут расходиться",
                "Нормализовать decimal и запретить NaN/Infinity/экспоненту",
            )
            return None
        try:
            parsed = Decimal(raw)
        except InvalidOperation:
            return None
        self.decimals += 1
        if positive and parsed <= 0:
            self.add(
                "high", "payload", "rate.non_positive", path,
                "Курс не является положительным", "non-positive decimal",
                "Значение строго больше нуля",
                "Конвертация даст ошибку деления или неверный итог",
                "Не публиковать нулевые и отрицательные курсы",
            )
        return parsed

    def rates(self, value: Any, path: str) -> None:
        if not isinstance(value, dict):
            self.add(
                "high", "payload", "rates.type", path,
                "Таблица курсов не является объектом", value,
                "Объект code -> positive decimal string",
                "Клиент не сможет найти курс по валюте",
                "Возвращать объект с валютными ключами",
            )
            return
        normalized: dict[str, list[str]] = {}
        for key, rate in value.items():
            key_path = child_path(path, key)
            code = self.currency(key, key_path + "#key")
            if code:
                normalized.setdefault(code, []).append(key)
            self.decimal(rate, key_path, positive=True)
        for keys in normalized.values():
            if len(keys) > 1:
                self.add(
                    "high", "payload", "rates.normalized_collision", path,
                    "Ключи курсов совпадают после нормализации", ", ".join(keys),
                    "Один канонический ключ на валюту",
                    "Один курс может незаметно перезаписать другой",
                    "Дедуплицировать ключи после uppercase/trim",
                )

    def symbol(self, value: Any, path: str) -> None:
        if not isinstance(value, str) or not FX_RE.fullmatch(value.strip()):
            if self.profile == "realtime":
                self.add(
                    "high", "payload", "symbol.format", path,
                    "FX-символ имеет неверный формат", value,
                    "Шесть латинских букв: BASEQUOTE",
                    "Котировка не связана с валютной парой",
                    "Возвращать канонический шестибуквенный символ",
                )
            return
        symbol = value.strip()
        if symbol != symbol.upper():
            self.add(
                "medium", "payload", "symbol.case", path,
                "FX-символ возвращён не в верхнем регистре", value,
                "Uppercase BASEQUOTE", "Подписки и state-ключи могут разойтись",
                "Нормализовать символ на сервере",
            )
        self.currency(symbol[:3], path + "#base")
        self.currency(symbol[3:], path + "#quote")

    def api_date(self, value: Any, path: str) -> None:
        if not isinstance(value, str):
            self.add(
                "high", "payload", "date.type", path, "Дата имеет неверный тип",
                value, "YYYY-MM-DD", "Выбор курсов по дате неоднозначен",
                "Возвращать календарную дату ISO 8601",
            )
            return
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            self.add(
                "high", "payload", "date.invalid", path,
                "Дата не является корректной ISO-датой", value, "YYYY-MM-DD",
                "Курс может быть привязан к неверному дню",
                "Исправить дату и timezone-правило upstream",
            )
            return
        if value != parsed.isoformat():
            self.add(
                "medium", "payload", "date.non_canonical", path,
                "Дата сериализована неканонически", value, parsed.isoformat(),
                "Строковое сравнение и cache keys могут расходиться",
                "Сериализовать дату как YYYY-MM-DD",
            )
        age = (datetime.now(timezone.utc).date() - parsed).days
        if age > self.stale_days:
            self.add(
                "medium", "payload", "date.stale", path,
                "Дата финансовых данных устарела", value,
                f"Не старше {self.stale_days} дней",
                "Портфель может использовать устаревшие курсы",
                "Обновить источник и публиковать retrieval timestamp",
            )
        if age < -1:
            self.add(
                "high", "payload", "date.future", path,
                "Дата финансовых данных находится в будущем", value,
                "Не позже следующего UTC-дня",
                "Возможна ошибка timezone или неверный набор курсов",
                "Исправить timezone и источник даты",
            )

    def timestamp(self, value: Any, path: str) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            self.add(
                "high", "payload", "timestamp.type", path,
                "Timestamp имеет неверный тип", value,
                "Целое число Unix milliseconds",
                "Порядок и свежесть событий нельзя определить",
                "Возвращать integer milliseconds",
            )
            return
        if not math.isfinite(value) or int(value) != value:
            self.add(
                "high", "payload", "timestamp.non_integer", path,
                "Timestamp не является конечным integer", value,
                "Целое число Unix milliseconds",
                "Событие может сортироваться неверно",
                "Сериализовать timestamp целым числом",
            )
            return
        if value < 1_000_000_000_000:
            self.add(
                "high", "payload", "timestamp.seconds", path,
                "Timestamp похож на seconds вместо milliseconds", value,
                "Unix milliseconds",
                "Клиент интерпретирует дату примерно как 1970 год",
                "Конвертировать seconds в milliseconds в adapter",
            )
            return
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        if value < 946_684_800_000 or value > now_ms + 5 * 366 * 86_400_000:
            self.add(
                "high", "payload", "timestamp.range", path,
                "Timestamp вне допустимого диапазона", value,
                "2000-01-01 .. now+5y",
                "Событие нарушит сортировку и stale-check",
                "Исправить единицы и clock source",
            )

    def invariants(self, obj: dict[str, Any], path: str) -> set[str]:
        handled: set[str] = set()
        if "bid" in obj and "ask" in obj:
            bid = self.decimal(obj["bid"], child_path(path, "bid"))
            ask = self.decimal(obj["ask"], child_path(path, "ask"))
            handled.update({"bid", "ask"})
            if bid is not None and ask is not None and ask < bid:
                self.add(
                    "high", "payload", "quote.crossed", child_path(path, "ask"),
                    "Ask ниже bid", "crossed quote", "ask >= bid",
                    "Спред и оценка позиции будут неверными",
                    "Отклонять crossed quote на серверной границе",
                )
        candle = {"open", "high", "low", "close"}
        if candle.issubset(obj):
            values = {key: self.decimal(obj[key], child_path(path, key)) for key in candle}
            handled.update(candle)
            if all(item is not None for item in values.values()):
                high, low = values["high"], values["low"]
                assert high is not None and low is not None
                if high < max(values["open"], values["close"], low):
                    self.add(
                        "high", "payload", "candle.high", child_path(path, "high"),
                        "High ниже одного из OHLC-значений", "OHLC invariant violated",
                        "high >= open, close, low",
                        "Свеча и индикаторы будут искажены",
                        "Проверять OHLC до публикации",
                    )
                if low > min(values["open"], values["close"], high):
                    self.add(
                        "high", "payload", "candle.low", child_path(path, "low"),
                        "Low выше одного из OHLC-значений", "OHLC invariant violated",
                        "low <= open, close, high",
                        "Свеча и индикаторы будут искажены",
                        "Проверять OHLC до публикации",
                    )
        return handled

    def walk(self, value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            self.objects += 1
            handled = self.invariants(value, path)
            for key, child in value.items():
                next_path = child_path(path, key)
                normalized = key.lower()
                if normalized == "rates":
                    self.rates(child, next_path)
                    continue
                if normalized in CURRENCY_KEYS:
                    self.currency(child, next_path)
                elif normalized == "currencies" and isinstance(child, list):
                    for index, code in enumerate(child):
                        self.currency(code, child_path(next_path, index))
                elif normalized == "symbol":
                    self.symbol(child, next_path)
                elif normalized == "date":
                    self.api_date(child, next_path)
                elif normalized in TIMESTAMP_KEYS:
                    self.timestamp(child, next_path)
                elif normalized in DECIMAL_KEYS and key not in handled:
                    self.decimal(child, next_path)
                self.walk(child, next_path)
        elif isinstance(value, list):
            self.arrays += 1
            for index, child in enumerate(value):
                self.walk(child, child_path(path, index))

    def sequence(self, payload: Any) -> None:
        records = payload if isinstance(payload, list) else [payload]
        previous: int | None = None
        for index, record in enumerate(records):
            if not isinstance(record, dict) or "sequence" not in record:
                continue
            sequence = record["sequence"]
            path = f"$[{index}].sequence" if isinstance(payload, list) else "$.sequence"
            if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
                self.add(
                    "high", "payload", "sequence.invalid", path,
                    "Sequence не является неотрицательным integer", sequence,
                    "Неотрицательное монотонное целое",
                    "Порядок событий невозможно гарантировать",
                    "Исправить генератор sequence на сервере",
                )
                continue
            if previous is not None and sequence <= previous:
                self.add(
                    "high", "payload", "sequence.regression", path,
                    "Sequence повторился или уменьшился", sequence,
                    f"Значение больше {previous}",
                    "Клиент отбросит событие как устаревшее",
                    "Гарантировать монотонность в рамках подписки",
                )
            previous = sequence

    def svelte_portfolio(self, payload: Any, meta: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            self.add(
                "critical", "payload", "portfolio.root", "$",
                "Корень portfolio API не является объектом", payload,
                "Объект financeResult + currencyData",
                "Клиент не сможет загрузить портфель",
                "Вернуть документированную корневую структуру",
            )
            return
        result = payload.get("financeResult")
        currency_data = payload.get("currencyData")
        if not isinstance(result, list) or len(result) != 2:
            self.add(
                "high", "payload", "portfolio.finance_result_shape", "$.financeResult",
                "financeResult не является tuple из двух источников", result,
                "Массив ровно из двух элементов",
                "Расчёт не сможет сопоставить источники",
                "Стабилизировать форму агрегированного ответа",
            )
            return
        if not isinstance(currency_data, dict):
            return
        base_raw = currency_data.get("base")
        base = base_raw.strip().upper() if isinstance(base_raw, str) else None
        rates_raw = currency_data.get("rates")
        rates = rates_raw if isinstance(rates_raw, dict) else {}
        normalized_rates = {str(key).strip().upper(): value for key, value in rates.items()}
        used: set[str] = set()
        first, second = result
        if isinstance(first, dict) and isinstance(first.get("transactions"), list):
            for item in first["transactions"]:
                if isinstance(item, dict) and isinstance(item.get("currency"), str):
                    used.add(item["currency"].strip().upper())
        if isinstance(second, list):
            object_rows = 0
            for item in second:
                if isinstance(item, dict):
                    object_rows += 1
                    if isinstance(item.get("currency"), str):
                        used.add(item["currency"].strip().upper())
                elif isinstance(item, str):
                    match = re.search(r"([A-Za-z]{3})\s*$", item)
                    if match:
                        used.add(match.group(1).upper())
            if object_rows:
                self.add(
                    "medium", "contract", "contract.normalized_output_schema",
                    "$.financeResult[1]",
                    "REST отдаёт нормализованные объекты, а upstream-схема принимает строки",
                    f"{object_rows} normalized object rows",
                    "Отдельная response schema либо документированная bidirectional schema",
                    "Повторная валидация ответа той же схемой завершится ошибкой",
                    "Добавить financeDataResponseSchema для нормализованного ответа",
                )
        for code in sorted(used):
            if code != base and code not in normalized_rates:
                self.add(
                    "high", "payload", "rates.missing", "$.currencyData.rates",
                    "Для использованной валюты отсутствует курс", code,
                    "Положительный курс для каждой небазовой валюты",
                    "Расчёт завершится ошибкой или даст пустой итог",
                    "Добавить курс или удалить несогласованную запись",
                )
        if base:
            if base not in normalized_rates:
                self.add(
                    "low", "contract", "rates.base_missing", "$.currencyData.rates",
                    "Базовая валюта отсутствует в rates", base,
                    "Явный курс base = 1",
                    "Контракт сложнее сравнивать между provider-ами",
                    "Добавить явный курс базовой валюты",
                )
            else:
                try:
                    if Decimal(str(normalized_rates[base])) != Decimal("1"):
                        self.add(
                            "high", "payload", "rates.base_not_one",
                            child_path("$.currencyData.rates", base),
                            "Курс базовой валюты не равен 1", "non-unit base rate", "1",
                            "Все конверсии будут систематически искажены",
                            "Исправить provider mapping для base rate",
                        )
                except InvalidOperation:
                    pass
        if meta.get("source_type") == "url" and "no-store" not in str(
            meta.get("cache_control", "")
        ).lower():
            self.add(
                "high", "http", "http.cache_control",
                "$response.headers.cache-control",
                "Финансовый ответ допускает кеширование",
                meta.get("cache_control") or "(missing)", "Cache-Control: no-store",
                "Данные портфеля могут сохраниться в промежуточном кеше",
                "Добавить no-store на endpoint",
            )

    def project_contract(self, root: Path) -> None:
        finance = root / "src/lib/schemas/finance.ts"
        realtime = root / "src/lib/schemas/realtime.ts"
        if finance.exists():
            text = finance.read_text(encoding="utf-8")
            if ".toUpperCase()" in text:
                self.add(
                    "medium", "contract", "contract.case_normalized_silently",
                    "src/lib/schemas/finance.ts:currencyCodeSchema",
                    "Клиентская схема молча исправляет регистр валюты",
                    ".toUpperCase() before validation",
                    "Backend возвращает uppercase, отклонения наблюдаемы",
                    "Ошибки регистра сервера скрываются от мониторинга",
                    "Проверять raw payload до transform и исправить backend serialization",
                )
            if "currencyCodeSchema" in text and "ISO 4217" not in text:
                self.add(
                    "medium", "contract", "contract.currency_membership_unchecked",
                    "src/lib/schemas/finance.ts:currencyCodeSchema",
                    "Схема проверяет форму кода, но не существование валюты",
                    "/^[A-Z]{3}$/ after normalization",
                    "Активный ISO 4217 код или allowlist",
                    "Код ZZZ пройдёт границу и сломает обработку позже",
                    "Добавить membership-проверку на backend и frontend boundary",
                )
        if realtime.exists():
            text = realtime.read_text(encoding="utf-8")
            if "regex(/^[A-Z]{3}$/" in text and "ISO 4217" not in text:
                self.add(
                    "medium", "contract",
                    "contract.realtime_currency_membership_unchecked",
                    "src/lib/schemas/realtime.ts",
                    "Realtime-схема принимает любой uppercase код из трёх букв",
                    "/^[A-Z]{3}$/", "Активный ISO 4217 код или allowlist",
                    "Несуществующая валюта попадёт в balances/news/calendar",
                    "Синхронизировать ISO/allowlist-проверку с REST",
                )

    def finish(self) -> None:
        self.findings.sort(
            key=lambda item: (ORDER[item.severity], item.kind, item.code, item.path)
        )
        for index, item in enumerate(self.findings, 1):
            item.id = f"F-{index:03d}"


def transport(meta: dict[str, Any], auditor: Auditor) -> None:
    status = meta.get("http_status")
    if status is not None and not 200 <= status < 300:
        auditor.add(
            "critical", "http", "http.status", "$response.status",
            "HTTP endpoint вернул ошибочный статус", status, "2xx",
            "Payload может быть сообщением об ошибке вместо финансовых данных",
            "Исправить endpoint и повторить аудит ответа 2xx",
        )
    content_type = str(meta.get("content_type", "")).lower()
    if meta.get("source_type") == "url" and not (
        "application/json" in content_type or "ndjson" in content_type
    ):
        auditor.add(
            "high", "http", "http.content_type",
            "$response.headers.content-type", "Ответ не объявлен JSON",
            content_type or "(missing)", "application/json или application/x-ndjson",
            "Прокси и клиенты могут неверно обработать ответ",
            "Установить корректный Content-Type",
        )


def decision(counts: Counter[str]) -> tuple[str, str]:
    if counts["critical"] or counts["high"]:
        return "STOP", "Не передавать контракт в production до устранения high/critical."
    if counts["medium"]:
        return "REVIEW", "Payload пригоден для demo, но контракт требует согласования до production."
    return "PASS", "Блокирующих проблем в проверенном срезе не обнаружено."


def build_report(
    auditor: Auditor, meta: dict[str, Any], args: argparse.Namespace,
    snapshot: str | None, error: str | None,
) -> dict[str, Any]:
    counts = Counter(item.severity for item in auditor.findings)
    status, status_text = decision(counts)
    limitations: list[str] = []
    if args.profile == "svelte-portfolio":
        limitations.append(
            "Production realtime-provider не проверен: запуск охватывает REST и статические схемы."
        )
    if meta.get("source_type") == "file":
        limitations.append("Для файлового capture не проверены HTTP-заголовки и доступность endpoint.")
    if snapshot:
        limitations.append(f"Currency membership использует offline ISO 4217 snapshot от {snapshot}.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": args.title,
        "profile": args.profile,
        "decision": status,
        "decision_text": status_text,
        "source": meta,
        "summary": {
            "total_findings": len(auditor.findings),
            "by_severity": {
                level: counts[level]
                for level in ["critical", "high", "medium", "low", "info"]
            },
            "currency_codes_seen": sorted(auditor.seen_codes),
            "objects_checked": auditor.objects,
            "arrays_checked": auditor.arrays,
            "decimal_fields_checked": auditor.decimals,
        },
        "findings": [asdict(item) for item in auditor.findings],
        "limitations": limitations,
        "operational_error": error,
        "references": [
            {
                "title": "SIX - ISO 4217 Maintenance Agency",
                "url": "https://www.six-group.com/en/products-services/financial-information/market-reference-data/data-standards.html",
            },
            {
                "title": "ISO 4217 currency codes",
                "url": "https://www.iso.org/iso-4217-currency-codes.html",
            },
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    tick = chr(96)
    source, summary = report["source"], report["summary"]
    counts = summary["by_severity"]
    lines = [
        f"# {report['title']}", "",
        f"**Решение: {report['decision']}** - {report['decision_text']}", "",
        f"- Сформирован: {report['generated_at']}",
        f"- Профиль: {tick}{report['profile']}{tick}",
        f"- Источник: {tick}{source.get('source', 'unavailable')}{tick}",
        f"- Формат: {tick}{source.get('document_format', 'unknown')}{tick}",
        f"- Размер: {source.get('payload_bytes', 0)} bytes",
    ]
    if source.get("http_status") is not None:
        lines += [
            f"- HTTP: {source['http_status']}; Content-Type: "
            f"{tick}{source.get('content_type') or '(missing)'}{tick}",
            f"- Cache-Control: {tick}{source.get('cache_control') or '(missing)'}{tick}",
        ]
    lines += [
        "", "## Краткая сводка", "",
        "| Critical | High | Medium | Low | Total |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| {counts['critical']} | {counts['high']} | {counts['medium']} | "
        f"{counts['low']} | {summary['total_findings']} |", "",
        f"Проверено объектов: {summary['objects_checked']}; массивов: "
        f"{summary['arrays_checked']}; decimal-полей: {summary['decimal_fields_checked']}. "
        f"Коды валют/активов: {', '.join(summary['currency_codes_seen']) or 'нет'}.",
        "", "## Замечания", "",
    ]
    findings = report["findings"]
    if not findings:
        lines.append("В проверенном срезе замечаний не найдено.")
    else:
        lines += [
            "| ID | Уровень | Тип | Code | Path |",
            "| --- | --- | --- | --- | --- |",
        ]
        for item in findings:
            lines.append(
                f"| {item['id']} | {SEVERITY_RU[item['severity']]} | {item['kind']} | "
                f"{tick}{item['code']}{tick} | {tick}{item['path']}{tick} |"
            )
        for item in findings:
            lines += [
                "", f"### {item['id']} - {item['summary']}", "",
                f"- **Уровень:** {SEVERITY_RU[item['severity']]}",
                f"- **Тип:** {item['kind']}",
                f"- **Code:** {tick}{item['code']}{tick}",
                f"- **Path:** {tick}{item['path']}{tick}",
                f"- **Наблюдение:** {item['observed']}",
                f"- **Ожидание:** {item['expected']}",
                f"- **Риск:** {item['risk']}",
                f"- **Рекомендация backend:** {item['recommendation']}",
            ]
    lines += ["", "## Приоритетный план для backend", ""]
    recommendations: list[str] = []
    for item in findings:
        if item["recommendation"] not in recommendations:
            recommendations.append(item["recommendation"])
    if recommendations:
        lines.extend(f"{index}. {text}" for index, text in enumerate(recommendations, 1))
    else:
        lines.append("Сохранять контракт и повторять аудит на новых capture.")
    lines += ["", "## Ограничения", ""]
    lines.extend(f"- {item}" for item in report["limitations"])
    if not report["limitations"]:
        lines.append("- Не зафиксированы.")
    lines += [
        "", "## Методика и источники", "",
        "Проверен сырой payload до client transforms: HTTP/JSON, регистр и membership "
        "валют, decimal-представление, полнота rates, даты, timestamp/sequence и "
        "рыночные инварианты.",
    ]
    lines.extend(f"- [{item['title']}]({item['url']})" for item in report["references"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--input")
    parser.add_argument(
        "--profile", choices=["auto", "svelte-portfolio", "realtime"], default="auto"
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--title", default="Аудит финансового API")
    parser.add_argument("--allow-code", action="append", default=[])
    parser.add_argument("--headers-env")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--max-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("--stale-days", type=int, default=3)
    parser.add_argument("--currency-codes")
    args = parser.parse_args()
    if not args.output_json and not args.output_md:
        parser.error("нужен --output-json и/или --output-md")
    return args


def write_text(path_value: str | None, text: str) -> None:
    if path_value:
        path = Path(path_value)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    default_codes = Path(__file__).resolve().parent.parent / "references/iso4217-current.txt"
    try:
        codes, snapshot = load_codes(
            Path(args.currency_codes) if args.currency_codes else default_codes
        )
    except (OSError, InputError) as error:
        print(f"audit-financial-api: {error}", file=sys.stderr)
        return 1
    auditor = Auditor(
        codes, {item.strip().upper() for item in args.allow_code},
        args.profile, args.stale_days,
    )
    meta: dict[str, Any] = {
        "source_type": "url" if args.url else "file",
        "source": clean_url(args.url) if args.url else str(Path(args.input).resolve()),
        "http_status": None, "content_type": "", "cache_control": "",
        "payload_bytes": 0, "elapsed_ms": 0, "document_format": "unknown",
        "record_count": 0,
    }
    payload = None
    operation_error = None
    try:
        payload, meta = load_payload(args)
    except (OSError, InputError) as error:
        operation_error = str(error)
        code = error.code if isinstance(error, InputError) else "input.io"
        auditor.add(
            "critical", "operation", code, "$input",
            "Не удалось получить или разобрать payload", str(error),
            "Доступный UTF-8 JSON/JSONL в пределах лимита",
            "Аудит данных не выполнен; состояние API неизвестно",
            "Исправить доступ/формат и повторить запуск",
        )
    if payload is not None:
        transport(meta, auditor)
        auditor.walk(payload)
        if args.profile in {"auto", "realtime"}:
            auditor.sequence(payload)
        if args.profile == "svelte-portfolio":
            auditor.svelte_portfolio(payload, meta)
            auditor.project_contract(Path(args.project_root).resolve())
    auditor.finish()
    report = build_report(auditor, meta, args, snapshot, operation_error)
    write_text(args.output_json, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    write_text(args.output_md, markdown(report))
    counts = report["summary"]["by_severity"]
    print(
        f"{report['decision']}: {report['summary']['total_findings']} findings "
        f"(critical={counts['critical']}, high={counts['high']}, "
        f"medium={counts['medium']}, low={counts['low']})"
    )
    return 2 if counts["critical"] or counts["high"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
