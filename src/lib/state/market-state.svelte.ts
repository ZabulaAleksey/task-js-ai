import { getContext, setContext } from "svelte";
import type { RealtimeEvent } from "$lib/schemas/realtime";
import type {
  CalendarEvent,
  Candle,
  ConnectionStatus,
  LiveBalance,
  NewsItem,
  Quote,
  Timeframe,
} from "$lib/types";

const marketContext = Symbol("market");
const MAX_CANDLES = 500;
const MAX_NEWS = 100;
const MAX_CALENDAR_EVENTS = 200;

function candleKey(symbol: string, timeframe: Timeframe) {
  return `${symbol}:${timeframe}`;
}

export class MarketState {
  private reconnectHandler: (() => void) | null = null;
  status = $state<ConnectionStatus>("idle");
  quotes = $state<Record<string, Quote>>({});
  candles = $state<Record<string, Candle[]>>({});
  balances = $state<LiveBalance[]>([]);
  news = $state<NewsItem[]>([]);
  calendar = $state<CalendarEvent[]>([]);
  lastSequence = $state(0);
  lastEventAt = $state<number | null>(null);
  invalidMessages = $state(0);

  setStatus(status: ConnectionStatus) {
    this.status = status;
  }

  noteInvalidMessage() {
    this.invalidMessages += 1;
  }

  setReconnectHandler(handler: (() => void) | null) {
    this.reconnectHandler = handler;
  }

  reconnect() {
    this.reconnectHandler?.();
  }

  apply(event: RealtimeEvent) {
    if (event.type !== "snapshot" && event.sequence <= this.lastSequence)
      return;
    this.lastSequence = Math.max(this.lastSequence, event.sequence);
    this.lastEventAt = event.serverTime;

    switch (event.type) {
      case "snapshot": {
        this.quotes = Object.fromEntries(
          event.data.quotes.map((quote) => [quote.symbol, quote]),
        );
        const grouped: Record<string, Candle[]> = {};
        for (const candle of event.data.candles) {
          const key = candleKey(candle.symbol, candle.timeframe);
          (grouped[key] ??= []).push(candle);
        }
        this.candles = Object.fromEntries(
          Object.entries(grouped).map(([key, values]) => [
            key,
            values
              .sort((a, b) => a.timestamp - b.timestamp)
              .slice(-MAX_CANDLES),
          ]),
        );
        this.balances = event.data.balances;
        this.news = event.data.news.slice(0, MAX_NEWS);
        this.calendar = event.data.calendar
          .sort((a, b) => a.scheduledAt - b.scheduledAt)
          .slice(0, MAX_CALENDAR_EVENTS);
        break;
      }
      case "quote.update":
        this.quotes[event.data.symbol] = event.data;
        break;
      case "candle.update": {
        const key = candleKey(event.data.symbol, event.data.timeframe);
        const values = this.candles[key] ?? [];
        const index = values.findIndex(
          (candle) => candle.timestamp === event.data.timestamp,
        );
        if (index >= 0) values[index] = event.data;
        else values.push(event.data);
        this.candles[key] = values.slice(-MAX_CANDLES);
        break;
      }
      case "balance.update": {
        const index = this.balances.findIndex(
          (balance) => balance.currency === event.data.currency,
        );
        if (index >= 0) this.balances[index] = event.data;
        else this.balances.push(event.data);
        break;
      }
      case "news.create":
        this.news = [
          event.data,
          ...this.news.filter((item) => item.id !== event.data.id),
        ].slice(0, MAX_NEWS);
        break;
      case "calendar.update": {
        const index = this.calendar.findIndex(
          (item) => item.id === event.data.id,
        );
        if (index >= 0) this.calendar[index] = event.data;
        else this.calendar.push(event.data);
        this.calendar = this.calendar
          .sort((a, b) => a.scheduledAt - b.scheduledAt)
          .slice(0, MAX_CALENDAR_EVENTS);
        break;
      }
      case "heartbeat":
        break;
    }
  }

  candlesFor(symbol: string, timeframe: Timeframe) {
    return this.candles[candleKey(symbol, timeframe)] ?? [];
  }
}

export function provideMarketState() {
  return setContext(marketContext, new MarketState());
}

export function useMarketState() {
  return getContext<MarketState>(marketContext);
}
