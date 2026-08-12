# Finance Data Aggregator - local instructions

Before working here, read `~/codex-workspace/AGENTS.md`. This file contains only project-specific additions.

## Project context

- React 19, TypeScript, and Vite application that aggregates financial data from external APIs.
- Validate external payloads with the existing Zod schemas and keep request/calculation logic outside presentation components.
- Use `decimal.js-light` and the established banking-rounding rules for monetary calculations.
- Keep English, Russian, and Ukrainian user-facing text synchronized through the existing i18n layer.
- API keys are ephemeral sensitive input: never log, persist, hard-code, or commit them.
- Preserve explicit loading and error states around independent data sources.

## Commands

- Development: `npm run dev`
- Lint: `npm run lint`
- Production build: `npm run build`

There is no automated test script in the current package manifest. Load only task-relevant AI Dev Team rules or specifications; do not preload all rules, SPEC files, or `LEARNING_LOG.md`.
