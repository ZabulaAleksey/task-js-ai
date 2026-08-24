import Decimal from "decimal.js-light";

Decimal.set({ precision: 40, rounding: Decimal.ROUND_HALF_EVEN });

export const decimal = (value: string | number) => new Decimal(value);

export function currencyFractionDigits(currency: string): number {
  return (
    new Intl.NumberFormat("en", {
      style: "currency",
      currency,
    }).resolvedOptions().maximumFractionDigits ?? 2
  );
}

export function roundMoney(value: Decimal, currency: string): string {
  const digits = currencyFractionDigits(currency);
  return value.toDecimalPlaces(digits, Decimal.ROUND_HALF_EVEN).toFixed(digits);
}
