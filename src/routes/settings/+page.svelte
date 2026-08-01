<script lang="ts">
  import { onMount } from "svelte";
  import { preferencesSchema } from "$lib/schemas/preferences";
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import { useMarketState } from "$lib/state/market-state.svelte";
  import type { Timeframe } from "$lib/types";

  const locale = useLocaleState();
  const market = useMarketState();
  let preferredSymbol = $state("EURUSD");
  let preferredTimeframe = $state<Timeframe>("1m");
  let maxCandles = $state(300);
  let validationError = $state("");
  let saved = $state(false);
  let ready = $state(false);

  onMount(() => {
    const stored = localStorage.getItem("terminal-preferences");
    if (stored) {
      try {
        const result = preferencesSchema.safeParse(JSON.parse(stored));
        if (result.success) {
          preferredSymbol = result.data.preferredSymbol;
          preferredTimeframe = result.data.preferredTimeframe;
          maxCandles = result.data.maxCandles;
        }
      } catch {
        localStorage.removeItem("terminal-preferences");
      }
    }
    ready = true;
  });

  function save(event: SubmitEvent) {
    event.preventDefault();
    saved = false;
    const result = preferencesSchema.safeParse({
      preferredSymbol,
      preferredTimeframe,
      maxCandles,
    });
    if (!result.success) {
      validationError = locale.t("invalidPreferences");
      return;
    }
    validationError = "";
    localStorage.setItem("terminal-preferences", JSON.stringify(result.data));
    saved = true;
  }
</script>

<svelte:head>
  <title>{locale.t("settingsTitle")} — {locale.t("brand")}</title>
  <meta name="description" content={locale.t("settingsDescription")} />
</svelte:head>

<section class="page-section">
  <header class="page-heading">
    <span class="eyebrow">{locale.t("settings")}</span>
    <h1>{locale.t("settingsTitle")}</h1>
    <p>{locale.t("settingsDescription")}</p>
  </header>

  <div class="settings-grid">
    <section class="terminal-panel settings-panel">
      <div class="panel-heading">
        <div>
          <span class="panel-kicker">{locale.t("appearance")}</span>
          <h2>Workspace preferences</h2>
        </div>
      </div>
      <form class="settings-form" onsubmit={save} novalidate aria-busy={!ready}>
        <label>
          <span>{locale.t("preferredSymbol")}</span>
          <select class="terminal-select" bind:value={preferredSymbol} required>
            <option value="EURUSD">EUR / USD</option>
            <option value="GBPUSD">GBP / USD</option>
            <option value="USDJPY">USD / JPY</option>
          </select>
        </label>
        <label>
          <span>{locale.t("preferredTimeframe")}</span>
          <select
            class="terminal-select"
            bind:value={preferredTimeframe}
            required
          >
            <option value="1m">1m</option>
            <option value="5m">5m</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
          </select>
        </label>
        <label>
          <span>{locale.t("maxCandles")}</span>
          <input
            class="terminal-input"
            class:invalid={Boolean(validationError)}
            type="number"
            min="100"
            max="500"
            step="25"
            bind:value={maxCandles}
            aria-invalid={Boolean(validationError)}
            aria-describedby="max-candles-help settings-error"
            required
          />
          <small id="max-candles-help">{locale.t("maxCandlesHelp")}</small>
        </label>
        {#if validationError}
          <p id="settings-error" class="field-error" role="alert">
            {validationError}
          </p>
        {/if}
        <button class="primary-button" type="submit" disabled={!ready}>
          <span aria-hidden="true">✓</span>
          {locale.t("saveSettings")}
        </button>
        <p class="form-status" aria-live="polite">
          {saved ? locale.t("settingsSaved") : ""}
        </p>
      </form>
    </section>

    <section class="terminal-panel settings-panel">
      <div class="panel-heading">
        <div>
          <span class="panel-kicker">{locale.t("live")}</span>
          <h2>{locale.t("connection")}</h2>
        </div>
        <span
          class={"importance-badge " +
            (market.status === "offline" ? "high" : "low")}
        >
          {market.status}
        </span>
      </div>
      <dl class="connection-details">
        <div>
          <dt>Mode</dt>
          <dd>{market.status === "demo" ? locale.t("demo") : "WebSocket"}</dd>
        </div>
        <div>
          <dt>Last sequence</dt>
          <dd class="numeric">{market.lastSequence}</dd>
        </div>
        <div>
          <dt>Invalid messages</dt>
          <dd class="numeric">{market.invalidMessages}</dd>
        </div>
        <div>
          <dt>Endpoint</dt>
          <dd>
            {market.status === "demo" ? "Built-in safe demo" : "Configured WSS"}
          </dd>
        </div>
      </dl>
      <p class="settings-note">{locale.t("connectionHint")}</p>
      <p class="settings-note secure-note">
        <span aria-hidden="true">◆</span>
        {locale.t("secureConfig")}
      </p>
      <button
        class="secondary-button"
        type="button"
        onclick={() => market.reconnect()}
      >
        <span aria-hidden="true">↻</span>
        {locale.t("reconnectNow")}
      </button>
    </section>
  </div>
</section>
