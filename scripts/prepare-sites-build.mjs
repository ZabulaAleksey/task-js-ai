import { cp, mkdir, rm, stat } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { build } from "esbuild";

const projectRoot = process.cwd();
const svelteKitOutput = resolve(projectRoot, ".svelte-kit");
const cloudflareOutput = resolve(svelteKitOutput, "cloudflare");
const workerSource = resolve(cloudflareOutput, "_worker.js");
const distRoot = resolve(projectRoot, "dist");
const serverOutput = resolve(distRoot, "server");
const clientOutput = resolve(distRoot, "client");

const workerStats = await stat(workerSource).catch(() => null);
if (!workerStats?.isFile()) {
  throw new Error("Cloudflare worker output is missing: run vite build first");
}

await rm(distRoot, { recursive: true, force: true });
await mkdir(serverOutput, { recursive: true });
await build({
  entryPoints: [workerSource],
  outfile: resolve(serverOutput, "index.js"),
  bundle: true,
  format: "esm",
  platform: "browser",
  target: "es2022",
  conditions: ["workerd", "worker", "browser"],
  external: ["cloudflare:workers"],
  legalComments: "none",
});
await cp(cloudflareOutput, clientOutput, {
  recursive: true,
  filter: (source) => basename(source) !== "_worker.js",
});

console.log("Prepared Sites bundle in dist/server and dist/client");
