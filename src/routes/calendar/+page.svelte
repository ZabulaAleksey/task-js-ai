<script lang="ts">
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import { useMarketState } from "$lib/state/market-state.svelte";

  const locale = useLocaleState();
  const market = useMarketState();
  let currency = $state("all");
  let importance = $state("all");
  const localeCode = $derived(
    ({ en: "en-US", ru: "ru-RU", uk: "uk-UA" } as const)[locale.language],
  );
  const currencies = $derived(
    [...new Set(market.calendar.map((item) => item.currency))].sort(),
  );
  const events = $derived(
    market.calendar.filter(
      (item) =>
        (currency === "all" || item.currency === currency) &&
        (importance === "all" || item.importance === importance),
    ),
  );
</script>

<svelte:head>
  <title>{locale.t("calendarTitle")} — {locale.t("brand")}</title>
  <meta name="description" content={locale.t("calendarDescription")} />
</svelte:head>

<section class="page-section">
  <header class="page-heading">
    <span class="eyebrow">{locale.t("calendar")}</span>
    <h1>{locale.t("calendarTitle")}</h1>
    <p>{locale.t("calendarDescription")}</p>
  </header>

  <form
    class="filter-bar compact-filters"
    onsubmit={(event) => event.preventDefault()}
  >
    <label>
      <span class="control-label">{locale.t("currency")}</span>
      <select class="terminal-select" bind:value={currency}>
        <option value="all">{locale.t("all")}</option>
        {#each currencies as item (item)}
          <option value={item}>{item}</option>
        {/each}
      </select>
    </label>
    <label>
      <span class="control-label">{locale.t("importance")}</span>
      <select class="terminal-select" bind:value={importance}>
        <option value="all">{locale.t("all")}</option>
        <option value="high">{locale.t("high")}</option>
        <option value="medium">{locale.t("medium")}</option>
        <option value="low">{locale.t("low")}</option>
      </select>
    </label>
  </form>

  <section class="terminal-panel calendar-panel">
    <div class="data-table-wrapper">
      <table class="data-table calendar-table">
        <thead>
          <tr>
            <th>{locale.t("time")}</th>
            <th>{locale.t("currency")}</th>
            <th>{locale.t("event")}</th>
            <th>{locale.t("importance")}</th>
            <th class="text-end">{locale.t("previous")}</th>
            <th class="text-end">{locale.t("forecast")}</th>
            <th class="text-end">{locale.t("actual")}</th>
          </tr>
        </thead>
        <tbody>
          {#each events as item (item.id)}
            <tr>
              <td>
                <time datetime={new Date(item.scheduledAt).toISOString()}>
                  <strong
                    >{new Intl.DateTimeFormat(localeCode, {
                      hour: "2-digit",
                      minute: "2-digit",
                    }).format(item.scheduledAt)}</strong
                  >
                  <span
                    >{new Intl.DateTimeFormat(localeCode, {
                      month: "short",
                      day: "numeric",
                    }).format(item.scheduledAt)}</span
                  >
                </time>
              </td>
              <td><span class="currency-code">{item.currency}</span></td>
              <td>
                <strong>{item.title}</strong>
                <span>{item.country}</span>
              </td>
              <td>
                <span class={"importance-badge " + item.importance}>
                  {locale.t(item.importance)}
                </span>
              </td>
              <td class="text-end numeric">{item.previous ?? "—"}</td>
              <td class="text-end numeric">{item.forecast ?? "—"}</td>
              <td class="text-end numeric actual-value">{item.actual ?? "—"}</td
              >
            </tr>
          {:else}
            <tr>
              <td colspan="7" class="empty-cell">{locale.t("noEvents")}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>
</section>
