import type { ParamMatcher } from "@sveltejs/kit";

export const match: ParamMatcher = (value) => /^[A-Z]{6}$/.test(value);
