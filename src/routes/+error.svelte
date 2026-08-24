<script lang="ts">
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  const locale = useLocaleState();
</script>

<svelte:head>
  <title>{page.status} — {locale.t("brand")}</title>
</svelte:head>

<section class="page-section narrow-section">
  <div class="error-panel" role="alert">
    <span class="eyebrow">HTTP {page.status}</span>
    <h1>{page.status === 404 ? locale.t("notFound") : locale.t("appError")}</h1>
    <p>
      {page.status === 404 ? locale.t("appErrorHelp") : page.error?.message}
    </p>
    {#if page.error?.errorId}
      <p class="error-id">Reference: {page.error.errorId}</p>
    {/if}
    <a
      class="primary-button"
      href={resolve("/terminal/[symbol=symbol]", { symbol: "EURUSD" })}
      >{locale.t("backToTerminal")}</a
    >
  </div>
</section>
