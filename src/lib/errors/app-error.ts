export type AppErrorCode =
  | "invalidApiResponse"
  | "requestFailed"
  | "missingCurrencyApiKey"
  | "missingCurrencyRate"
  | "invalidApiKey"
  | "timeout"
  | "rateLimited"
  | "unknownError";

export class AppError extends Error {
  constructor(
    public readonly code: AppErrorCode,
    public readonly values: Record<string, string> = {},
    options?: ErrorOptions,
  ) {
    super(code, options);
    this.name = "AppError";
  }
}

export function serializeAppError(error: unknown) {
  const appError =
    error instanceof AppError
      ? error
      : new AppError("unknownError", {}, { cause: error });

  return { code: appError.code, values: appError.values };
}
