<script lang="ts">
  import { env } from "$env/dynamic/public";
  import { onMount } from "svelte";
  import "../app.css";
  import FinanceNavbar from "../components/FinanceNavbar.svelte";
  import { RealtimeClient } from "$lib/realtime/realtime-client";
  import { provideLocaleState } from "$lib/state/locale-state.svelte";
  import { provideMarketState } from "$lib/state/market-state.svelte";
  import type { Theme } from "$lib/types";

  let { children, data } = $props();
  const locale = provideLocaleState();
  const market = provideMarketState();
  let theme = $state<Theme>("dark");
  let realtimeClient: RealtimeClient | null = null;

  function applyTheme(nextTheme: Theme) {
    theme = nextTheme;
    document.documentElement.dataset.bsTheme = nextTheme;
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", nextTheme === "dark" ? "#07111f" : "#eef4fb");
    localStorage.setItem("theme", nextTheme);
  }

  function toggleTheme() {
    applyTheme(theme === "dark" ? "light" : "dark");
  }

  onMount(() => {
    locale.initialize();
    const savedTheme = localStorage.getItem("theme");
    const preferredTheme = matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    applyTheme(
      savedTheme === "light" || savedTheme === "dark"
        ? savedTheme
        : preferredTheme,
    );

    realtimeClient = new RealtimeClient(market, env.PUBLIC_WS_URL);
    market.setReconnectHandler(() => realtimeClient?.reconnectNow());
    realtimeClient.start();
    return () => {
      market.setReconnectHandler(null);
      realtimeClient?.stop();
    };
  });
</script>

<svelte:head>
  <meta
    name="description"
    content="Realtime currency terminal with live candles, portfolio balances, market news and an economic calendar."
  />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Northstar Finance Terminal" />
  <meta property="og:title" content="Northstar Finance Terminal" />
  <meta
    property="og:description"
    content="Realtime currency candles, exact portfolio balances, market news and an economic calendar."
  />
  <meta property="og:image" content={`${data.origin}/og-card.png`} />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Northstar Market Intelligence" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content={`${data.origin}/og-card.png`} />
</svelte:head>

<a class="skip-link" href="#main-content">{locale.t("skipToContent")}</a>
<div class="app-shell">
  <FinanceNavbar {theme} onToggleTheme={toggleTheme} />
  <main id="main-content" class="app-main" tabindex="-1">
    {@render children()}
  </main>
</div>
