# Northstar Finance Terminal

SvelteKit 2 + Svelte 5 терминал для точных денежных расчётов, потоковых валютных котировок, свечей, новостей и экономического календаря.

## Что уже есть

- файловая маршрутизация: `/terminal/[symbol]`, `/portfolio`, `/news`, `/calendar`, `/settings`;
- серверная загрузка портфеля и form action без передачи секретов в браузер;
- точные расчёты через `decimal.js-light`, без арифметики денежных сумм на `Number`;
- Zod-схемы на границах HTTP, форм и WebSocket;
- изолированные locale/market state на Svelte 5 runes;
- WebSocket-клиент с WSS, snapshot + delta, sequence-дедупликацией, heartbeat, stale-state, backoff и буферизацией обновлений через `requestAnimationFrame`;
- встроенный demo-stream, который работает без внешних ключей;
- светлая и тёмная темы, адаптивная вёрстка, клавиатурный focus, skip-link и live regions;
- route-level metadata, manifest и favicon;
- unit- и Playwright E2E-тесты.

## Запуск

```bash
npm install
npm run dev
```

Откройте адрес, который выведет Vite. Без переменных окружения приложение автоматически запускает безопасный локальный demo-stream.

## Проверки

```bash
npm run check
npm run lint
npm run test:unit
npx playwright install chromium
npm run test:e2e
npm run build
```

## Подключение WebSocket

Создайте `.env` на основе `.env.example`:

```dotenv
PUBLIC_WS_URL=wss://stream.example.com/v1/market
```

В production разрешён только `wss://`. `ws://` допускается исключительно для `localhost` и `127.0.0.1`. В браузер нельзя передавать API-ключи поставщиков: внешний feed должен подключаться через ваш доверенный backend/BFF.

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

Сервер должен присылать версионированные события `snapshot`, `quote.update`, `candle.update`, `balance.update`, `news.create`, `calendar.update` и `heartbeat`. Точная runtime-схема находится в `src/lib/schemas/realtime.ts`.

## Структура

```text
src/lib/calculations/  точная доменная арифметика
src/lib/demo/          автономные тестовые данные
src/lib/realtime/      транспорт и стратегия переподключения
src/lib/schemas/       runtime-валидация внешних данных
src/lib/state/         scoped state приложения
src/routes/            страницы, server load/actions и API
tests/                 сквозные пользовательские сценарии
```

Production-сборка использует официальный `@sveltejs/adapter-cloudflare` и дополнительно готовит Workers-совместимые каталоги `dist/server` и `dist/client`. Заголовки CSP и monitoring настраиваются на стороне выбранного хостинга.
