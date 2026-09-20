import { defineConfig } from "vite";
import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";
export default defineConfig({
  plugins: [tailwindcss(), reactRouter()],
  resolve: { alias: { "@": fileURLToPath(new URL("./app", import.meta.url)) } },
  build: { outDir: "build/client" },
  // React Router uses preview during SPA prerender; avoid localhost IPv4/IPv6 mismatch.
  preview: { host: "127.0.0.1" },
});
