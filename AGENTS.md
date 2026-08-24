# Northstar Finance Terminal — локальные инструкции

Перед работой прочитай `~/.codex/AGENTS.md` и применяй этот файл только как project-specific delta. Для этапной работы используй `prompts/STAGES.md`, `docs/AI_PLAN.md` и `docs/AI_STATUS.md`.

## Контекст и инварианты

- Канонический стек этой ветки: SvelteKit 2, Svelte 5, TypeScript, Vite.
- Денежные вычисления выполняются через `decimal.js-light`; арифметика денег на `Number` запрещена.
- Все внешние HTTP/WebSocket payload проходят существующие Zod-схемы до попадания в состояние приложения.
- API keys и provider credentials не передаются в browser bundle, URL, логи или fixtures. Внешние feeds подключаются через доверенный backend/BFF.
- Production WebSocket использует `wss://`; `ws://` допустим только для loopback development.
- Demo stream является явным локальным режимом, а не скрытым fallback для ошибки production feed.
- Locale/market state должен оставаться scoped; не вводи неограниченное глобальное mutable state.

## Проверки

- `npm run check`
- `npm run lint`
- `npm run test:unit`
- `npm run test:e2e` после установки Chromium для Playwright
- `npm run build`

Принятые tests/fixtures/goldens являются контрактом и не меняются в рамках документационной или migration-задачи. Недоступный browser/backend gate фиксируется как `UNVERIFIED` с причиной.

## Локальные ограничения

- Сохраняй sequence deduplication, heartbeat, stale state, bounded backoff и `requestAnimationFrame` batching realtime-клиента.
- Не заявляй production market-data readiness без provider/BFF evidence.
- Не выполняй push/merge и не разрешай конфликт основного checkout без явного разрешения пользователя.
