# Compatibility matrix: STAGES migration

Read-only reconcile перед изменением классифицировал brownfield overlay: `AGENTS.md`, `prompts/STAGES.md`, `docs/AI_PLAN.md`, `docs/AI_STATUS.md` — MERGE; `docs/STAGES.md` — ADD. Продуктовый код, accepted tests, fixtures, `package.json`, lockfile и пользовательские checkout — FORBIDDEN_TO_OVERWRITE. Старые AI facts и stage contracts сохранены в `docs/notes/` с SHA и Git parent как rollback point. Формального DEV bridge нет; global overlay validator по этой причине не подтверждает full adoption.
