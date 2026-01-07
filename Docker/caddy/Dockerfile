# syntax=docker/dockerfile:1
FROM caddy:builder-alpine AS builder
ENV CGO_ENABLED=0
ENV GOARCH=amd64
ENV GOOS=linux
ENV GOMAXPROCS=1
RUN xcaddy build \
    --with github.com/mholt/caddy-l4 \
    --with github.com/mholt/caddy-ratelimit \
    --with github.com/caddy-dns/cloudflare \
    --output ./caddy

FROM caddy:alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
RUN chmod +x /usr/bin/caddy
RUN apk add --no-cache bash \
    coreutils ca-certificates \
    nss nss-tools
RUN update-ca-certificates
ENTRYPOINT [ "caddy", "run", "--config", "/etc/caddy/config.json" ]
