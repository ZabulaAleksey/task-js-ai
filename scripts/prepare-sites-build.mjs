import { cp, mkdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

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
const worker = (await readFile(workerSource, "utf8"))
  .replace(
    'from "./../output/server/index.js"',
    'from "./output/server/index.js"',
  )
  .replace(
    'from "./../cloudflare-tmp/manifest.js"',
    'from "./cloudflare-tmp/manifest.js"',
  );
await writeFile(resolve(serverOutput, "index.js"), worker);
await cp(
  resolve(svelteKitOutput, "output", "server"),
  resolve(serverOutput, "output", "server"),
  { recursive: true },
);
await cp(
  resolve(svelteKitOutput, "cloudflare-tmp"),
  resolve(serverOutput, "cloudflare-tmp"),
  { recursive: true },
);
await cp(cloudflareOutput, clientOutput, {
  recursive: true,
  filter: (source) => basename(source) !== "_worker.js",
});

console.log("Prepared Sites bundle in dist/server and dist/client");
