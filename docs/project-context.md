# Контекст Northstar Finance Terminal

Проект — SvelteKit 2 / Svelte 5 терминал для портфеля, валютных котировок, свечей, новостей и экономического календаря. Репозиторий содержит автономный demo stream и production-oriented WebSocket boundary, но не содержит доверенного provider backend/BFF.

Ключевые границы: точные расчёты находятся в `src/lib/calculations`, внешние данные валидируются в `src/lib/schemas`, realtime transport изолирован в `src/lib/realtime`, scoped state — в `src/lib/state`, страницы и server load/actions — в `src/routes`. Browser не должен получать provider secrets.

Опубликованный GitHub `main` содержит SvelteKit baseline и merge dependency-manager migration. Состояние иных пользовательских checkout не проверено; эта документационная миграция не разрешает их возможные конфликты.
