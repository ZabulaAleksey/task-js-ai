import type { CurrencyData, FinanceResult } from "$lib/types";
import { decimal, roundMoney } from "./money";

export function calculateFinanceTotal(
  [first, second]: FinanceResult,
  currencyData: CurrencyData,
): string {
  const convertToBase = (amount: string, currency: string) => {
    const value = decimal(amount);
    return currency === currencyData.base
      ? value
      : value.dividedBy(decimal(currencyData.rates[currency]));
  };

  const firstTotal = first.transactions.reduce(
    (total, transaction) =>
      transaction.type === "paid"
        ? total.plus(convertToBase(transaction.amount, transaction.currency))
        : total,
    decimal("0"),
  );

  const secondTotal = second.reduce(
    (total, payment) =>
      total.plus(convertToBase(payment.amount, payment.currency)),
    decimal("0"),
  );

  return roundMoney(firstTotal.plus(secondTotal), currencyData.base);
}
