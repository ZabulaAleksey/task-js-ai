# Northstar Finance Terminal contract profile

Use this profile only for the repository that contains `src/lib/schemas/finance.ts` and `src/routes/api/portfolio/+server.ts`.

## REST `/api/portfolio`

- Expect JSON and `Cache-Control: no-store`.
- Expect top-level `financeResult` and `currencyData`.
- Treat `currencyData.base` and transaction/payment currencies as ISO 4217 codes.
- Require a positive decimal rate for every used non-base currency.
- Prefer a base rate equal to `1` when the base key is present.
- Expect financial decimals as JSON strings to preserve exact representation.

## Important schema direction

`secondFinanceSourceSchema` accepts upstream `string[]` values such as `"125 USD"` and transforms them into normalized `{ amount, currency }[]` objects. `FinanceData` is the transformed output type, and the current REST route emits that output.

Do not claim that normalized objects are intrinsically invalid. Report a contract ambiguity when the public endpoint is described or tested with the same input schema, because the emitted output cannot be parsed again by that schema. Recommend one of:

1. define and export a dedicated response schema for normalized `FinanceData`;
2. expose the raw upstream form and document it explicitly; or
3. make the transformation idempotent only if both representations are intentionally supported.

## Realtime

- Expect version `1`, nonnegative monotonic `sequence`, and millisecond timestamps.
- Expect uppercase six-letter FX symbols whose two three-letter legs are active/allowed codes.
- Require `ask >= bid`.
- Require `low <= open/close <= high`.
- Validate balances, news currencies, and calendar currencies as active/allowed codes.

## Known coverage boundary

The repository has an internal demo REST endpoint and an optional external WebSocket provider. When `PUBLIC_WS_URL` is unset, clearly state that the report covers demo realtime fixtures rather than a production server.
