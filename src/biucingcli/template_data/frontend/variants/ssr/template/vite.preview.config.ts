import { resolve } from "node:path";
import { defineConfig } from "vite";
import { applicationListener, loadApplication } from "./server/runtime.ts";

// Preview real server-rendered responses, not a static SPA fallback.
// Production uses server/index.ts (no Vite process or development dependencies).
export default defineConfig({
  build: { outDir: "build/client" },
  preview: { host: "127.0.0.1" },
  plugins: [
    {
      name: "node-ssr-preview",
      async configurePreviewServer(server) {
        server.middlewares.use(
          applicationListener(resolve("build/client"), await loadApplication()),
        );
      },
    },
  ],
});
