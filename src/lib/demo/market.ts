import type {
  CalendarEvent,
  Candle,
  LiveBalance,
  NewsItem,
  Quote,
  Timeframe,
} from "$lib/types";
import type { RealtimeEvent } from "$lib/schemas/realtime";

const minute = 60_000;
const prices: Record<string, number> = {
  EURUSD: 1.08372,
  GBPUSD: 1.27143,
  USDJPY: 148.624,
};

function precision(symbol: string) {
  return symbol.endsWith("JPY") ? 3 : 5;
}

function buildCandles(
  symbol: string,
  startPrice: number,
  count = 96,
  timeframe: Timeframe = "1m",
  now = Date.now(),
): Candle[] {
  const step = {
    "1m": minute,
    "5m": 5 * minute,
    "15m": 15 * minute,
    "1h": 60 * minute,
  }[timeframe];
  const digits = precision(symbol);
  let previous = startPrice * 0.998;

  return Array.from({ length: count }, (_, index) => {
    const wave = Math.sin(index / 6) * startPrice * 0.00055;
    const drift = index * startPrice * 0.0000025;
    const open = previous;
    const close = startPrice * 0.998 + wave + drift;
    const high =
      Math.max(open, close) + startPrice * (0.00016 + (index % 3) * 0.00003);
    const low =
      Math.min(open, close) - startPrice * (0.00012 + (index % 2) * 0.00004);
    previous = close;

    return {
      symbol,
      timeframe,
      timestamp: Math.floor(now / step) * step - (count - index - 1) * step,
      open: open.toFixed(digits),
      high: high.toFixed(digits),
      low: low.toFixed(digits),
      close: close.toFixed(digits),
      volume: String(640 + ((index * 47) % 720)),
      closed: index !== count - 1,
    };
  });
}

function buildQuotes(now: number): Quote[] {
  return Object.entries(prices).map(([symbol, price], index) => {
    const digits = precision(symbol);
    const spread = symbol.endsWith("JPY") ? 0.012 : 0.00012;
    return {
      symbol,
      bid: (price - spread / 2).toFixed(digits),
      ask: (price + spread / 2).toFixed(digits),
      changePercent: [0.34, -0.18, 0.27][index].toFixed(2),
      timestamp: now,
    };
  });
}

function buildBalances(now: number): LiveBalance[] {
  return [
    {
      currency: "USD",
      available: "12840.55",
      reserved: "950.00",
      convertedUsd: "13790.55",
      timestamp: now,
    },
    {
      currency: "EUR",
      available: "4260.20",
      reserved: "320.00",
      convertedUsd: "4960.70",
      timestamp: now,
    },
    {
      currency: "GBP",
      available: "1840.75",
      reserved: "0",
      convertedUsd: "2356.82",
      timestamp: now,
    },
  ];
}

function buildNews(now: number): NewsItem[] {
  return [
    {
      id: "news-fed-minutes",
      headline: "Dollar steadies as traders position for central-bank minutes",
      summary:
        "Short-dated yields hold their range while markets reassess the path of policy rates.",
      source: "Northstar Wire",
      currencies: ["USD", "EUR"],
      publishedAt: now - 8 * minute,
      importance: "high",
    },
    {
      id: "news-sterling",
      headline: "Sterling volatility eases ahead of services data",
      summary:
        "Options markets show lower near-term demand for protection after a quiet European session.",
      source: "Market Desk",
      currencies: ["GBP"],
      publishedAt: now - 24 * minute,
      importance: "medium",
    },
    {
      id: "news-yen",
      headline: "Yen firms as rate-differential trade pauses",
      summary:
        "USD/JPY retreats from the session high as regional bond yields move lower.",
      source: "Asia Brief",
      currencies: ["JPY", "USD"],
      publishedAt: now - 51 * minute,
      importance: "low",
    },
  ];
}

function buildCalendar(now: number): CalendarEvent[] {
  return [
    {
      id: "calendar-eu-cpi",
      title: "Consumer Price Index",
      currency: "EUR",
      country: "Eurozone",
      scheduledAt: now + 42 * minute,
      importance: "high",
      previous: "2.4%",
      forecast: "2.3%",
    },
    {
      id: "calendar-us-jolts",
      title: "JOLTS Job Openings",
      currency: "USD",
      country: "United States",
      scheduledAt: now + 132 * minute,
      importance: "high",
      previous: "7.18M",
      forecast: "7.22M",
    },
    {
      id: "calendar-gb-pmi",
      title: "Services PMI",
      currency: "GBP",
      country: "United Kingdom",
      scheduledAt: now + 22 * 60 * minute,
      importance: "medium",
      previous: "52.8",
      forecast: "52.6",
    },
  ];
}

export function createDemoSnapshot(
  sequence = 1,
  now = Date.now(),
): RealtimeEvent {
  return {
    version: 1,
    sequence,
    serverTime: now,
    type: "snapshot",
    data: {
      quotes: buildQuotes(now),
      candles: Object.entries(prices).flatMap(([symbol, price]) =>
        (["1m", "5m", "15m", "1h"] as Timeframe[]).flatMap((timeframe) =>
          buildCandles(symbol, price, 96, timeframe, now),
        ),
      ),
      balances: buildBalances(now),
      news: buildNews(now),
      calendar: buildCalendar(now),
    },
  };
}

export function createDemoQuote(
  symbol: string,
  tick: number,
  sequence: number,
  now = Date.now(),
): RealtimeEvent {
  const base = prices[symbol];
  const digits = precision(symbol);
  const movement = Math.sin(tick / 3 + symbol.length) * base * 0.00012;
  const midpoint = base + movement;
  const spread = symbol.endsWith("JPY") ? 0.012 : 0.00012;
  return {
    version: 1,
    sequence,
    serverTime: now,
    type: "quote.update",
    data: {
      symbol,
      bid: (midpoint - spread / 2).toFixed(digits),
      ask: (midpoint + spread / 2).toFixed(digits),
      changePercent: (Math.sin(tick / 9 + symbol.length) * 0.42).toFixed(2),
      timestamp: now,
    },
  };
}

export function createDemoCandle(
  symbol: string,
  tick: number,
  sequence: number,
  now = Date.now(),
): RealtimeEvent {
  const base = prices[symbol];
  const digits = precision(symbol);
  const timestamp = Math.floor(now / minute) * minute;
  const open = base + Math.sin((tick - 1) / 3 + symbol.length) * base * 0.00012;
  const close = base + Math.sin(tick / 3 + symbol.length) * base * 0.00012;
  const padding = base * 0.00008;
  return {
    version: 1,
    sequence,
    serverTime: now,
    type: "candle.update",
    data: {
      symbol,
      timeframe: "1m",
      timestamp,
      open: open.toFixed(digits),
      high: (Math.max(open, close) + padding).toFixed(digits),
      low: (Math.min(open, close) - padding).toFixed(digits),
      close: close.toFixed(digits),
      volume: String(780 + tick * 13),
      closed: false,
    },
  };
}
