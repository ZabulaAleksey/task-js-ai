# Журнал прогресса

## 2026-08-05 — Документирование архитектуры ветки `svelte`

### Итог

Удалённая ветка `origin/svelte` получена из того же GitHub-репозитория на коммите `4eb7164` и размещена в отдельном worktree `C:\MAMP\htdocs\Task_Module1-svelte` с локальной tracking-веткой `svelte`. Это сохранило незакоммиченные изменения основного checkout ветки `main` без смешивания двух реализаций.

Проанализированы SvelteKit routes, server load/actions, внутренний JSON endpoint, Svelte 5 state, WebSocket transport, Zod-схемы, demo-stream, Canvas-график, точные финансовые расчёты, тестовая инфраструктура и Cloudflare/OpenAI Sites build pipeline. Создан актуальный архитектурный документ ветки.

### Изменённые и созданные файлы

- `architecture.md` — создано полное описание архитектуры и технологического стека ветки `svelte`.
- `progress.md` — создан журнал задач репозитория и добавлена текущая запись.

### Проверки и тесты

- `npm ci` — успешно: установлено 239 пакетов, выполнен `svelte-kit sync`.
- `npm run check` — успешно: `svelte-check` обнаружил 0 ошибок и 0 предупреждений.
- `npm run lint` — ESLint завершился, но общий скрипт остановился на `prettier --check .`: до задачи 52 существующих файла ветки не соответствовали текущему Prettier; новый `architecture.md` после локального форматирования проверку проходит. Массовое переформатирование исходников не выполнялось как не относящееся к задаче.
- `npm run test:unit` — успешно: 3 test files, 7 тестов пройдено.
- Первый `npm run test:e2e` не смог запустить Chromium, потому что browser binary Playwright отсутствовал. Выполнен `npx playwright install chromium`, после чего E2E прошли.
- `npm test` — успешно: повторно пройдены 7 unit-тестов и 2 Playwright E2E-теста в Chromium.
- `npm run build` — успешно: Vite собрал SSR (175 модулей) и client (267 модулей), Cloudflare adapter завершил сборку, script подготовил `dist/server` и `dist/client` для Sites.

### Технические решения

- Ветка `main` не переключалась из-за незакоммиченных файлов; для `svelte` создан изолированный Git worktree.
- Архитектура описана как full-stack SvelteKit-приложение с явной server/client границей, а не как клиентская SPA.
- Отдельно зафиксированы realtime-протокол, sequence-дедупликация, batching через `requestAnimationFrame`, reconnect/backoff, demo fallback и ограничения размера state.
- Зафиксирован фактический Workers/Sites build pipeline: `adapter-cloudflare` плюс post-processing через esbuild.
- Конфигурация `.openai/hosting.json` сохранена без изменений; публикация не выполнялась, поскольку задача ограничена получением ветки и документацией.
- `PUBLIC_WS_URL` документирован как публичная браузерная конфигурация, в которой нельзя хранить секреты.
- Сгенерированные во время проверки `node_modules`, `.svelte-kit`, `dist` и `test-results` были очищены для обхода сбоя Windows sandbox; они полностью восстанавливаются командами ниже и не являются исходниками проекта.

### Известные ограничения и следующий шаг

- Внешний market provider и BFF отсутствуют; без `PUBLIC_WS_URL` работает demo-stream.
- Portfolio и `/api/portfolio` используют демонстрационные данные.
- Сохранённые terminal preferences пока не применяются к redirect, route defaults и размеру истории свечей.
- Canvas-график не имеет zoom, pan, crosshair и сохранения viewport.
- В проекте остаётся существующий formatting debt Prettier в 52 файлах.
- `npm ci` под Node.js 20.19.6 сообщает `EBADENGINE` для нескольких транзитивных Cloudflare/Wrangler-пакетов, требующих Node.js 22+; рекомендуется обновить локальную Node.js до 22 или новее.
- npm audit сообщает 9 уязвимостей зависимостей: 5 low, 2 moderate и 2 high. Автоматический `npm audit fix` не выполнялся, чтобы не менять dependency graph без отдельного анализа и запроса.
- Рекомендуемый следующий шаг: отдельной задачей обновить Node.js/toolchain, разобрать audit findings и согласованно отформатировать ветку, затем подключать production WebSocket через доверенный BFF.

### Переменные окружения

Новых переменных не добавлено. Текущая переменная ветки:

- `PUBLIC_WS_URL`

### Команды для продолжения работы

```bash
cd C:\MAMP\htdocs\Task_Module1-svelte
npm ci
npm run dev
npm run check
npm run lint
npm test
npm run build
```

## 2026-08-05 — Усиление безопасности, обновление стека и правила `AGENTS.md`

### Итог

Реализованы согласованные рекомендации по безопасности и toolchain для ветки `svelte`: проект переведён на закреплённые Node.js 24/npm 12 и Vite 7.3.6, audit очищен от известных уязвимостей, добавлены CSP и HTTP security headers, ограничены входящие realtime/finance payload, усилена последовательность событий, добавлены CI и Dependabot. Создан репозиторный `AGENTS.md` с обязательными архитектурными, security- и verification-правилами.

### Изменённые и созданные файлы

Функциональные, security- и dependency-изменения:

- `.env.example`, `.nvmrc`, `.node-version`;
- `package.json`, `package-lock.json`;
- `svelte.config.js`, `src/hooks.server.ts`, `src/app.html`, `src/app.css`;
- `src/routes/+layout.server.ts`, `src/routes/api/portfolio/+server.ts`;
- `src/lib/realtime/realtime-client.ts`, `src/lib/state/market-state.svelte.ts`, `src/lib/types.ts`;
- `src/lib/schemas/finance.ts`, `src/lib/schemas/finance.test.ts`;
- `src/lib/schemas/realtime.ts`, `src/lib/schemas/realtime.test.ts`;
- `tests/app.spec.ts`;
- `.github/workflows/ci.yml`, `.github/dependabot.yml`;
- `AGENTS.md`, `README.md`, `architecture.md`, `progress.md`.

В рамках устранения существовавшего formatting debt команда `npm run format` также механически нормализовала:

- `.openai/hosting.json`, `.prettierrc`, `eslint.config.js`, `playwright.config.ts`, `scripts/prepare-sites-build.mjs`;
- `src/app.d.ts`, `src/error.html`, `src/vite-env.d.ts`;
- `src/components/CandleChart.svelte`, `src/components/FinanceDashboard.svelte`, `src/components/FinanceLogo.svelte`, `src/components/FinanceNavbar.svelte`;
- `src/lib/calculations/currency-totals.ts`, `src/lib/calculations/finance-total.test.ts`, `src/lib/calculations/finance-total.ts`, `src/lib/calculations/money.ts`;
- `src/lib/demo/finance.ts`, `src/lib/demo/market.ts`, `src/lib/errors/app-error.ts`, `src/lib/i18n.ts`;
- `src/lib/schemas/preferences.test.ts`, `src/lib/schemas/preferences.ts`, `src/lib/state/locale-state.svelte.ts`;
- `src/params/symbol.ts`, `src/routes/+error.svelte`, `src/routes/+layout.svelte`, `src/routes/+page.ts`;
- `src/routes/calendar/+page.svelte`, `src/routes/news/+page.svelte`, `src/routes/portfolio/+page.server.ts`, `src/routes/portfolio/+page.svelte`, `src/routes/settings/+page.svelte`, `src/routes/terminal/[symbol=symbol]/+page.svelte`;
- `static/manifest.webmanifest`, `tsconfig.json`, `vite.config.ts`, `vitest.config.ts`.

### Проверки и тесты

Все команды выполнены с Node.js 24.18.0 и npm 12.0.2:

- `npm ci` — успешно, установлено 231 package, audit после установки: 0 vulnerabilities;
- `npm run format` — успешно, форматирование применено;
- `npm run check` — успешно, `svelte-check`: 0 errors и 0 warnings;
- `npm run lint` — успешно, ESLint и Prettier check без ошибок;
- `npm test` — успешно: Vitest 4/4 files и 11/11 tests; Playwright Chromium 3/3 tests;
- `npm run build` — успешно: Vite 7.3.6 собрал SSR (176 modules) и client (267 modules), Cloudflare adapter и Sites post-processing завершены;
- `npm audit --audit-level=high` — успешно, найдено 0 vulnerabilities.

E2E-проверка подтверждает наличие CSP и security headers, а также `Cache-Control: no-store` у portfolio API.

### Технические решения

- Node.js 24 выбран как актуальная LTS-среда, удовлетворяющая требованиям текущих Cloudflare/Wrangler-пакетов; версия закреплена во всех файлах toolchain.
- `@sveltejs/adapter-auto` удалён как неиспользуемый: production target уже определён как Cloudflare Workers/OpenAI Sites.
- Vite обновлён точечно до 7.3.6; транзитивные `cookie` и `undici` закреплены совместимыми `overrides`, без `npm audit fix --force` и без новых production-зависимостей.
- CSP управляется SvelteKit в auto-режиме. `connect-src 'self' wss:` временно допускает runtime-configured provider; после выбора provider origin нужно сузить.
- HSTS выдаётся только для HTTPS. Остальные защитные заголовки централизованы в server hook.
- `PUBLIC_SITE_URL` валидируется и используется для canonical origin, чтобы не полагаться на недоверенный Host в production.
- Realtime принимает только text frames до 64 КБ, использует bounded queues и закрывает соединение после пяти подряд protocol violations.
- Runtime-типы finance/realtime выводятся из Zod-схем, чтобы исключить расхождение ручных интерфейсов и фактической валидации.
- CI actions закреплены immutable SHA, а npm 12.0.2 устанавливается явно после setup-node; deployment не добавлялся и не выполнялся. Существующая структура Cloudflare/OpenAI Sites сохранена.

### Известные ограничения и следующий шаг

- Production WebSocket provider и BFF отсутствуют; без `PUBLIC_WS_URL` используется demo-stream.
- Пока provider не выбран, `connect-src wss:` шире желаемого. Следующий security-шаг — указать точный origin.
- Перед подключением реальных персональных данных portfolio необходимы authentication, authorization и server-side BFF с Origin allowlist, session expiry, per-message authorization и rate limits.
- Portfolio остаётся demo, серверного persistence нет; settings не влияют на начальный terminal route, а график не имеет zoom/pan/crosshair.
- Публикация в OpenAI Sites не выполнялась, так как пользователь её не запрашивал.

### Переменные окружения

Добавлена:

- `PUBLIC_SITE_URL`

Существующая:

- `PUBLIC_WS_URL`

Обе переменные публичны; секреты и их значения не добавлялись.

### Команды для продолжения работы

```bash
cd C:\MAMP\htdocs\Task_Module1-svelte
npm ci
npm run dev
npm run check
npm run lint
npm test
npm run build
npm audit --audit-level=high
```

## 2026-08-05 — Разделение репозиторных правил по предметным областям

### Итог

Монолитный `AGENTS.md` преобразован в короткий индекс с выборочной загрузкой правил. Финансовые вычисления вынесены отдельно; также выделены toolchain, безопасность, realtime и поставка с проверками. Обязательность исходных требований сохранена без необходимости помещать все несвязанные инструкции в контекст каждой задачи.

### Изменённые и созданные файлы

- `AGENTS.md` — оставлены общие правила, приоритеты и маршрутизация по тематическим документам.
- `rules/finance.md` — правила Decimal, округления и финансовых типов.
- `rules/security.md` — секреты, HTTP, CSP, server-side границы и безопасные логи.
- `rules/realtime.md` — WebSocket, Zod-валидация, лимиты, sequence и обновление протокола.
- `rules/toolchain.md` — закреплённый стек и политика зависимостей.
- `rules/delivery.md` — OpenAI Sites, обязательные проверки, документация и завершение.
- `architecture.md` — отражена новая структура каталога `rules/` и порядок выборочной загрузки.
- `progress.md` — добавлена эта запись.

### Проверки и тесты

- Проверено форматирование изменённых Markdown-файлов.
- `git diff --check` — без ошибок.
- Выполнена проверка изменённых файлов на случайные секреты; секреты и env-значения не добавлены.
- Полный набор application-тестов не запускался: изменялась только документация и инструкции, runtime-код и конфигурация не затронуты.

### Технические решения

- `rules/delivery.md` обязателен для любой задачи с изменением файлов, поскольку содержит общие требования к завершению.
- Остальные тематические документы читаются только при затрагивании соответствующей области; для междисциплинарной задачи применяются все релевантные файлы.
- Повторяющееся правило вывода внешних типов из Zod сохранено в finance и realtime независимо, чтобы каждый файл оставался самодостаточным в своей области.
- Публикация в OpenAI Sites не выполнялась: задача ограничена локальной реорганизацией инструкций.

### Известные ограничения и следующий шаг

- Экономия контекста зависит от соблюдения маршрутизации в корневом `AGENTS.md`; тематические файлы нельзя пропускать, если задача затрагивает их область.
- Следующий шаг не требуется. При появлении самостоятельной новой области её следует добавлять отдельным файлом только при наличии устойчивого набора правил.

### Переменные окружения

Новых переменных не добавлено.

## 2026-08-06 — Явная маршрутизация `AGENTS.md` к тематическим правилам

### Итог

Локальный `AGENTS.md` сокращён до обязательного индекса с прямыми Markdown-ссылками на каждый тематический файл из `rules/`. В индексе явно зафиксировано, что произвольные Markdown-файлы Codex автоматически не обнаруживает и соответствующий документ требуется прочитать до изменения файлов.

Корневые правила учебных Word/PDF-проектов вынесены из `C:\MAMP\htdocs\AGENTS.md` в отдельный тематический файл рабочей области. Корневой `AGENTS.md` теперь только направляет к нему подходящие задачи и исключает применение этих требований к программным проектам.

### Изменённые и созданные файлы

- `AGENTS.md` — локальный индекс проектных правил с прямыми ссылками.
- `rules/toolchain.md` и `rules/delivery.md` — удалены персональные требования о подтверждении зависимости и прямом разрешении пользователя на публикацию.
- `progress.md` — добавлена эта запись.
- `../AGENTS.md` — корневой тематический маршрутизатор рабочей области.
- `../rules/word-pdf-academic.md` — полный стандарт учебных Word/PDF-проектов.

### Проверки и тесты

- Проверено существование всех файлов, на которые ссылаются оба `AGENTS.md`.
- Проверено форматирование изменённых Markdown-файлов.
- `git diff --check` для Svelte-проекта — без ошибок.
- Полный набор application-тестов не запускался: runtime-код и конфигурация не изменялись.

### Технические решения

- В корневых и локальных `AGENTS.md` сохранена явная инструкция прочитать ссылочный файл: сама Markdown-ссылка не является механизмом автоматического импорта.
- Общие требования проекта остаются в тематических файлах; личные разрешения не возвращаются через новые ссылки.
- Hosting-конфигурация и hosted resources не изменялись, публикация не выполнялась.

### Известные ограничения и следующий шаг

- Применение ссылочного файла остаётся инструкцией агенту. Требования, которым нужна механическая гарантия, должны дополнительно обеспечиваться тестами, CI или hooks.
- Следующий шаг не требуется.

### Переменные окружения

Новых переменных не добавлено.

## 2026-08-08 — Навык аудита финансового API и текущий backend-отчёт

### Итог

Добавлен проектный и установленный в личный каталог Codex skill `audit-financial-api`. Он проверяет сырой REST JSON и JSONL realtime capture до клиентских transform, выявляет проблемы регистра, membership ISO 4217, decimal-представления, rates, дат, timestamps, sequence, bid/ask, OHLC и направления schema transform. Сформированы Markdown, JSON и визуально проверенный двухстраничный PDF-отчёт для backend-команды.

Фактический ответ `GET /api/portfolio` вернул HTTP 200, `application/json`, `Cache-Control: no-store`, 591 bytes. В текущем payload обнаружены только активные uppercase-коды `EUR`, `GBP`, `UAH`, `USD`; rates полны, положительны, base rate равен 1. Решение отчёта — `REVIEW`: 0 critical, 0 high, 4 medium контрактных замечания.

### Изменённые и созданные файлы

- `.agents/skills/audit-financial-api/SKILL.md` — workflow аудита и требования к backend-отчёту.
- `.agents/skills/audit-financial-api/agents/openai.yaml` — UI-метаданные навыка.
- `.agents/skills/audit-financial-api/scripts/audit_financial_api.py` — детерминированный HTTP/JSON/JSONL auditor.
- `.agents/skills/audit-financial-api/scripts/render_report_pdf.py` — Cyrillic-safe ReportLab renderer.
- `.agents/skills/audit-financial-api/references/iso4217-current.txt` — snapshot официального SIX List One от 2026-08-08.
- `.agents/skills/audit-financial-api/references/svelte-finance-contract.md` — профиль REST/realtime контракта проекта.
- `reports/financial-api-audit.md`, `reports/financial-api-audit.json` — текущий человекочитаемый и структурированный отчёт.
- `output/pdf/financial-api-audit.pdf` — передаваемая backend-команде PDF-версия.
- `README.md`, `architecture.md`, `progress.md` — использование, структура и журнал поставки.

### Проверки и тесты

- `quick_validate.py` для проектной и установленной копий skill — `Skill is valid!`.
- `python -m py_compile` для обоих Python-скриптов — успешно.
- Фактический аудит локального `/api/portfolio` — `REVIEW`, 4 medium, без high/critical.
- Синтетический проблемный portfolio payload — `STOP`, exit 2; обнаружены case/whitespace, `ZZZ`, collision rates, missing/non-positive/base rates, stale date и JSON number.
- Синтетический realtime JSONL — `STOP`, exit 2; обнаружены sequence regression, lowercase symbol, unknown currency, seconds timestamp, crossed quote и нарушения OHLC.
- PDF отрендерен в две страницы и проверен постранично: кириллица, таблицы, переносы, поля, header/footer и page numbers без дефектов.
- `npm run format` — выполнено; итоговый `npm run lint` подтвердил Prettier/ESLint.
- `npm run check` — 0 errors и 0 warnings.
- `npm run lint` — успешно.
- `npm test` — Vitest 4/4 files, 11/11 tests; Playwright 3/3 tests.
- `npm run build` — успешно, Cloudflare adapter и Sites post-processing завершены.
- `npm audit --audit-level=high` — не пройден: 1 high advisory `GHSA-2v37-7h3g-55p8` в транзитивном dev dependency `nanoid@3.3.16` через `eslint-plugin-svelte -> postcss`; исправление доступно, но dependency/lockfile не изменялись вне scope этой задачи.
- `git diff --check` и проверка отчёта на secrets выполняются перед финальным commit.

### Технические решения

- Сырой payload проверяется до Zod `.toUpperCase()`, чтобы backend-дефекты регистра не исчезали при нормализации.
- ISO membership отделён от трёхбуквенной формы; не-ISO активы принимаются только через явный `--allow-code`.
- Upstream input schema и нормализованный public response рассматриваются как разные направления контракта; для endpoint рекомендована отдельная `financeDataResponseSchema`.
- Отчёт не сохраняет authorization headers, cookies, query strings, API keys или полный персональный payload.
- ISO snapshot взят у SIX как официального Maintenance Agency; при устаревании skill требует обновить reference.
- PDF сформирован через ReportLab и проверен PNG-рендером через PyMuPDF, поскольку Poppler в среде отсутствовал.
- Навык хранится в репозитории и синхронизирован в `C:\Users\aleks\.codex\skills\audit-financial-api`.

### Известные ограничения и следующий шаг

- Production WebSocket provider не проверен: без отдельного raw JSONL capture отчёт покрывает REST endpoint, demo payload и статические realtime-схемы.
- Четыре medium замечания требуют backend/frontend согласования: raw casing, ISO membership в finance, отдельная response schema и общая membership-проверка realtime.
- Отдельным следующим шагом следует обновить транзитивный `nanoid` совместимым patch-релизом и повторить `npm audit --audit-level=high`.

### Переменные окружения

Новых переменных не добавлено. Для authenticated audit существующие секреты можно передавать только через явно выбранную env-переменную и `--headers-env`; её имя и значение в проект не добавлялись.
