# Аудит текущего финансового API — Northstar Finance Terminal

**Решение: REVIEW** - Payload пригоден для demo, но контракт требует согласования до production.

- Сформирован: 2026-08-08T14:25:01.345596+00:00
- Профиль: `svelte-portfolio`
- Источник: `http://127.0.0.1:5187/api/portfolio`
- Формат: `json`
- Размер: 591 bytes
- HTTP: 200; Content-Type: `application/json`
- Cache-Control: `no-store`

## Краткая сводка

| Critical | High | Medium | Low | Total |
| -------: | ---: | -----: | --: | ----: |
|        0 |    0 |      4 |   0 |     4 |

Проверено объектов: 12; массивов: 3; decimal-полей: 12. Коды валют/активов: EUR, GBP, UAH, USD.

## Замечания

| ID    | Уровень | Тип      | Code                                              | Path                                            |
| ----- | ------- | -------- | ------------------------------------------------- | ----------------------------------------------- |
| F-001 | Средний | contract | `contract.case_normalized_silently`               | `src/lib/schemas/finance.ts:currencyCodeSchema` |
| F-002 | Средний | contract | `contract.currency_membership_unchecked`          | `src/lib/schemas/finance.ts:currencyCodeSchema` |
| F-003 | Средний | contract | `contract.normalized_output_schema`               | `$.financeResult[1]`                            |
| F-004 | Средний | contract | `contract.realtime_currency_membership_unchecked` | `src/lib/schemas/realtime.ts`                   |

### F-001 - Клиентская схема молча исправляет регистр валюты

- **Уровень:** Средний
- **Тип:** contract
- **Code:** `contract.case_normalized_silently`
- **Path:** `src/lib/schemas/finance.ts:currencyCodeSchema`
- **Наблюдение:** .toUpperCase() before validation
- **Ожидание:** Backend возвращает uppercase, отклонения наблюдаемы
- **Риск:** Ошибки регистра сервера скрываются от мониторинга
- **Рекомендация backend:** Проверять raw payload до transform и исправить backend serialization

### F-002 - Схема проверяет форму кода, но не существование валюты

- **Уровень:** Средний
- **Тип:** contract
- **Code:** `contract.currency_membership_unchecked`
- **Path:** `src/lib/schemas/finance.ts:currencyCodeSchema`
- **Наблюдение:** /^[A-Z]{3}$/ after normalization
- **Ожидание:** Активный ISO 4217 код или allowlist
- **Риск:** Код ZZZ пройдёт границу и сломает обработку позже
- **Рекомендация backend:** Добавить membership-проверку на backend и frontend boundary

### F-003 - REST отдаёт нормализованные объекты, а upstream-схема принимает строки

- **Уровень:** Средний
- **Тип:** contract
- **Code:** `contract.normalized_output_schema`
- **Path:** `$.financeResult[1]`
- **Наблюдение:** 3 normalized object rows
- **Ожидание:** Отдельная response schema либо документированная bidirectional schema
- **Риск:** Повторная валидация ответа той же схемой завершится ошибкой
- **Рекомендация backend:** Добавить financeDataResponseSchema для нормализованного ответа

### F-004 - Realtime-схема принимает любой uppercase код из трёх букв

- **Уровень:** Средний
- **Тип:** contract
- **Code:** `contract.realtime_currency_membership_unchecked`
- **Path:** `src/lib/schemas/realtime.ts`
- **Наблюдение:** /^[A-Z]{3}$/
- **Ожидание:** Активный ISO 4217 код или allowlist
- **Риск:** Несуществующая валюта попадёт в balances/news/calendar
- **Рекомендация backend:** Синхронизировать ISO/allowlist-проверку с REST

## Приоритетный план для backend

1. Проверять raw payload до transform и исправить backend serialization
2. Добавить membership-проверку на backend и frontend boundary
3. Добавить financeDataResponseSchema для нормализованного ответа
4. Синхронизировать ISO/allowlist-проверку с REST

## Ограничения

- Production realtime-provider не проверен: запуск охватывает REST и статические схемы.
- Currency membership использует offline ISO 4217 snapshot от 2026-08-08.

## Методика и источники

Проверен сырой payload до client transforms: HTTP/JSON, регистр и membership валют, decimal-представление, полнота rates, даты, timestamp/sequence и рыночные инварианты.

- [SIX - ISO 4217 Maintenance Agency](https://www.six-group.com/en/products-services/financial-information/market-reference-data/data-standards.html)
- [ISO 4217 currency codes](https://www.iso.org/iso-4217-currency-codes.html)
