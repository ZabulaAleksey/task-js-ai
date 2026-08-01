import { json } from "@sveltejs/kit";
import { createDemoFinanceData } from "$lib/demo/finance";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = () =>
  json(createDemoFinanceData(), {
    headers: {
      "cache-control": "private, max-age=15",
    },
  });
