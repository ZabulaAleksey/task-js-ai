import { z } from "zod";
import { decimalStringSchema } from "./finance";

const timestampSchema = z.number().int().nonnegative();
const importanceSchema = z.enum(["low", "medium", "high"]);
const timeframeSchema = z.enum(["1m", "5m", "15m", "1h"]);

export const quoteSchema = z.object({
  symbol: z.string().regex(/^[A-Z]{6}$/),
  bid: decimalStringSchema,
  ask: decimalStringSchema,
  changePercent: decimalStringSchema,
  timestamp: timestampSchema,
});

export const candleSchema = z.object({
  symbol: z.string().regex(/^[A-Z]{6}$/),
  timeframe: timeframeSchema,
  timestamp: timestampSchema,
  open: decimalStringSchema,
  high: decimalStringSchema,
  low: decimalStringSchema,
  close: decimalStringSchema,
  volume: decimalStringSchema,
  closed: z.boolean(),
});

export const liveBalanceSchema = z.object({
  currency: z.string().regex(/^[A-Z]{3}$/),
  available: decimalStringSchema,
  reserved: decimalStringSchema,
  convertedUsd: decimalStringSchema,
  timestamp: timestampSchema,
});

export const newsItemSchema = z.object({
  id: z.string().min(1),
  headline: z.string().min(1).max(300),
  summary: z.string().max(1200),
  source: z.string().min(1).max(100),
  currencies: z.array(z.string().regex(/^[A-Z]{3}$/)).max(12),
  publishedAt: timestampSchema,
  importance: importanceSchema,
});

export const calendarEventSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1).max(300),
  currency: z.string().regex(/^[A-Z]{3}$/),
  country: z.string().min(2).max(80),
  scheduledAt: timestampSchema,
  importance: importanceSchema,
  previous: z.string().optional(),
  forecast: z.string().optional(),
  actual: z.string().optional(),
});

const envelope = {
  version: z.literal(1),
  sequence: z.number().int().nonnegative(),
  serverTime: timestampSchema,
};

export const realtimeEventSchema = z.discriminatedUnion("type", [
  z.object({
    ...envelope,
    type: z.literal("snapshot"),
    data: z.object({
      quotes: z.array(quoteSchema),
      candles: z.array(candleSchema),
      balances: z.array(liveBalanceSchema),
      news: z.array(newsItemSchema),
      calendar: z.array(calendarEventSchema),
    }),
  }),
  z.object({ ...envelope, type: z.literal("quote.update"), data: quoteSchema }),
  z.object({
    ...envelope,
    type: z.literal("candle.update"),
    data: candleSchema,
  }),
  z.object({
    ...envelope,
    type: z.literal("balance.update"),
    data: liveBalanceSchema,
  }),
  z.object({
    ...envelope,
    type: z.literal("news.create"),
    data: newsItemSchema,
  }),
  z.object({
    ...envelope,
    type: z.literal("calendar.update"),
    data: calendarEventSchema,
  }),
  z.object({
    ...envelope,
    type: z.literal("heartbeat"),
    data: z.object({ connectionId: z.string().optional() }),
  }),
]);

export type RealtimeEvent = z.infer<typeof realtimeEventSchema>;

export function parseRealtimeEvent(payload: unknown): RealtimeEvent | null {
  const result = realtimeEventSchema.safeParse(payload);
  return result.success ? result.data : null;
}
