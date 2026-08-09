<script lang="ts">
  type FinanceIconName =
    | "terminal"
    | "portfolio"
    | "news"
    | "calendar"
    | "settings"
    | "sun"
    | "moon"
    | "arrow-up-right";

  let { name, size = 20 }: { name: FinanceIconName; size?: number } = $props();
</script>

<svg
  class="finance-icon"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.6"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  {#if name === "terminal"}
    <path d="M4 19V5M4 19h16" />
    <path d="m7 15 3.2-4 3.1 2.2L19 7" />
  {:else if name === "portfolio"}
    <rect x="3" y="7" width="18" height="13" rx="2" />
    <path
      d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18M10 12v2h4v-2"
    />
  {:else if name === "news"}
    <rect x="4" y="3" width="16" height="18" rx="2" />
    <path d="M8 7h8M8 11h8M8 15h5M8 18h7" />
  {:else if name === "calendar"}
    <rect x="3" y="5" width="18" height="16" rx="2" />
    <path
      d="M8 3v4M16 3v4M3 10h18M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"
    />
  {:else if name === "settings"}
    <circle cx="12" cy="12" r="3" />
    <path
      d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.86 2.86-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21H9.5v-.1A1.7 1.7 0 0 0 8.4 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.86-2.86.06-.06A1.7 1.7 0 0 0 4 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H2V9.5h.3A1.7 1.7 0 0 0 4 8.4a1.7 1.7 0 0 0-.34-1.88l-.06-.06L6.46 3.6l.06.06A1.7 1.7 0 0 0 8.4 4a1.7 1.7 0 0 0 1-.6A1.7 1.7 0 0 0 9.8 2H14v.3A1.7 1.7 0 0 0 15 4a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.86 2.86-.06.06A1.7 1.7 0 0 0 19.4 8a1.7 1.7 0 0 0 .6 1 1.7 1.7 0 0 0 1.1.4h.1v4.2h-.1a1.7 1.7 0 0 0-1.7 1.4Z"
    />
  {:else if name === "sun"}
    <circle cx="12" cy="12" r="3.5" />
    <path
      d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42"
    />
  {:else if name === "moon"}
    <path d="M20.2 15.4A8 8 0 0 1 8.6 3.8 8.5 8.5 0 1 0 20.2 15.4Z" />
  {:else}
    <path d="M7 17 17 7M9 7h8v8" />
  {/if}
</svg>

<style>
  @media (max-width: 700px) {
    :global(.header-actions .connection-label) {
      display: inline;
    }

    :global(.header-actions .connection-pill) {
      padding: 0;
      font-size: 0.68rem;
    }
  }

  @media (max-width: 480px) {
    :global(.header-actions .compact-select) {
      padding: 0.45rem 1.25rem 0.45rem 0.55rem;
    }
  }
</style>
