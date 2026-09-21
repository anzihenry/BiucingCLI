ARG BUILDER_IMAGE=node:24.19.0-bookworm-slim
ARG RUNTIME_IMAGE=node:24.19.0-bookworm-slim

FROM ${BUILDER_IMAGE} AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN npm install --global pnpm@11.21.0 && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM ${BUILDER_IMAGE} AS dependencies
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN npm install --global pnpm@11.21.0 && pnpm install --prod --frozen-lockfile

FROM ${RUNTIME_IMAGE}
WORKDIR /app
ENV NODE_ENV=production HOST=0.0.0.0 PORT=3000
COPY --from=dependencies /app/node_modules ./node_modules
COPY package.json ./
COPY --from=builder /app/build ./build
COPY server ./server
USER node
EXPOSE 3000
HEALTHCHECK --interval=1s --timeout=2s --start-period=2s --retries=30 \
  CMD node -e 'fetch("http://127.0.0.1:"+process.env.PORT+"/healthz").then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))'
CMD ["node", "server/index.ts"]
