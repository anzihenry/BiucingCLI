import { defineConfig } from "vite";
import { contentPaths } from "./app/content";

// Local artifact preview only. Production 404/header checks run against Nginx.
export default defineConfig({
  appType: "mpa",
  build: { outDir: "build/client" },
  preview: { host: "127.0.0.1" },
  plugins: [
    {
      name: "ssg-preview-paths",
      configurePreviewServer(server) {
        const paths = new Set(contentPaths());
        server.middlewares.use((request, _response, next) => {
          const url = new URL(request.url ?? "/", "http://preview.invalid");
          const path =
            url.pathname === "/" ? "/" : url.pathname.replace(/\/$/, "");
          if (paths.has(path)) {
            request.url =
              (path === "/" ? "/index.html" : `${path}/index.html`) +
              url.search;
          }
          next();
        });
      },
    },
  ],
});
