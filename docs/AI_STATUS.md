# Текущее состояние

Дата: 2026-08-24.

## Governance

- Project overlay интегрирован в `main` merge-коммитом `aeac30e`.
- Локальные правила ссылаются на глобальный контракт `~/.codex/AGENTS.md`.
- `validate_project_overlay.py <project-root>` — PASS.
- Старый незавершённый merge `integration/context-chain-main` был прерван: это unrelated React-приложение без общего merge-base с каноническим SvelteKit-проектом и не является совместимым governance-изменением.

## Product gates

- `pnpm check` — PASS: 0 ошибок, 0 предупреждений.
- `pnpm test:unit` — PASS: 7/7.
- `pnpm test:e2e` — PASS: 2/2 Chromium.
- `pnpm build` — PASS: production SvelteKit и Sites bundle собраны.
- `pnpm lint` — ESLint PASS; общий gate FAIL из-за существующего Prettier drift в 60 файлах. Форматирование не относится к dependency migration и отложено до отдельной задачи.
- Dependency manager migration 2026-08-24 локально интегрирована в `main`: `pnpm@11.23.0`, единственный `pnpm-lock.yaml`, clean restore и global virtual store — PASS; allowlist build scripts ограничен `esbuild` и `workerd`; push не выполнялся.
- `pnpm audit`: 13 транзитивных advisory (5 high, 6 moderate, 2 low) в Vite/Cloudflare tooling; автоматические upgrades не выполнялись, нужен отдельный dependency/security этап.
- Production provider backend/BFF отсутствует; readiness остаётся `UNVERIFIED`.

## Git

- Изменения governance объединены в `main`; push не выполнялся.
- Рабочее дерево чистое после проверок.
