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
