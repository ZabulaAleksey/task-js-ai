import type { FinanceResult } from "$lib/types";
import { decimal } from "./money";

export type CurrencyTotal = { currency: string; amount: string };

export function calculateCurrencyTotals([
  first,
  second,
]: FinanceResult): CurrencyTotal[] {
  const totals = new Map<string, string>();

  const add = (amount: string, currency: string) => {
    const next = decimal(totals.get(currency) ?? "0").plus(decimal(amount));
    totals.set(currency, next.toString());
  };

  first.transactions.forEach((transaction) => {
    if (transaction.type === "paid")
      add(transaction.amount, transaction.currency);
  });
  second.forEach(({ amount, currency }) => add(amount, currency));

  return [...totals]
    .map(([currency, amount]) => ({ currency, amount }))
    .sort((left, right) => left.currency.localeCompare(right.currency));
}
