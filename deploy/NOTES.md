# deploy/NOTES.md

## Стратегия композиции

Корневой `docker-compose.yml` **полностью заменяет** `infra/docker-compose.yml`.

Все 4 infra-сервиса (prometheus, node-exporter, cadvisor, grafana) продублированы
в корневом файле, но ссылаются на конфиги из `infra/` через относительные пути
(`./infra/prometheus.yml`, `./infra/grafana/provisioning`). Дублирования конфигов нет.

**Не нужно** запускать `docker compose -f infra/docker-compose.yml -f docker-compose.yml up`.
Достаточно одной команды из корня:

```bash
docker compose up --build
```

`infra/docker-compose.yml` остаётся в репозитории для возможности изолированного
запуска мониторинга без api/frontend (например, для отладки метрик).

---

## TODO перед первым запуском

- **Обучить модель.** Файлы `ml-pipeline/models/model.pkl` и
  `ml-pipeline/models/feature_pipeline.pkl` должны существовать до запуска
  контейнера `api`. Обучить через:

  ```bash
  cd ml-pipeline
  python train.py
  ```

  Это создаст оба `.pkl`-файла в `ml-pipeline/models/`.

- **Создать `frontend/.env`.** Скопировать `frontend/.env.example` →
  `frontend/.env` и установить `VITE_USE_MOCK=false`,
  `VITE_API_URL=http://localhost:8000`. Vite читает `.env` при `npm run build`
  внутри Docker-сборки (`COPY . .` копирует `.env` в контейнер).

---

## Порты сервисов

| Сервис         | Порт  |
|----------------|-------|
| Prometheus     | 9090  |
| Grafana        | 3000  |
| node-exporter  | 9100  |
| cAdvisor       | 8080  |
| API            | 8000  |
| Frontend       | 80    |
