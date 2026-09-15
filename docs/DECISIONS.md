# Архитектурные решения

## ADR-000 — pnpm и общий dependency store

Статус: принято 2026-08-24. Канонический менеджер — `pnpm@11.23.0`, единственный lock-файл — `pnpm-lock.yaml`. Clean restore и все gates выполняются через pnpm; build scripts разрешаются только точечным allowlist. При несовместимости global virtual store сохраняется общий content store и применяется project-local virtual-store fallback.

## ADR-001 — SvelteKit является каноническим стеком migration-ветки

Статус: принято. Проверенный branch содержит SvelteKit 2/Svelte 5, его routes, tests и build contract. Незавершённый конфликт с React в основном checkout не разрешается governance-миграцией.

## ADR-002 — Денежные значения не вычисляются на Number

Статус: принято. `decimal.js-light` сохраняет точность и банковское округление.

## ADR-003 — Provider secrets принадлежат backend/BFF

Статус: принято. Browser принимает валидированные публичные события; ключи не попадают в client bundle.

## ADR-004 — Demo stream является отдельным режимом

Статус: принято. Он обеспечивает локальную воспроизводимость, но не маскирует сбой настроенного production feed.

## ADR-005 — Канонический execution state

Статус: принято 2026-09-15. Текущий plan, status, evidence и NEXT принадлежат только `docs/STAGES.md`. Исторический stage catalog и старые AI facts сохранены в `docs/notes/`, не как второй live owner.
