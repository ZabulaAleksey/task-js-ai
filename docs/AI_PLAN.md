# Текущий план

Статус: governance migration подготовлена в отдельном worktree.

1. Интегрировать этот project overlay только после пользовательского разрешения и осознанного разрешения Svelte/React merge в основном checkout.
2. После интеграции прогнать `check`, lint, unit, E2E и build на фактическом выбранном продуктовом варианте.
3. Следующей продуктовой задачей отдельно спроектировать backend/BFF contract; не помещать provider secrets в frontend.

Definition of Done governance-этапа: единый `STAGES.md`, согласованные локальные инструкции, честный статус merge blocker, overlay validator PASS, отсутствие изменения продуктового кода.
