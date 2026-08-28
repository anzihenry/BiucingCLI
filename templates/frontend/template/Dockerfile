ARG BUILDER_IMAGE=node:20-alpine
ARG RUNTIME_IMAGE=nginx:1.27-alpine

FROM ${BUILDER_IMAGE} AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@9.9.0 --activate \
    && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM ${RUNTIME_IMAGE}

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=1s --timeout=2s --start-period=2s --retries=30 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
