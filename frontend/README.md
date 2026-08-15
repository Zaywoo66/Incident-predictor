# frontend/ — Incident Predictor Dashboard

React + Vite дашборд для отображения вероятности инцидента, метрик инфраструктуры и SHAP-вклада признаков.

## Разработка

```bash
cp .env.example .env
npm install
npm run dev
```

Откроется на `http://localhost:5173`. По умолчанию работает в mock-режиме (`VITE_USE_MOCK=true`).

## Переключение на реальный API

1. В `.env` установите:
   ```
   VITE_USE_MOCK=false
   VITE_API_URL=http://localhost:8000
   ```
2. Перезапустите `npm run dev`.

Для Docker-сборки передайте build-arg:
```bash
docker build --build-arg VITE_USE_MOCK=false -t incident-frontend .
docker run -p 80:80 incident-frontend
```
