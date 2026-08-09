<script lang="ts">
  import { goto } from "$app/navigation";
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import CandleChart from "../../../components/CandleChart.svelte";
  import FinanceNavIcon from "../../../components/FinanceNavIcon.svelte";
  import { decimal } from "$lib/calculations/money";
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import { useMarketState } from "$lib/state/market-state.svelte";
  import type { Timeframe } from "$lib/types";
  import type { PageProps } from "./$types";

  let { params }: PageProps = $props();
  const locale = useLocaleState();
  const market = useMarketState();
  const pairs = ["EURUSD", "GBPUSD", "USDJPY"];
  const timeframes: Timeframe[] = ["1m", "5m", "15m", "1h"];
  const currencySymbols: Record<string, string> = {
    USD: "$",
    EUR: "€",
    GBP: "£",
  };

  const timeframe = $derived.by(() => {
    const requested = page.url.searchParams.get(
      "timeframe",
    ) as Timeframe | null;
    return requested && timeframes.includes(requested) ? requested : "1m";
  });
  const quote = $derived(market.quotes[params.symbol]);
  const candles = $derived(market.candlesFor(params.symbol, timeframe));
  const latestCandle = $derived(candles.at(-1));
  const spread = $derived(
    quote ? decimal(quote.ask).minus(decimal(quote.bid)).toString() : "—",
  );
  const localeCode = $derived(
    ({ en: "en-US", ru: "ru-RU", uk: "uk-UA" } as const)[locale.language],
  );

  function changePair(event: Event) {
    const symbol = (event.currentTarget as HTMLSelectElement).value;
    goto(
      resolve("/terminal/[symbol=symbol]", { symbol }) +
        "?timeframe=" +
        timeframe,
    );
  }
</script>

<svelte:head>
  <title>{params.symbol} · {timeframe} — {locale.t("brand")}</title>
  <meta name="description" content={locale.t("terminalDescription")} />
</svelte:head>

<section class="page-section terminal-page">
  <header class="page-heading terminal-heading">
    <div class="terminal-title-block">
      <h1>{locale.t("terminalTitle", { symbol: params.symbol })}</h1>
      <p>{locale.t("terminalDescription")}</p>
    </div>
    <div class="terminal-controls">
      <label>
        <span class="control-label">Instrument</span>
        <select
          class="terminal-select instrument-select"
          value={params.symbol}
          onchange={changePair}
        >
          {#each pairs as pair (pair)}
            <option value={pair}>{pair.slice(0, 3)} / {pair.slice(3)}</option>
          {/each}
        </select>
      </label>
      <div>
        <span class="control-label">{locale.t("timeframe")}</span>
        <div class="segmented-control">
          {#each timeframes as item (item)}
            <a
              class:active={timeframe === item}
              href={resolve("/terminal/[symbol=symbol]", {
                symbol: params.symbol,
              }) +
                "?timeframe=" +
                item}
              aria-current={timeframe === item ? "page" : undefined}>{item}</a
            >
          {/each}
        </div>
      </div>
    </div>
  </header>

  <div class="market-grid trading-workspace">
    <section class="terminal-panel chart-panel">
      <div class="market-overview">
        <div class="price-cluster">
          <span class="instrument-label"
            >{params.symbol.slice(0, 3)} / {params.symbol.slice(3)}</span
          >
          <div class="live-price-row">
            <strong class="live-price">{quote?.bid ?? "—"}</strong>
            {#if quote}
              <span
                class:negative={Number(quote.changePercent) < 0}
                class="price-change"
              >
                {Number(quote.changePercent) >= 0 ? "+" : "−"}{Math.abs(
                  Number(quote.changePercent),
                ).toFixed(2)}%
              </span>
            {/if}
          </div>
        </div>
        <div class="market-clock">
          <span>{locale.t("lastUpdate")}</span>
          <strong>
            {quote
              ? new Intl.DateTimeFormat(localeCode, {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                }).format(quote.timestamp)
              : "—"}
          </strong>
        </div>
      </div>

      <div class="quote-strip" aria-label="Current quote">
        <div>
          <span>{locale.t("bid")}</span><strong class="quote-positive"
            >{quote?.bid ?? "—"}</strong
          >
        </div>
        <div>
          <span>{locale.t("ask")}</span><strong class="quote-negative"
            >{quote?.ask ?? "—"}</strong
          >
        </div>
        <div><span>{locale.t("spread")}</span><strong>{spread}</strong></div>
        <div>
          <span>{locale.t("dayChange")}</span>
          <strong>{quote ? quote.changePercent + "%" : "—"}</strong>
        </div>
      </div>

      <CandleChart
        {candles}
        label={locale.t("priceChart", { symbol: params.symbol })}
        summary={latestCandle
          ? locale.t("candleSummary", {
              open: latestCandle.open,
              high: latestCandle.high,
              low: latestCandle.low,
              close: latestCandle.close,
            })
          : ""}
      />
    </section>

    <aside class="terminal-panel balances-panel">
      <div class="panel-heading balance-heading">
        <div>
          <h2>{locale.t("portfolio")}</h2>
          <p>{locale.t("balances")}</p>
        </div>
        <a class="text-link" href={resolve("/portfolio")}>
          View all <FinanceNavIcon name="arrow-up-right" size={15} />
        </a>
      </div>
      <div class="balance-list">
        {#each market.balances as balance (balance.currency)}
          <article>
            <div class="currency-chip">
              {currencySymbols[balance.currency] ??
                balance.currency.slice(0, 1)}
            </div>
            <div>
              <strong>{balance.currency}</strong>
              <span>{locale.t("available")}</span>
            </div>
            <div class="balance-value">
              <strong
                >{new Intl.NumberFormat(localeCode, {
                  maximumFractionDigits: 2,
                }).format(Number(balance.available))}</strong
              >
              <span
                >≈ USD {new Intl.NumberFormat(localeCode, {
                  maximumFractionDigits: 2,
                }).format(Number(balance.convertedUsd))}</span
              >
            </div>
          </article>
        {:else}
          <div class="data-placeholder">Waiting for balance snapshot…</div>
        {/each}
      </div>
    </aside>
  </div>
</section>
