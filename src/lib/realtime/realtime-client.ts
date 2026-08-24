import {
  createDemoCandle,
  createDemoQuote,
  createDemoSnapshot,
} from "$lib/demo/market";
import { parseRealtimeEvent, type RealtimeEvent } from "$lib/schemas/realtime";
import type { MarketState } from "$lib/state/market-state.svelte";

const symbols = ["EURUSD", "GBPUSD", "USDJPY"];

export class RealtimeClient {
  private socket: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private staleTimer: ReturnType<typeof setInterval> | null = null;
  private demoTimer: ReturnType<typeof setInterval> | null = null;
  private manuallyClosed = false;
  private reconnectAttempt = 0;
  private demoTick = 0;
  private sequence = 1;
  private animationFrame: number | null = null;
  private latestEvents = new Map<string, RealtimeEvent>();
  private queuedEvents: RealtimeEvent[] = [];

  constructor(
    private readonly state: MarketState,
    private readonly endpoint?: string,
  ) {}

  start() {
    this.manuallyClosed = false;
    this.startStaleMonitor();
    if (!this.endpoint) {
      this.startDemo();
      return;
    }
    this.connect();
  }

  stop() {
    this.manuallyClosed = true;
    this.clearTimers();
    this.socket?.close(1000, "Client closed");
    this.socket = null;
    if (this.animationFrame !== null) cancelAnimationFrame(this.animationFrame);
    this.animationFrame = null;
    this.latestEvents.clear();
    this.queuedEvents = [];
    this.state.setStatus("offline");
  }

  reconnectNow() {
    this.manuallyClosed = false;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.socket?.close();
    if (this.endpoint) this.connect();
    else this.startDemo();
  }

  private startDemo() {
    if (this.demoTimer) clearInterval(this.demoTimer);
    this.state.setStatus("demo");
    this.enqueue(createDemoSnapshot(this.sequence++));
    this.demoTimer = setInterval(() => {
      this.demoTick += 1;
      for (const symbol of symbols) {
        this.enqueue(createDemoQuote(symbol, this.demoTick, this.sequence++));
        this.enqueue(createDemoCandle(symbol, this.demoTick, this.sequence++));
      }
    }, 1_000);
  }

  private connect() {
    if (this.manuallyClosed || !this.endpoint) return;
    let url: URL;
    try {
      url = new URL(this.endpoint);
      const local =
        url.hostname === "localhost" || url.hostname === "127.0.0.1";
      if (url.protocol !== "wss:" && !(local && url.protocol === "ws:")) {
        throw new Error("Realtime endpoint must use WSS");
      }
    } catch {
      this.state.setStatus("offline");
      return;
    }

    this.state.setStatus(this.reconnectAttempt ? "reconnecting" : "connecting");
    const socket = new WebSocket(url);
    this.socket = socket;

    socket.addEventListener("open", () => {
      if (this.socket !== socket) return;
      this.reconnectAttempt = 0;
      this.state.setStatus("online");
      socket.send(
        JSON.stringify({
          type: "subscribe",
          symbols,
          timeframes: ["1m", "5m", "15m", "1h"],
          channels: ["quotes", "candles", "balances", "news", "calendar"],
          afterSequence: this.state.lastSequence,
        }),
      );
      if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(
            JSON.stringify({
              type: "ping",
              lastSequence: this.state.lastSequence,
            }),
          );
        }
      }, 25_000);
    });

    socket.addEventListener("message", (message) => {
      let payload: unknown;
      try {
        payload = JSON.parse(String(message.data));
      } catch {
        this.state.noteInvalidMessage();
        return;
      }
      const event = parseRealtimeEvent(payload);
      if (!event) {
        this.state.noteInvalidMessage();
        return;
      }
      this.enqueue(event);
    });

    socket.addEventListener("close", () => {
      if (this.socket !== socket) return;
      this.socket = null;
      if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
      if (!this.manuallyClosed) this.scheduleReconnect();
    });

    socket.addEventListener("error", () => socket.close());
  }

  private scheduleReconnect() {
    this.reconnectAttempt += 1;
    this.state.setStatus("reconnecting");
    const base = Math.min(30_000, 750 * 2 ** (this.reconnectAttempt - 1));
    const delay = base + Math.random() * base * 0.25;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  private enqueue(event: RealtimeEvent) {
    if (event.type === "quote.update") {
      this.latestEvents.set(`quote:${event.data.symbol}`, event);
    } else if (event.type === "candle.update") {
      this.latestEvents.set(
        `candle:${event.data.symbol}:${event.data.timeframe}`,
        event,
      );
    } else {
      this.queuedEvents.push(event);
    }

    if (this.animationFrame === null) {
      this.animationFrame = requestAnimationFrame(() => this.flush());
    }
  }

  private flush() {
    const events = [...this.queuedEvents, ...this.latestEvents.values()].sort(
      (left, right) => left.sequence - right.sequence,
    );
    this.queuedEvents = [];
    this.latestEvents.clear();
    this.animationFrame = null;
    events.forEach((event) => this.state.apply(event));
  }

  private startStaleMonitor() {
    if (this.staleTimer) clearInterval(this.staleTimer);
    this.staleTimer = setInterval(() => {
      if (
        this.state.status === "online" &&
        this.state.lastEventAt &&
        Date.now() - this.state.lastEventAt > 15_000
      ) {
        this.state.setStatus("stale");
      }
    }, 5_000);
  }

  private clearTimers() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    if (this.staleTimer) clearInterval(this.staleTimer);
    if (this.demoTimer) clearInterval(this.demoTimer);
    this.reconnectTimer = null;
    this.heartbeatTimer = null;
    this.staleTimer = null;
    this.demoTimer = null;
  }
}
