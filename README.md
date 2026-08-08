# Northstar Finance Terminal

SvelteKit 2 + Svelte 5 терминал для точных денежных расчётов, потоковых валютных котировок, свечей, новостей и экономического календаря.

## Возможности

- маршруты `/terminal/[symbol]`, `/portfolio`, `/news`, `/calendar`, `/settings`;
- SSR, server load/actions и внутренний JSON API;
- точные расчёты через `decimal.js-light`;
- Zod-схемы на границах HTTP, форм и WebSocket;
- изолированные locale/market state на Svelte 5 runes;
- WebSocket-клиент с snapshot/delta, монотонным `sequence`, heartbeat, reconnect и bounded queues;
- встроенный demo-stream без внешних ключей;
- адаптивные светлая и тёмная темы;
- unit- и Playwright E2E-тесты;
- проектный навык аудита сырых финансовых API-ответов с Markdown/JSON/PDF-отчётом;
- сборка для Cloudflare Workers и OpenAI Sites.

## Требования и запуск

Нужны Node.js 24.18 LTS и npm 12. Версии закреплены в `.nvmrc`, `.node-version`, `package.json` и lockfile.

```bash
npm ci
npm run dev
```

Без переменных окружения приложение использует локальный demo-stream.

## Конфигурация

Создайте `.env` на основе `.env.example`:

```dotenv
PUBLIC_WS_URL=wss://stream.example.com/v1/market
PUBLIC_SITE_URL=https://terminal.example.com
```

- `PUBLIC_WS_URL` — публичный WebSocket endpoint. В production разрешён только `wss://`; `ws://` допустим только для `localhost` и `127.0.0.1`.
- `PUBLIC_SITE_URL` — доверенный canonical origin production-сайта. Для внешнего адреса требуется HTTPS.

Любое значение `PUBLIC_*` попадает в браузер. Не храните там API-ключи, токены или другие секреты. Поставщика, которому нужна секретная авторизация, подключайте через доверенный backend/BFF.

После соединения клиент отправляет подписку:

```json
{
  "type": "subscribe",
  "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
  "timeframes": ["1m", "5m", "15m", "1h"],
  "channels": ["quotes", "candles", "balances", "news", "calendar"],
  "afterSequence": 0
}
```

Runtime-контракт событий находится в `src/lib/schemas/realtime.ts`.

## Безопасность

- SvelteKit формирует CSP без `unsafe-eval` и inline-стилей; сервер добавляет HSTS для HTTPS, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` и защиту от framing.
- `/api/portfolio` возвращает `Cache-Control: no-store`.
- Входящие WebSocket-сообщения ограничены 64 КБ, проходят Zod-валидацию и помещаются только в ограниченные очереди. После пяти подряд нарушений протокола соединение закрывается без автоматического reconnect.
- Размеры массивов и строк, timestamps, `sequence`, decimal values, bid/ask и OHLC-инварианты проверяются до изменения состояния.
- Production-логи не содержат исходный объект ошибки, request headers, cookies или payload.

Текущая CSP разрешает `connect-src 'self' wss:` для настраиваемого внешнего feed. После выбора production provider сузьте директиву до конкретного origin. BFF дополнительно должен проверять Origin, аутентификацию, срок сессии, авторизацию подписок и rate limits.

## Аудит финансового API

Проектный skill `.agents/skills/audit-financial-api` проверяет сырой REST JSON или JSONL-capture realtime-потока до клиентской нормализации. Он выявляет проблемы регистра, неизвестные или выведенные из обращения ISO 4217 коды, коллизии ключей rates, отсутствие курсов, неточные JSON-числа, устаревшие даты, нарушения sequence, bid/ask и OHLC, а также расхождения input/output schema.

Для текущего REST endpoint:

```powershell
python .agents/skills/audit-financial-api/scripts/audit_financial_api.py `
  --url http://127.0.0.1:5173/api/portfolio `
  --profile svelte-portfolio `
  --project-root . `
  --output-json reports/financial-api-audit.json `
  --output-md reports/financial-api-audit.md
```

Актуальные результаты находятся в `reports/financial-api-audit.md`, `reports/financial-api-audit.json` и `output/pdf/financial-api-audit.pdf`. Заголовки авторизации передавайте только через отдельную env-переменную с `--headers-env`; skill не включает secrets или полный персональный payload в отчёт.

## Проверки

```bash
npm run format
npm run check
npm run lint
npm test
npm run build
npm audit --audit-level=high
```

Для первого E2E-запуска установите Chromium: `npx playwright install chromium`.

GitHub Actions выполняет этот набор для `main` и `svelte`; Dependabot предлагает совместимые обновления npm и GitHub Actions.

## Структура

```text
.agents/skills/audit-financial-api/  повторяемый аудит API и генерация отчётов
output/pdf/                         PDF-отчёты для передачи backend-команде
reports/                            Markdown и структурированный JSON аудита
src/lib/calculations/  точная доменная арифметика
src/lib/demo/          автономные тестовые данные
src/lib/realtime/      WebSocket-транспорт и reconnect
src/lib/schemas/       runtime-валидация и выведенные из схем типы
src/lib/state/         scoped state приложения
src/routes/            страницы, server load/actions и API
tests/                 сквозные пользовательские сценарии
```

Production-сборка использует `@sveltejs/adapter-cloudflare` и формирует Workers-совместимые `dist/server` и `dist/client` для существующего проекта OpenAI Sites. Публикация не выполняется автоматически локальными командами.
