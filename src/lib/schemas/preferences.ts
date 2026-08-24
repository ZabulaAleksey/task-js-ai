import { z } from "zod";

export const preferencesSchema = z.object({
  preferredSymbol: z.enum(["EURUSD", "GBPUSD", "USDJPY"]),
  preferredTimeframe: z.enum(["1m", "5m", "15m", "1h"]),
  maxCandles: z.number().int().min(100).max(500),
});

export type Preferences = z.infer<typeof preferencesSchema>;
