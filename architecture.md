# Архитектура Task_Module1 — ветка `svelte`

## 1. Назначение и границы

Northstar Finance Terminal — полноэкранное SvelteKit-приложение для наблюдения за валютным рынком и демонстрационным портфелем. Оно объединяет:

- realtime-котировки и OHLC-свечи;
- портфель с точной десятичной арифметикой;
- рыночные новости и экономический календарь;
- локальные настройки языка, темы и терминала;
- demo-stream для автономного запуска.

SvelteKit разделяет приложение на SSR/server load/actions/API и гидратируемую браузерную часть. Собственной базы данных, очередей, authentication-сервиса и долговременного серверного хранилища в репозитории нет.

## 2. Технологический стек

| Область              | Технология                              | Роль                                                       |
| -------------------- | --------------------------------------- | ---------------------------------------------------------- |
| Runtime              | Node.js 24.18 LTS, npm 12               | Локальная разработка, тесты и сборка                       |
| Язык                 | TypeScript 6, ES modules, target ES2022 | Строгая типизация client/server/build-кода                 |
| UI                   | Svelte 5                                | Компоненты, runes и Context API                            |
| Full-stack framework | SvelteKit 2                             | Routing, SSR, load/actions, endpoint, error handling и CSP |
| Сборка               | Vite 7.3.6                              | Dev server и bundling                                      |
| Production runtime   | Cloudflare Workers                      | Выполнение server bundle                                   |
| Adapter              | `@sveltejs/adapter-cloudflare`          | Сборка SvelteKit под Workers                               |
| Hosting              | OpenAI Sites, `.openai/hosting.json`    | Существующий hosting pipeline без D1/R2 bindings           |
| Realtime             | Browser WebSocket API                   | Snapshot и последовательные delta-события                  |
| Валидация            | Zod 4                                   | Runtime-контракты HTTP, форм, preferences и realtime       |
| Деньги               | `decimal.js-light`                      | Десятичные вычисления и банковское округление              |
| График               | Canvas 2D API                           | Отрисовка OHLC без внешней chart-библиотеки                |
| Стили                | Собственный CSS                         | Design tokens, темы, responsive layout                     |
| Unit-тесты           | Vitest 4, V8 coverage                   | Расчёты и схемы                                            |
| E2E                  | Playwright                              | Пользовательские и HTTP security-сценарии                  |
| Анализ               | `svelte-check`, ESLint 10               | Типы, Svelte и статический анализ                          |
| Форматирование       | Prettier 3                              | Единый формат исходников и документации                    |
| CI                   | GitHub Actions                          | Полная проверка веток `main` и `svelte`                    |
| Обновления           | Dependabot                              | Совместимые npm- и GitHub Actions-обновления               |

Версии среды закреплены в `.nvmrc`, `.node-version`, `package.json#engines` и `packageManager`. Установка выполняется через `npm ci` с committed lockfile. `overrides` фиксируют безопасные совместимые версии транзитивных `cookie` и `undici`.

## 3. Архитектурные слои

```text
Routes и Svelte components
        ↓
Scoped state на Svelte 5 runes
        ↓
Realtime transport / server loads, actions и API
        ↓
Zod schemas и чистые финансовые calculations
        ↓
Внешний WebSocket provider либо встроенные demo-источники
```

Основные правила границ:

- `src/routes` владеет URL, SSR, metadata, server load/actions и композицией экранов;
- `src/components` содержит переиспользуемое представление без server-only импорта;
- locale и market state создаются для layout и передаются через Svelte Context, а не через глобальные singleton;
- `RealtimeClient` отвечает за транспорт, reconnect, лимиты и диспетчеризацию;
- `MarketState` отвечает за реактивное состояние, монотонный `sequence` и ограничение истории;
- все внешние данные валидируются Zod до попадания в state или расчёты;
- TypeScript-типы внешних контрактов выводятся из Zod-схем, чтобы runtime- и compile-time-модели не расходились;
- денежные расчёты изолированы от Svelte и выполняются через `decimal.js-light`;
- demo-источники используют тот же внутренний контракт, что и внешний provider.

## 4. Структура репозитория

```text
Task_Module1/
├── .agents/
│   └── skills/audit-financial-api/  # Аудит REST/realtime payload и генерация отчётов
├── .github/
│   ├── workflows/ci.yml             # Проверки push/PR
│   └── dependabot.yml               # Регулярные dependency updates
├── .openai/hosting.json             # Связь с проектом OpenAI Sites
├── scripts/prepare-sites-build.mjs  # Подготовка dist/server и dist/client
├── src/
│   ├── components/                  # Navbar, portfolio dashboard, Canvas chart
│   ├── lib/
│   │   ├── calculations/            # Точная финансовая арифметика
│   │   ├── demo/                    # Автономные finance/market fixtures
│   │   ├── errors/                  # Безопасные прикладные ошибки
│   │   ├── realtime/                # WebSocket transport
│   │   ├── schemas/                 # Zod-схемы и выведенные типы
│   │   └── state/                   # Scoped locale/market state
│   ├── params/                      # Route matcher валютных символов
│   ├── routes/                      # Страницы, server load/actions и API
│   ├── hooks.server.ts              # Error handling и HTTP security headers
│   ├── app.html                     # HTML shell
│   └── app.css                      # Глобальные tokens и layout
├── tests/                           # Playwright E2E и HTTP security tests
├── reports/                         # Текущие Markdown/JSON результаты API-аудита
├── output/pdf/                      # Передаваемый backend-команде PDF-отчёт
├── rules/                           # Тематические правила, загружаемые по области задачи
│   ├── delivery.md                  # Sites, проверки и завершение
│   ├── finance.md                   # Денежные вычисления и округление
│   ├── realtime.md                  # WebSocket и market payload
│   ├── security.md                  # Секреты, HTTP и server-side безопасность
│   └── toolchain.md                 # Runtime, стек и зависимости
├── AGENTS.md                        # Краткий индекс правил работы с веткой
├── architecture.md                  # Этот документ
└── progress.md                      # Добавляемый журнал изменений
```

`AGENTS.md` содержит только общие правила и маршрутизацию. Перед изменением файлов исполнитель читает `rules/delivery.md` и лишь те дополнительные файлы из `rules/`, которые относятся к затронутой предметной области. Это сохраняет обязательность правил без загрузки несвязанных инструкций в контекст каждой задачи.

## 5. Runtime и маршруты

Сервер SvelteKit:

- перенаправляет `/` на `/terminal/EURUSD`;
- загружает demo-портфель на `/portfolio`;
- обрабатывает portfolio form action;
- отдаёт `/api/portfolio` с `Cache-Control: no-store`;
- формирует canonical URL из валидированного `PUBLIC_SITE_URL`, а при его отсутствии — из request origin;
- создаёт reference id для необработанных ошибок и не раскрывает пользователю технические детали.

Основные маршруты:

| Маршрут              | Назначение                                   |
| -------------------- | -------------------------------------------- |
| `/terminal/[symbol]` | Котировки, timeframe, OHLC-график и balances |
| `/portfolio`         | Сводка и точные финансовые расчёты           |
| `/news`              | Поток рыночных новостей                      |
| `/calendar`          | Экономические события                        |
| `/settings`          | Локальные preferences                        |
| `/api/portfolio`     | Внутренний JSON endpoint demo-портфеля       |

После hydration корневой layout создаёт state, подключает `RealtimeClient`, выбирает внешний WebSocket либо demo-stream и сохраняет browser-only настройки. DOM, Canvas, storage и WebSocket используются только в браузерных lifecycle-участках.

## 6. Realtime-протокол

Если `PUBLIC_WS_URL` пуст, запускается встроенный demo-stream. Для внешнего endpoint разрешены `wss://` и локальные `ws://localhost`/`ws://127.0.0.1`.

После открытия соединения клиент отправляет версионированную подписку с symbols, timeframes, channels и `afterSequence`. Поддерживаются события:

- `snapshot`;
- `quote.update`;
- `candle.update`;
- `balance.update`;
- `news.create`;
- `calendar.update`;
- `heartbeat`.

Каждое входящее сообщение проходит следующую границу:

```text
string message → размер ≤ 64 КБ → JSON.parse → Zod safeParse
→ монотонный sequence → bounded queue/coalescing → MarketState
```

Binary frames отклоняются. После пяти подряд невалидных сообщений соединение закрывается с protocol error, а автоматический reconnect блокируется до явного ручного подключения. Основная очередь ограничена 1000 событиями, coalesced map — 256 ключами. Quote/candle updates схлопываются по бизнес-ключу и применяются через `requestAnimationFrame`.

Схемы ограничивают размеры строк и snapshot-массивов, диапазоны timestamps/`sequence`, длину decimal strings и проверяют `ask >= bid` и OHLC-инварианты. Событие, включая snapshot, не применяется при `sequence <= lastSequence`.

Состояние дополнительно ограничено 500 свечами на `symbol:timeframe`, 100 новостями и 200 календарными событиями. Heartbeat/stale-check и exponential backoff с jitter обеспечивают восстановление связи.

## 7. Финансовые расчёты

`/portfolio` пока использует server-side demo-источник. Схемы готовы для валидации двух finance providers и таблицы валютных курсов.

Расчёты:

- используют precision 40;
- учитывают только оплаченные транзакции первого источника;
- переводят небазовую валюту делением на курс;
- не применяют промежуточное округление;
- округляют итог через `ROUND_HALF_EVEN` по fraction digits базовой валюты;
- преобразуют Decimal в `number` только для визуализации после валидации.

## 8. График и пользовательское состояние

`CandleChart.svelte` рисует OHLC-свечи через Canvas 2D: wick по high/low, body по open/close, масштабирование по `devicePixelRatio`, адаптация через `ResizeObserver` и группировка redraw через `requestAnimationFrame`. Одновременно показываются последние 72 свечи; текстовый `figcaption` предоставляет OHLC-summary для assistive technologies.

Язык, тема и terminal preferences хранятся в `localStorage` только после Zod-валидации. Market state живёт в памяти layout до перезагрузки.

## 9. Конфигурация и безопасность

```dotenv
PUBLIC_WS_URL=
PUBLIC_SITE_URL=
```

Обе переменные публичны и не могут содержать секреты. `PUBLIC_SITE_URL` должен быть HTTPS-origin, кроме локального HTTP. Если feed требует secret token, нужен server-side BFF.

Реализованные меры:

- SvelteKit CSP в auto-режиме: `default-src 'self'`, запрет object/frame embedding, ограниченные script/style/font/img/worker directives;
- `connect-src 'self' wss:` разрешает runtime-configured secure feed; после выбора provider директиву следует сузить до его origin;
- серверные заголовки: `Permissions-Policy`, `Referrer-Policy`, `X-Content-Type-Options`, `X-Frame-Options`; HSTS добавляется только для HTTPS;
- inline style из HTML shell удалён, `unsafe-eval` и `unsafe-inline` не используются;
- SvelteKit CSRF origin check не ослаблен;
- персональный API-ответ не кешируется;
- production error log содержит структурированные безопасные поля и reference id, но не raw error, headers, cookies или payload;
- realtime и finance payload ограничены и семантически валидируются;
- lockfile проходит `npm audit --audit-level=high` без известных уязвимостей;
- CI actions закреплены immutable commit SHA.

Будущий production BFF обязан проверять WebSocket Origin allowlist, authentication, session expiry, authorization каждой подписки и rate limits.

## 10. Сборка, CI и поставка

`npm run build` выполняет:

1. `vite build` создаёт Cloudflare Worker output;
2. `scripts/prepare-sites-build.mjs` формирует bundled ESM `dist/server/index.js` и статический `dist/client`.

`.openai/hosting.json` сохраняет связь с существующим OpenAI Sites-проектом. Локальная задача не публикует приложение и не изменяет hosted resources без прямого запроса пользователя.

GitHub Actions для push/PR в `main` и `svelte` использует Node из `.nvmrc`, явно устанавливает npm 12.0.2, выполняет `npm ci`, устанавливает Playwright Chromium и запускает:

```bash
npm run check
npm run lint
npm test
npm run build
npm audit --audit-level=high
```

Dependabot еженедельно группирует patch/minor обновления development toolchain и ежемесячно проверяет GitHub Actions.

## 11. Тестовая архитектура

Vitest проверяет:

- денежные расчёты, конвертацию, группировку и `ROUND_HALF_EVEN`;
- preferences;
- корректные и повреждённые realtime events;
- лимиты snapshot, crossed quote и OHLC-инварианты;
- лимиты finance decimal strings и коллекций rates.

Playwright запускает приложение на `127.0.0.1:4173` и проверяет навигацию, demo-stream, сохранение settings, CSP/security headers и запрет кеширования portfolio API.

## 12. Текущие ограничения и точки расширения

- Внешний provider и доверенный BFF не входят в репозиторий; без `PUBLIC_WS_URL` работает demo-stream.
- `connect-src wss:` остаётся широкой временной директивой, пока не выбран production provider.
- Portfolio API использует demo-данные и пока не имеет authentication/authorization; перед реальными персональными данными они обязательны.
- Серверного persistence и общей пользовательской сессии нет.
- Settings пока не меняют начальный redirect и константу максимального числа свечей.
- График не поддерживает zoom, pan, crosshair и сохранение viewport.
- Realtime snapshot не сохраняется между перезагрузками вкладки.
- При добавлении provider сохраняется граница: внешний payload → schema/adapter → внутренний тип → scoped state/UI.
- При добавлении D1, R2, authentication или новых Sites bindings нужно одновременно обновить hosting metadata, server types, security tests и этот документ.

## 13. Аудит качества финансового API

Проектный skill `.agents/skills/audit-financial-api` отделяет аудит сырого server payload от нормализованного внутреннего состояния. Он принимает HTTP JSON, локальный JSON или JSONL capture realtime-событий и выпускает:

- структурированный JSON с устойчивыми finding ID, severity, JSON path, риском и backend-рекомендацией;
- Markdown-отчёт без secrets, query tokens и полного персонального payload;
- проверяемый PDF через отдельный ReportLab renderer.

Офлайн-валидация валют использует датированный snapshot официального ISO 4217 List One от SIX. Для не-ISO активов требуется явный allowlist. Профиль `svelte-portfolio` дополнительно сравнивает текущий REST output с направлением Zod transform, проверяет полноту rates и `Cache-Control: no-store`, а также отмечает контрактные границы, которые молча нормализуют регистр или проверяют только трёхбуквенную форму кода.

Текущий отчёт хранится в `reports/financial-api-audit.md` и `reports/financial-api-audit.json`; передаваемая версия — в `output/pdf/financial-api-audit.pdf`. Production WebSocket provider не считается проверенным без отдельного raw capture.
