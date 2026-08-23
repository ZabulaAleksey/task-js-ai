# Этапы Northstar Finance Terminal

## Общий контракт

Выполняй один этап за раз. До реализации сверяй `AGENTS.md`, `docs/ARCHITECTURE.md`, текущие `AI_PLAN`/`AI_STATUS`; не меняй принятые tests/fixtures. Внешние данные валидируй Zod, деньги считай через `decimal.js-light`, secrets оставляй на backend/BFF. Для каждого этапа фиксируй gates и evidence, а недоступное помечай `UNVERIFIED`.

## Этап 1 — Зафиксировать Svelte integration baseline

Цель: после отдельного пользовательского решения интегрировать migration-ветку с основным checkout без потери обеих сторон незавершённого merge.

Scope: выбрать канонический продуктовый стек; разрешить package/README/source conflicts; сохранить backup refs; проверить полный diff. Non-goals: новый UI или provider integration. DoD: нет conflict markers, выбранный stack документирован ADR, `npm ci` и его gates воспроизводимы. Текущий статус: `BLOCKED_BY_USER_MERGE_DECISION`.

## Этап 2 — Подтвердить существующий Svelte quality gate

Цель: доказать, что принятый Svelte baseline проходит `npm run check`, `npm run lint`, `npm run test:unit`, `npm run test:e2e`, `npm run build`.

Scope: только прогон и минимальное исправление выявленных regression по отдельному запросу. DoD: команды и версии окружения записаны в `AI_STATUS`; browser/backend ограничения отделены от PASS. Тестовые контракты не переписываются.

## Этап 3 — Versioned backend/BFF contract

Цель: определить доверенную серверную границу для market data без выдачи provider keys браузеру.

Scope: versioned HTTP/WebSocket schemas, authentication, quotas, timeout/retry policy, sequence semantics, redacted observability и explicit demo mode. Security: только `wss://` production, bounded payloads, no secrets/log leakage. DoD: SPEC/ADR, contract tests и documented fallback до реализации provider adapter.

## Этап 4 — Provider adapter

Цель: подключить одного выбранного provider через backend/BFF.

Scope: adapter mapping в канонические Zod events, rate limits, backoff, stale/error UX, metrics. Non-goals: второй provider или автоматический fallback. DoD: contract/integration tests, failure matrix, sandbox evidence; реальные credentials не попадают в Git.

## Этап 5 — Production deployment evidence

Цель: подтвердить Cloudflare deployment boundary.

Scope: CSP, security headers, environment separation, health/monitoring, rollback и smoke scenarios. DoD: build artifact, deployment checklist и критические E2E; внешняя публикация выполняется только с отдельным разрешением.
