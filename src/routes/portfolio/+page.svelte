<script lang="ts">
  import { enhance } from "$app/forms";
  import FinanceDashboard from "../../components/FinanceDashboard.svelte";
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import type { PageProps } from "./$types";

  let { data, form }: PageProps = $props();
  const locale = useLocaleState();
  let refreshing = $state(false);
  const financeData = $derived(form?.financeData ?? data.financeData);
</script>

<svelte:head>
  <title>{locale.t("portfolioTitle")} — {locale.t("brand")}</title>
  <meta name="description" content={locale.t("portfolioDescription")} />
</svelte:head>

<section class="page-section">
  <header class="page-heading split-heading">
    <div>
      <span class="eyebrow">{locale.t("portfolio")}</span>
      <h1>{locale.t("portfolioTitle")}</h1>
      <p>{locale.t("portfolioDescription")}</p>
    </div>
    <form
      method="POST"
      action="?/refresh"
      use:enhance={() => {
        refreshing = true;
        return async ({ update }) => {
          await update();
          refreshing = false;
        };
      }}
    >
      <button class="secondary-button" type="submit" disabled={refreshing}>
        <span class:spin={refreshing} aria-hidden="true">↻</span>
        {refreshing ? "Refreshing…" : "Refresh snapshot"}
      </button>
    </form>
  </header>

  <div class="notice-banner" role="status">
    <span aria-hidden="true">◆</span>
    <span>{locale.t("demoPortfolioNotice")}</span>
  </div>

  <FinanceDashboard data={financeData} />
</section>
