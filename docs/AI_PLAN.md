# Текущий план

## Governance migration

Статус: завершено.

1. Интегрировать project overlay с единым глобальным контрактом `~/.codex/AGENTS.md` — выполнено.
2. Сохранить канонический стек SvelteKit 2/Svelte 5 и не смешивать его с unrelated React-историей — выполнено.
3. Проверить overlay, type-check, unit, E2E и production build — выполнено; результаты находятся в `docs/AI_STATUS.md`.
4. Не форматировать продуктовый код в рамках governance-задачи; Prettier drift вынести в отдельную задачу — принято.

## Следующая продуктовая задача

Отдельно спроектировать backend/BFF contract для provider feeds. Provider secrets не должны попадать во frontend bundle, URL, логи или fixtures.

Definition of Done governance-этапа: единый `prompts/STAGES.md`, согласованный project overlay, ссылка на `~/.codex/AGENTS.md`, validator PASS, продуктовый код не изменён.
