import Decimal from "decimal.js-light";
import { z } from "zod";

export const apiKeySchema = z
  .string()
  .trim()
  .min(1, "apiKeyRequired")
  .max(512, "apiKeyTooLong");

export const currencyCodeSchema = z
  .string()
  .trim()
  .toUpperCase()
  .regex(/^[A-Z]{3}$/, "invalidCurrency");

const rateCodeSchema = z
  .string()
  .trim()
  .toUpperCase()
  .regex(/^[A-Z0-9.$_-]{1,30}$/, "invalidAsset");

const apiDateSchema = z
  .string()
  .trim()
  .refine((value) => !Number.isNaN(Date.parse(value)), "invalidDate")
  .transform((value) => new Date(value).toISOString().slice(0, 10));

export const decimalStringSchema = z
  .union([z.string(), z.number().finite()])
  .transform(String)
  .refine((value) => /^-?\d+(?:\.\d+)?$/.test(value), "invalidMoney");

const positiveDecimalStringSchema = decimalStringSchema.refine(
  (value) => new Decimal(value).greaterThan(0),
  "invalidRate",
);

const transactionSchema = z.object({
  type: z.enum(["paid", "pending", "rejected"]),
  amount: decimalStringSchema,
  currency: currencyCodeSchema,
});

export const firstFinanceSourceSchema = z.object({
  transactions: z.array(transactionSchema),
  address: z.object({
    city: z.string(),
    street: z.string(),
    houseNumber: z.number().finite(),
  }),
});

export const secondFinanceSourceSchema = z
  .array(z.string())
  .transform((payments, context) =>
    payments.map((payment) => {
      const match = payment.trim().match(/^(-?\d+(?:\.\d+)?)\s+([A-Za-z]{3})$/);
      if (!match) {
        context.addIssue({
          code: "custom",
          message: `Invalid payment: ${payment}`,
        });
        return { amount: "0", currency: "USD" };
      }
      return { amount: match[1], currency: match[2].toUpperCase() };
    }),
  );

export const currencyDataSchema = z.object({
  date: apiDateSchema,
  base: currencyCodeSchema,
  rates: z.record(rateCodeSchema, positiveDecimalStringSchema),
});

export const financeDataSchema = z.object({
  financeResult: z.tuple([firstFinanceSourceSchema, secondFinanceSourceSchema]),
  currencyData: currencyDataSchema,
});

export type FirstFinanceSource = z.infer<typeof firstFinanceSourceSchema>;
export type SecondFinanceSource = z.infer<typeof secondFinanceSourceSchema>;
export type CurrencyData = z.infer<typeof currencyDataSchema>;
export type FinanceData = z.infer<typeof financeDataSchema>;
