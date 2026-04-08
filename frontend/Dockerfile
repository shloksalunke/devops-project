FROM oven/bun:1-alpine AS build

WORKDIR /app

COPY package*.json bun.lock* ./
RUN bun install --frozen-lockfile

COPY . .

# Vite uses this at build time to embed the API URL.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN bun run build

FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

