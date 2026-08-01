import { describe, expect, it } from "vitest";
import { preferencesSchema } from "./preferences";

describe("terminal preferences", () => {
  it("accepts bounded preferences", () => {
    expect(
      preferencesSchema.safeParse({
        preferredSymbol: "EURUSD",
        preferredTimeframe: "1m",
        maxCandles: 300,
      }).success,
    ).toBe(true);
  });

  it("rejects an unbounded candle history", () => {
    expect(
      preferencesSchema.safeParse({
        preferredSymbol: "EURUSD",
        preferredTimeframe: "1m",
        maxCandles: 5_000,
      }).success,
    ).toBe(false);
  });
});
