import { defineConfig } from "vite";

export default defineConfig({
  appType: "spa",
  build: { outDir: "build/client" },
  preview: { host: "127.0.0.1" },
});
