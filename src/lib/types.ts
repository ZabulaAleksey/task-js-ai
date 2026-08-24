export type Language = "en" | "ru" | "uk";
export type Theme = "light" | "dark";
export type Timeframe = "1m" | "5m" | "15m" | "1h";
export type ConnectionStatus =
  | "idle"
  | "connecting"
  | "online"
  | "reconnecting"
  | "stale"
  | "offline"
  | "demo";

export type Transaction = {
  type: "paid" | "pending" | "rejected";
  amount: string;
  currency: string;
};

export type FirstFinanceSource = {
  transactions: Transaction[];
  address: { city: string; street: string; houseNumber: number };
};

export type SecondFinanceSource = { amount: string; currency: string }[];

export type CurrencyData = {
  date: string;
  base: string;
  rates: Record<string, string>;
};

export type FinanceResult = [FirstFinanceSource, SecondFinanceSource];
export type FinanceData = {
  financeResult: FinanceResult;
  currencyData: CurrencyData;
};

export type Quote = {
  symbol: string;
  bid: string;
  ask: string;
  changePercent: string;
  timestamp: number;
};

export type Candle = {
  symbol: string;
  timeframe: Timeframe;
  timestamp: number;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
  closed: boolean;
};

export type LiveBalance = {
  currency: string;
  available: string;
  reserved: string;
  convertedUsd: string;
  timestamp: number;
};

export type NewsItem = {
  id: string;
  headline: string;
  summary: string;
  source: string;
  currencies: string[];
  publishedAt: number;
  importance: "low" | "medium" | "high";
};

export type CalendarEvent = {
  id: string;
  title: string;
  currency: string;
  country: string;
  scheduledAt: number;
  importance: "low" | "medium" | "high";
  previous?: string;
  forecast?: string;
  actual?: string;
};
