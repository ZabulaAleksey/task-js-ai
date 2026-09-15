# Этапы Northstar Finance Terminal

- Stage ID: NSTAR-QUALITY-BASELINE

## NSTAR-QUALITY-BASELINE — Svelte quality gate

- Status: partial
- Condition: четыре принятых gates прошли, общий lint gate не прошёл из-за 63 файлов с Prettier drift; production backend/BFF не проверен.
- Plan: отдельным ограниченным изменением устранить форматирование, не переписывая accepted tests/fixtures; затем повторить весь quality pipeline.
- Evidence: 2026-09-15 `pnpm install --frozen-lockfile` PASS; `pnpm check` 0/0 PASS; unit 7/7 PASS; Chromium E2E 2/2 PASS; build PASS; ESLint PASS; Prettier 63 files FAIL. Исторические факты и SHA старых документов сохранены в `docs/notes/legacy-ai-state-evidence.md`; подробные будущие контракты — `docs/notes/legacy-stage-contracts.md`.
- NEXT: NSTAR-QUALITY-FORMATTING
- USER action `NSTAR-MERGE-DOCS`: PENDING; после публикации документационной ветки явно разрешить её merge в `main`; evidence — GitHub default-branch read-back только `docs/STAGES.md`; unlock — удаление полностью слитой ветки.

## Будущие этапы

- `NSTAR-BFF-CONTRACT`: planned; versioned HTTP/WebSocket schemas, authentication, quotas, timeout/retry, redacted observability и явный demo mode. Требуются утверждённая SPEC/ADR и contract tests до provider adapter.
- `NSTAR-PROVIDER-ADAPTER`: planned; один provider через доверенный backend/BFF, Zod event mapping, rate limits, backoff и failure evidence; credentials не попадают в Git.
- `NSTAR-DEPLOYMENT-EVIDENCE`: planned; CSP, monitoring, rollback и live deployment gates после отдельного разрешения.
