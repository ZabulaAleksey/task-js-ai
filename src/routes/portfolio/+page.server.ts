import { createDemoFinanceData } from "$lib/demo/finance";
import type { Actions, PageServerLoad } from "./$types";

export const load: PageServerLoad = () => ({
  financeData: createDemoFinanceData(),
  mode: "demo" as const,
});

export const actions = {
  refresh: () => ({
    financeData: createDemoFinanceData(),
    refreshedAt: Date.now(),
  }),
} satisfies Actions;
