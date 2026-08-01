import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = ({ url }) => ({
  origin: url.origin,
});
