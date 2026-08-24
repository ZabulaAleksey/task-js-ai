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
  const height = 320;

  function draw(values: Candle[]) {
    if (!canvas || !container || width < 40 || values.length === 0) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    const context = canvas.getContext("2d");
    if (!context) return;
    context.scale(ratio, ratio);
    const styles = getComputedStyle(container);
    const grid = styles.getPropertyValue("--chart-grid").trim() || "#26364a";
    const text = styles.getPropertyValue("--chart-text").trim() || "#8ea1b8";
    const rise = styles.getPropertyValue("--price-up").trim() || "#25d695";
    const fall = styles.getPropertyValue("--price-down").trim() || "#ff667d";
    const background =
      styles.getPropertyValue("--chart-bg").trim() || "#0b1726";
    context.fillStyle = background;
    context.fillRect(0, 0, width, height);

    const visible = values.slice(-72);
    const maximum = Math.max(...visible.map((item) => Number(item.high)));
    const minimum = Math.min(...visible.map((item) => Number(item.low)));
    const range = Math.max(maximum - minimum, maximum * 0.0001);
    const padding = { top: 18, right: 58, bottom: 28, left: 12 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;
    const toY = (price: number) =>
      padding.top + ((maximum - price) / range) * plotHeight;

    context.lineWidth = 1;
    context.font = "11px ui-monospace, SFMono-Regular, Menlo, monospace";
    context.textAlign = "left";
    context.textBaseline = "middle";
    for (let index = 0; index <= 4; index += 1) {
      const y = padding.top + (plotHeight / 4) * index;
      const price = maximum - (range / 4) * index;
      context.strokeStyle = grid;
      context.beginPath();
      context.moveTo(padding.left, y);
      context.lineTo(width - padding.right + 8, y);
      context.stroke();
      context.fillStyle = text;
      context.fillText(
        price.toFixed(price > 20 ? 3 : 5),
        width - padding.right + 13,
        y,
      );
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
  }

  onMount(() => {
    const observer = new ResizeObserver(([entry]) => {
      width = entry.contentRect.width;
    });
    if (!container) return;
    observer.observe(container);
    return () => observer.disconnect();
  });

  $effect(() => {
    const values = candles;
    if (!width) return;
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
