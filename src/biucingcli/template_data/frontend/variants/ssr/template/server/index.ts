import { resolve } from "node:path";
import {
  applicationListener,
  createAppServer,
  loadApplication,
  portFromEnvironment,
} from "./runtime.ts";

const port = portFromEnvironment(process.env.PORT);
const host = process.env.HOST ?? "0.0.0.0";
if (!["0.0.0.0", "127.0.0.1", "::", "::1"].includes(host)) {
  throw new Error("HOST must be an explicit bind address");
}
const { server, shutdown } = createAppServer(
  applicationListener(resolve("build/client"), await loadApplication()),
);
server.on("error", () => {
  console.error("SSR server failed to listen");
  process.exitCode = 1;
});
server.listen(port, host, () => {
  console.info(`SSR listening on ${host}:${port}`);
});
for (const signal of ["SIGINT", "SIGTERM"] as const) {
  process.on(signal, () => {
    void shutdown().then((drained) => {
      process.exitCode = drained ? 0 : 1;
    });
  });
}
