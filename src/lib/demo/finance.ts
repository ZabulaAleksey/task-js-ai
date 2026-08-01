import type { FinanceData } from "$lib/types";

export function createDemoFinanceData(now = new Date()): FinanceData {
  return {
    financeResult: [
      {
        transactions: [
          { type: "paid", amount: "2480.75", currency: "USD" },
          { type: "paid", amount: "935.40", currency: "EUR" },
          { type: "paid", amount: "714.20", currency: "GBP" },
          { type: "pending", amount: "1250", currency: "USD" },
          { type: "rejected", amount: "300", currency: "EUR" },
        ],
        address: {
          city: "Kyiv",
          street: "Market Street",
          houseNumber: 21,
        },
      },
      [
        { amount: "1260.50", currency: "USD" },
        { amount: "480.25", currency: "EUR" },
        { amount: "18250", currency: "UAH" },
      ],
    ],
    currencyData: {
      date: now.toISOString().slice(0, 10),
      base: "USD",
      rates: {
        USD: "1",
        EUR: "0.9235",
        GBP: "0.7812",
        UAH: "41.18",
      },
    },
  };
}
