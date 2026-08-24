# Контекст Northstar Finance Terminal

Проект — SvelteKit 2 / Svelte 5 терминал для портфеля, валютных котировок, свечей, новостей и экономического календаря. Репозиторий содержит автономный demo stream и production-oriented WebSocket boundary, но не содержит доверенного provider backend/BFF.

Ключевые границы: точные расчёты находятся в `src/lib/calculations`, внешние данные валидируются в `src/lib/schemas`, realtime transport изолирован в `src/lib/realtime`, scoped state — в `src/lib/state`, страницы и server load/actions — в `src/routes`. Browser не должен получать provider secrets.

Основной checkout находится в незавершённом пользовательском merge между Svelte и React вариантами. Governance-изменение изолировано в Svelte migration-worktree и не разрешает этот конфликт.
