ARG BUILDER_IMAGE=node:24.19.0-bookworm-slim
ARG RUNTIME_IMAGE=nginx:1.27-alpine

FROM ${BUILDER_IMAGE} AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN npm install --global pnpm@11.21.0 \
    && pnpm install --frozen-lockfile

COPY . .
ARG SITE_URL
RUN SITE_URL="$SITE_URL" pnpm build

FROM ${RUNTIME_IMAGE}

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/build/client /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=1s --timeout=2s --start-period=2s --retries=30 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
