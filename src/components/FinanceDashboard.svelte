<script lang="ts">
  import { calculateCurrencyTotals } from "$lib/calculations/currency-totals";
  import { calculateFinanceTotal } from "$lib/calculations/finance-total";
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import type { FinanceData, Language } from "$lib/types";

  let { data }: { data: FinanceData } = $props();
  const locale = useLocaleState();
  const locales: Record<Language, string> = {
    en: "en-US",
    ru: "ru-RU",
    uk: "uk-UA",
  };
  const totals = $derived(calculateCurrencyTotals(data.financeResult));
  const total = $derived(
    calculateFinanceTotal(data.financeResult, data.currencyData),
  );
  const localeCode = $derived(locales[locale.language]);
  const totalFormatted = $derived(
    new Intl.NumberFormat(localeCode, {
      style: "currency",
      currency: data.currencyData.base,
    }).format(Number(total)),
  );
  const formattedDate = $derived(
    new Intl.DateTimeFormat(localeCode, {
      dateStyle: "medium",
      timeZone: "UTC",
    }).format(new Date(data.currencyData.date + "T00:00:00Z")),
  );
</script>

<div class="portfolio-grid">
  <section class="total-balance-card">
    <div>
      <span class="panel-kicker">{locale.t("total")}</span>
      <strong>{totalFormatted}</strong>
      <p>{locale.t("finalRounded", { currency: data.currencyData.base })}</p>
    </div>
    <div class="balance-orbit" aria-hidden="true">
      <span>$</span>
    </div>
  </section>

  <section class="terminal-panel">
    <div class="panel-heading">
      <div>
        <span class="panel-kicker">{locale.t("noIntermediateRounding")}</span>
        <h2>{locale.t("totalsByCurrency")}</h2>
      </div>
    </div>
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>{locale.t("currency")}</th>
            <th class="text-end">{locale.t("total")}</th>
          </tr>
        </thead>
        <tbody>
          {#each totals as item (item.currency)}
            <tr>
              <td><span class="currency-code">{item.currency}</span></td>
              <td class="text-end numeric">
                {new Intl.NumberFormat(localeCode, {
                  style: "currency",
                  currency: item.currency,
                }).format(Number(item.amount))}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>

  <section class="terminal-panel">
    <div class="panel-heading">
      <div>
        <span class="panel-kicker"
          >{locale.t("asOf", { date: formattedDate })}</span
        >
        <h2>{locale.t("currentRates")}</h2>
      </div>
    </div>
    <div class="rate-list">
      {#each totals as item (item.currency)}
        {@const rate =
          item.currency === data.currencyData.base
            ? "1"
            : data.currencyData.rates[item.currency]}
        <div>
          <span>1 {data.currencyData.base}</span>
          <strong class="numeric">
            {new Intl.NumberFormat(localeCode, {
              maximumFractionDigits: 6,
            }).format(Number(rate))}
            {item.currency}
          </strong>
        </div>
      {/each}
    </div>
  </section>
</div>
