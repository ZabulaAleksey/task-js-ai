# Архитектура

```text
routes / server load-actions
        ↓
scoped application state
        ↓
validated calculations + realtime client
        ↓
Zod boundary ← demo stream | trusted backend/BFF
```

Svelte components отображают состояние и инициируют use cases, но не реализуют денежную арифметику или wire parsing. Realtime-клиент поддерживает snapshot/delta sequence, deduplication, heartbeat, stale state, bounded reconnect и UI batching. Demo provider выбирается явно при отсутствии production configuration; ошибка configured provider не должна незаметно переключать пользователя на demo.

Production credentials остаются на backend/BFF. В браузер передаётся только разрешённый `wss://` endpoint и публичные данные. Deployment adapter — Cloudflare; CSP и monitoring задаются на hosting boundary.

## Контракт зависимостей

- Источник истины (Source of truth): `package.json`, `pnpm-lock.yaml` и `pnpm-workspace.yaml`; канонический менеджер — `pnpm@11.23.0`.
- Чистое восстановление (Clean restore): удалить только disposable `node_modules`, затем выполнить `pnpm install --frozen-lockfile`.
- Общий pnpm content store и global virtual store разрешены; `allowBuilds` ограничен `esbuild` и `workerd`.
- `node_modules`, `.svelte-kit`, `build`, Playwright output и tool caches пересоздаваемы; исходники, fixtures и локальные секреты dependency cleanup не затрагивает.
- Locked gates: `pnpm check`, `pnpm lint`, `pnpm test:unit`, `pnpm build` и, при установленном Chromium, `pnpm test:e2e`.
