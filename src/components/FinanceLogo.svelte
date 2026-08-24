<script lang="ts">
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  const locale = useLocaleState();
</script>

<span class="finance-brand">
  <span class="finance-logo-mark" aria-hidden="true">
    <span>↗</span>
  </span>
  <span class="finance-brand-copy">
    <span class="finance-brand-name">{locale.t("brand")}</span>
    <span class="finance-brand-accent">{locale.t("brandTagline")}</span>
  </span>
</span>
