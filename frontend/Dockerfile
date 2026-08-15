# Multi-stage build: node → nginx
# ВАЖНО: VITE_USE_MOCK — это build-time переменная Vite (import.meta.env).
# Она вкомпиливается в бандл при `vite build`, поэтому передаётся как ARG,
# а НЕ как runtime ENV. Чтобы переключить режим, пересоберите образ:
#   docker build --build-arg VITE_USE_MOCK=false -t incident-frontend .

# --- Stage 1: Build ---
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .

ARG VITE_API_URL=http://localhost:8000
ARG VITE_USE_MOCK=true
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_USE_MOCK=$VITE_USE_MOCK

RUN npm run build

# --- Stage 2: Serve ---
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
