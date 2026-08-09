<script lang="ts">
  import { onMount } from "svelte";
  import type { Candle } from "$lib/types";

  let {
    candles,
    label,
    summary,
  }: {
    candles: Candle[];
    label: string;
    summary: string;
  } = $props();
  let canvas = $state<HTMLCanvasElement>();
  let container = $state<HTMLElement>();
  let width = $state(0);
  let height = $state(0);

  function draw(values: Candle[]) {
    if (
      !canvas ||
      !container ||
      width < 40 ||
      height < 40 ||
      values.length === 0
    )
      return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    const context = canvas.getContext("2d");
    if (!context) return;
    context.scale(ratio, ratio);
    const styles = getComputedStyle(container);
    const grid = styles.getPropertyValue("--chart-grid").trim() || "#26364a";
    const text = styles.getPropertyValue("--chart-text").trim() || "#8ea1b8";
    const rise = styles.getPropertyValue("--price-up").trim() || "#c8ff32";
    const fall = styles.getPropertyValue("--price-down").trim() || "#ff6655";
    const background =
      styles.getPropertyValue("--chart-bg").trim() || "#06121d";
    const foreground = styles.getPropertyValue("--text").trim() || "#f4f7f2";
    context.fillStyle = background;
    context.fillRect(0, 0, width, height);

    const visible = values.slice(-72);
    const maximum = Math.max(...visible.map((item) => Number(item.high)));
    const minimum = Math.min(...visible.map((item) => Number(item.low)));
    const range = Math.max(maximum - minimum, maximum * 0.0001);
    const padding = { top: 24, right: 74, bottom: 38, left: 14 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;
    const toY = (price: number) =>
      padding.top + ((maximum - price) / range) * plotHeight;

    context.lineWidth = 1;
    context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
    context.textBaseline = "middle";
    for (let index = 0; index <= 5; index += 1) {
      const y = padding.top + (plotHeight / 5) * index;
      const price = maximum - (range / 5) * index;
      context.strokeStyle = grid;
      context.setLineDash([4, 5]);
      context.beginPath();
      context.moveTo(padding.left, y);
      context.lineTo(width - padding.right + 8, y);
      context.stroke();
      context.setLineDash([]);
      context.fillStyle = text;
      context.textAlign = "left";
      context.fillText(
        price.toFixed(price > 20 ? 3 : 5),
        width - padding.right + 14,
        y,
      );
    }

    for (let index = 0; index <= 5; index += 1) {
      const x = padding.left + (plotWidth / 5) * index;
      context.strokeStyle = grid;
      context.setLineDash([3, 7]);
      context.beginPath();
      context.moveTo(x, padding.top);
      context.lineTo(x, height - padding.bottom);
      context.stroke();
      context.setLineDash([]);
    }

    const step = plotWidth / visible.length;
    const bodyWidth = Math.max(2, Math.min(8, step * 0.58));
    visible.forEach((candle, index) => {
      const open = Number(candle.open);
      const high = Number(candle.high);
      const low = Number(candle.low);
      const close = Number(candle.close);
      const x = padding.left + step * index + step / 2;
      const color = close >= open ? rise : fall;
      context.strokeStyle = color;
      context.fillStyle = color;
      context.beginPath();
      context.moveTo(x, toY(high));
      context.lineTo(x, toY(low));
      context.stroke();
      const top = Math.min(toY(open), toY(close));
      const bodyHeight = Math.max(1.5, Math.abs(toY(open) - toY(close)));
      context.fillRect(x - bodyWidth / 2, top, bodyWidth, bodyHeight);
    });

    const latest = visible.at(-1);
    if (latest) {
      const latestPrice = Number(latest.close);
      const latestY = toY(latestPrice);
      const priceLabel = latestPrice.toFixed(latestPrice > 20 ? 3 : 5);
      context.strokeStyle = rise;
      context.setLineDash([4, 4]);
      context.beginPath();
      context.moveTo(padding.left, latestY);
      context.lineTo(width - padding.right + 8, latestY);
      context.stroke();
      context.setLineDash([]);
      context.fillStyle = rise;
      context.fillRect(width - padding.right + 8, latestY - 11, 62, 22);
      context.fillStyle = background;
      context.font = "700 11px ui-monospace, SFMono-Regular, Menlo, monospace";
      context.textAlign = "center";
      context.fillText(priceLabel, width - padding.right + 39, latestY);
    }

    context.fillStyle = text;
    context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
    context.textAlign = "center";
    context.textBaseline = "bottom";
    const labelCount = Math.min(6, visible.length);
    for (let index = 0; index < labelCount; index += 1) {
      const candleIndex = Math.round(
        (index * (visible.length - 1)) / Math.max(1, labelCount - 1),
      );
      const candle = visible[candleIndex];
      const x = padding.left + step * candleIndex + step / 2;
      const time = new Intl.DateTimeFormat(undefined, {
        hour: "2-digit",
        minute: "2-digit",
      }).format(candle.timestamp);
      context.fillText(time, x, height - 7);
    }

    context.strokeStyle = foreground;
    context.globalAlpha = 0.4;
    context.beginPath();
    context.moveTo(width - padding.right + 8, padding.top);
    context.lineTo(width - padding.right + 8, height - padding.bottom);
    context.stroke();
    context.globalAlpha = 1;
  }

  onMount(() => {
    const observer = new ResizeObserver(([entry]) => {
      width = Math.round(entry.contentRect.width);
      height = Math.round(entry.contentRect.height);
    });
    if (!container) return;
    observer.observe(container);
    return () => observer.disconnect();
  });

  $effect(() => {
    const values = candles;
    if (!width || !height) return;
    const frame = requestAnimationFrame(() => draw(values));
    return () => cancelAnimationFrame(frame);
  });
</script>

<figure class="chart-canvas" bind:this={container} aria-label={label}>
  {#if candles.length}
    <canvas bind:this={canvas} aria-hidden="true"></canvas>
    <figcaption class="visually-hidden">{summary}</figcaption>
  {:else}
    <div class="chart-skeleton" aria-label="Loading chart">
      <span></span><span></span><span></span><span></span>
    </div>
  {/if}
</figure>
