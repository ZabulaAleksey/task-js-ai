import { describe, expect, it } from "vitest";
import { createDemoSnapshot } from "$lib/demo/market";
import { parseRealtimeEvent } from "./realtime";

describe("realtime protocol", () => {
  it("accepts the versioned demo snapshot", () => {
    expect(parseRealtimeEvent(createDemoSnapshot())).not.toBeNull();
  });

  it("rejects malformed or future events", () => {
    expect(parseRealtimeEvent({ type: "quote.update" })).toBeNull();
    expect(
      parseRealtimeEvent({
        version: 2,
        sequence: 1,
        serverTime: Date.now(),
        type: "heartbeat",
        data: {},
      }),
    ).toBeNull();
  });
});
