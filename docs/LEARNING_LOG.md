# Журнал проверенных наблюдений

- Migration-ветка содержит SvelteKit 2/Svelte 5, несмотря на историческое имя каталога и устаревшее React-описание в прежнем `AGENTS.md`.
- В репозитории уже есть unit и Playwright E2E scripts; утверждение об отсутствии test runner было устаревшим.
- Основной checkout имеет активный `MERGE_HEAD`; его index и рабочие файлы сохранены без попытки автоматического разрешения.
- Production readiness внешних feeds нельзя вывести из наличия WebSocket client: требуется отдельное evidence backend/BFF и provider contract.
- После lockfile install `npm audit` сообщил 10 известных advisories (3 high); автоматический breaking `audit fix` не выполнялся.
- `npm run lint` блокируется существующим Prettier drift в 52 product/config files, тогда как `svelte-check`, 7 unit tests и production build проходят.
