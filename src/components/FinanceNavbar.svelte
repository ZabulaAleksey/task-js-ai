<script lang="ts">
  import { resolve } from "$app/paths";
  import { page } from "$app/state";
  import { useLocaleState } from "$lib/state/locale-state.svelte";
  import { useMarketState } from "$lib/state/market-state.svelte";
  import type { TranslationKey } from "$lib/i18n";
  import type { Language, Theme } from "$lib/types";
  import FinanceLogo from "./FinanceLogo.svelte";

  let { theme, onToggleTheme }: { theme: Theme; onToggleTheme: () => void } =
    $props();
  const locale = useLocaleState();
  const market = useMarketState();
  const languages: Record<Language, string> = { en: "EN", ru: "RU", uk: "UA" };
  const links: { href: string; label: TranslationKey }[] = [
    {
      href: resolve("/terminal/[symbol=symbol]", { symbol: "EURUSD" }),
      label: "terminal",
    },
    { href: resolve("/portfolio"), label: "portfolio" },
    { href: resolve("/news"), label: "news" },
    { href: resolve("/calendar"), label: "calendar" },
    { href: resolve("/settings"), label: "settings" },
  ];

  const statusLabel = $derived(
    locale.t(
      (
        {
          idle: "offline",
          connecting: "connecting",
          online: "live",
          reconnecting: "reconnecting",
          stale: "stale",
          offline: "offline",
          demo: "demo",
        } as const
      )[market.status],
    ),
  );

  function isActive(href: string) {
    const root = href.split("/")[1];
    return (
      page.url.pathname === href || page.url.pathname.startsWith(`/${root}/`)
    );
  }
</script>

<header class="app-header">
  <div class="header-primary">
    <a
      class="brand-link"
      href={resolve("/terminal/[symbol=symbol]", { symbol: "EURUSD" })}
      aria-label={locale.t("terminal")}
    >
      <FinanceLogo />
    </a>

    <div class="header-actions">
      <span
        class:status-demo={market.status === "demo"}
        class="connection-pill"
      >
        <span class="status-dot" aria-hidden="true"></span>
        {statusLabel}
      </span>
      <label class="visually-hidden" for="language"
        >{locale.t("language")}</label
      >
      <select
        id="language"
        class="terminal-select compact-select"
        value={locale.language}
        aria-label={locale.t("language")}
        onchange={(event) =>
          locale.setLanguage(
            (event.currentTarget as HTMLSelectElement).value as Language,
          )}
      >
        {#each Object.entries(languages) as [value, label] (value)}
          <option {value}>{label}</option>
        {/each}
      </select>
      <button
        type="button"
        class="icon-button"
        onclick={onToggleTheme}
        aria-label={theme === "dark"
          ? locale.t("lightTheme")
          : locale.t("darkTheme")}
        title={theme === "dark"
          ? locale.t("lightTheme")
          : locale.t("darkTheme")}
      >
        <span aria-hidden="true">{theme === "dark" ? "☀" : "◐"}</span>
      </button>
    </div>
  </div>

  <nav class="terminal-nav" aria-label={locale.t("menu")}>
    {#each links as link (link.href)}
      <a
        href={link.href}
        class:active={isActive(link.href)}
        aria-current={isActive(link.href) ? "page" : undefined}
      >
        <span>{locale.t(link.label)}</span>
      </a>
    {/each}
  </nav>
</header>
