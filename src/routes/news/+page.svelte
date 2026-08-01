<script lang="ts">
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import { useMarketState } from "$lib/state/market-state.svelte";

  const locale = useLocaleState();
  const market = useMarketState();
  let query = $state("");
  let importance = $state("all");
  const localeCode = $derived(
    ({ en: "en-US", ru: "ru-RU", uk: "uk-UA" } as const)[locale.language],
  );
  const filteredNews = $derived.by(() => {
    const normalized = query.trim().toLowerCase();
    return market.news.filter((item) => {
      const matchesImportance =
        importance === "all" || item.importance === importance;
      const matchesQuery =
        !normalized ||
        item.headline.toLowerCase().includes(normalized) ||
        item.summary.toLowerCase().includes(normalized) ||
        item.currencies.some((currency) =>
          currency.toLowerCase().includes(normalized),
        );
      return matchesImportance && matchesQuery;
    });
  });

  function relativeTime(timestamp: number) {
    const minutes = Math.round((timestamp - Date.now()) / 60_000);
    return new Intl.RelativeTimeFormat(localeCode, { numeric: "auto" }).format(
      minutes,
      "minute",
    );
  }
</script>

<svelte:head>
  <title>{locale.t("newsTitle")} — {locale.t("brand")}</title>
  <meta name="description" content={locale.t("newsDescription")} />
</svelte:head>

<section class="page-section">
  <header class="page-heading split-heading">
    <div>
      <span class="eyebrow">{locale.t("live")}</span>
      <h1>{locale.t("newsTitle")}</h1>
      <p>{locale.t("newsDescription")}</p>
    </div>
    <span class="stream-counter">
      <span class="status-dot" aria-hidden="true"></span>
      {market.news.length} stories
    </span>
  </header>

  <form class="filter-bar" onsubmit={(event) => event.preventDefault()}>
    <label class="search-field">
      <span class="visually-hidden">{locale.t("searchNews")}</span>
      <span aria-hidden="true">⌕</span>
      <input
        type="search"
        bind:value={query}
        placeholder={locale.t("searchPlaceholder")}
        autocomplete="off"
      />
    </label>
    <label>
      <span class="visually-hidden">{locale.t("importance")}</span>
      <select class="terminal-select" bind:value={importance}>
        <option value="all">{locale.t("all")}</option>
        <option value="high">{locale.t("high")}</option>
        <option value="medium">{locale.t("medium")}</option>
        <option value="low">{locale.t("low")}</option>
      </select>
    </label>
  </form>

  <div class="news-grid" aria-live="polite">
    {#each filteredNews as item (item.id)}
      <article class="news-card">
        <div class="news-meta">
          <span class={"importance-badge " + item.importance}>
            {locale.t(item.importance)}
          </span>
          <time datetime={new Date(item.publishedAt).toISOString()}>
            {relativeTime(item.publishedAt)}
          </time>
        </div>
        <h2>{item.headline}</h2>
        <p>{item.summary}</p>
        <footer>
          <span>{item.source}</span>
          <div class="currency-tags">
            {#each item.currencies as currency (currency)}
              <span>{currency}</span>
            {/each}
          </div>
        </footer>
      </article>
    {:else}
      <div class="empty-state">
        <span class="empty-symbol" aria-hidden="true">◎</span>
        <p>{locale.t("noNews")}</p>
      </div>
    {/each}
  </div>
</section>
