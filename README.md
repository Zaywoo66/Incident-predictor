# Incident Predictor

Предиктивная модель инцидентов: на основе метрик инфраструктуры (CPU, RAM, latency, disk I/O, network I/O, частота деплоев) предсказывает вероятность сбоя сервиса в ближайшие N минут и объясняет вклад каждого признака через SHAP. Стек: Prometheus + Grafana → pandas → XGBoost + SHAP → FastAPI → React.

## Предусловие: обучение модели

Перед первым запуском необходимо обучить модель, чтобы появились файлы `ml-pipeline/models/model.pkl` и `ml-pipeline/models/feature_pipeline.pkl`:

```bash
cd ml-pipeline
python train.py
```

Также создайте `.env` для фронтенда:

```bash
cp frontend/.env.example frontend/.env
# Убедитесь, что VITE_USE_MOCK=false и VITE_API_URL=http://localhost:8000
```

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

## Адреса сервисов

| Сервис         | URL                          |
|----------------|------------------------------|
| Frontend       | http://localhost              |
| API            | http://localhost:8000         |
| API Health     | http://localhost:8000/health  |
| Prometheus     | http://localhost:9090         |
| Grafana        | http://localhost:3000         |
| node-exporter  | http://localhost:9100/metrics |
| cAdvisor       | http://localhost:8080         |

**Grafana:** логин `admin` / пароль `admin` (по умолчанию).

## Структура проекта

```
incident-predictor/
├── infra/                # Prometheus, Grafana, node-exporter, cAdvisor
├── data-generation/      # Генерация синтетических метрик + коллектор
├── ml-pipeline/          # Feature engineering, обучение XGBoost, SHAP
├── api/                  # FastAPI-сервис предсказания (/predict, /health)
├── frontend/             # React-дашборд (Vite + nginx)
├── deploy/               # Заметки по деплою
├── docker-compose.yml    # Единый compose для всего стека
├── .env.example          # Шаблон переменных окружения
└── ARCHITECTURE.md       # Архитектура и контракты между модулями
```
