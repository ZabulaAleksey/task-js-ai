# Northstar Finance Terminal - local instructions

Before working here, read `~/codex-workspace/AGENTS.md`. These rules apply only to this SvelteKit finance application.

## Context routing

- Read `architecture.md` for architecture, stack, directory, or module-boundary changes.
- Read only the applicable file from `rules/`: `delivery.md`, `toolchain.md`, `security.md`, `realtime.md`, or `finance.md`.
- Do not load the complete rules directory, all SPEC files, reports, or `LEARNING_LOG.md` for a local task.

## Project invariants

- Use `decimal.js-light` for monetary calculations and preserve explicit rounding rules.
- Validate HTTP, form, and WebSocket boundaries with the existing Zod schemas.
- Preserve snapshot/delta ordering, monotonic sequence handling, heartbeat, reconnect, and bounded queues.
- Keep the demo stream usable without external credentials; never commit `.env.local`.

## Commands

- Checks: `npm run check` and `npm run lint`
- Unit tests: `npm run test:unit`
- End-to-end tests: `npm run test:e2e`
- Production build: `npm run build`
