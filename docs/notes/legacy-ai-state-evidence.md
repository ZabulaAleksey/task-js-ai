# Сохранённые факты прежнего AI state

- `docs/AI_PLAN.md`: SHA-256 `173af397814d1c52b9e5b6f96a1a29cc49d27d6989675b96e2450a86f83ccfc8`; исходные байты восстановимы из Git parent этой миграции.
- `docs/AI_STATUS.md`: SHA-256 `25155b9ee4499b2ba1520a60a4638e37d5f9ce8db279bce8354a4c11f52bb29c`; исходные байты восстановимы из Git parent этой миграции.

Проверенные факты: в GitHub `main` опубликован merge dependency-manager migration; SvelteKit 2/Svelte 5 остаётся текущим стеком; доверенного provider backend/BFF нет. Повторная локальная проверка 2026-09-15: `pnpm install --frozen-lockfile`, `pnpm check` (0 ошибок и предупреждений), `pnpm test:unit` (7/7), `pnpm test:e2e` (2/2 Chromium после переноса disposable projection на короткий изолированный store), `pnpm build` — PASS. `pnpm lint`: ESLint PASS, общий gate FAIL из-за Prettier drift в 63 файлах. Исторические 13 advisory от 2026-08-24 не подтверждены текущим audit и не являются новой проверкой. Старое утверждение о неотправленном push устарело после GitHub merge; незавершённый merge в неизвестном пользовательском checkout этой документационной миграцией не разрешался.
