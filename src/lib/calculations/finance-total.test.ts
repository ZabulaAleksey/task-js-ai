import { describe, expect, it } from "vitest";
import type { CurrencyData, FinanceResult } from "$lib/types";
import { calculateCurrencyTotals } from "./currency-totals";
import { calculateFinanceTotal } from "./finance-total";
import { decimal, roundMoney } from "./money";

const financeResult: FinanceResult = [
  {
    transactions: [
      { type: "paid", amount: "100", currency: "USD" },
      { type: "paid", amount: "50", currency: "EUR" },
      { type: "pending", amount: "999", currency: "USD" },
    ],
    address: { city: "Kyiv", street: "Test", houseNumber: 1 },
  },
  [{ amount: "25", currency: "EUR" }],
];

const currencyData: CurrencyData = {
  date: "2026-08-02",
  base: "USD",
  rates: { USD: "1", EUR: "0.5" },
};

describe("finance calculations", () => {
  it("ignores unpaid transactions and converts without intermediate rounding", () => {
    expect(calculateFinanceTotal(financeResult, currencyData)).toBe("250.00");
  });

  it("groups source amounts by currency", () => {
    expect(calculateCurrencyTotals(financeResult)).toEqual([
      { currency: "EUR", amount: "75" },
      { currency: "USD", amount: "100" },
    ]);
  });

  it("uses banker's rounding for the final amount", () => {
    expect(roundMoney(decimal("2.345"), "USD")).toBe("2.34");
    expect(roundMoney(decimal("2.355"), "USD")).toBe("2.36");
  });
});
