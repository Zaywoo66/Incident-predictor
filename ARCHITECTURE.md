# ARCHITECTURE.md — Predictive Incident Model

> Этот файл — единственный источник правды по архитектуре проекта.
> Агент получает на вход: секции 0–3 (всегда) + секцию текущего этапа.
> Не давай агенту весь файл сразу для каждой задачи — давай только нужный этап, чтобы не сжигать токены.

---

## 0. Цель проекта

Предиктивная модель инцидентов: на основе метрик инфраструктуры (CPU, RAM, latency, disk I/O, network I/O, частота деплоев) предсказывает вероятность сбоя сервиса в ближайшие N минут и объясняет вклад каждого признака (SHAP).

Стек: Prometheus + Grafana + node_exporter/cAdvisor → pandas + tsfresh → XGBoost + SHAP → FastAPI → React. Деплой через Docker Compose.

---

## 1. Правила для агента (ОБЯЗАТЕЛЬНО)

1. **Работай только в пределах директории текущего этапа.** Не редактируй файлы в других директориях. Если нужно что-то изменить в общем контракте (раздел 2) — останови работу и зафиксируй это явно в commit message и в `NOTES.md` внутри своей директории, не меняй раздел 2 самостоятельно.
2. **Без воды.** Не пиши пояснений в чат сверх необходимого. Результат работы — код, тесты (если предусмотрены), README модуля (3–5 строк: что это и как запустить) и коммиты. Комментарии в коде — только там, где логика не очевидна из названий переменных/функций.
3. **Коммитить обязательно и часто**, не одним гигантским коммитом в конце:
   - Коммит после каждого логически завершённого куска (например: настроил docker-compose для Prometheus → коммит; добавил node_exporter → коммит; подключил Grafana dashboard → коммит).
   - Формат сообщений — Conventional Commits: `type(scope): описание`
     - `feat(infra): add prometheus and node_exporter compose config`
     - `fix(ml-pipeline): correct rolling window leak in feature engineering`
     - `test(api): add unit tests for /predict endpoint`
     - `docs(frontend): add setup instructions`
     - `chore(deploy): pin dependency versions`
   - Финальный коммит этапа всегда вида: `feat(<scope>): complete <stage name>` — он сигнализирует, что этап готов к ревью.
4. **Перед финальным коммитом этапа** — прогнать линтер/тесты, если они есть в этапе. Если что-то не проходит — фиксить в рамках этого же этапа, не переносить долг на следующий.
5. **Если контракт (раздел 2) невозможно выполнить буквально** — не придумывай свою версию тихо. Зафиксируй отклонение явно в `NOTES.md` своей директории и в commit message (`fix(scope): deviate from contract — <причина>`).
6. **Не трогай инструменты/библиотеки, не указанные в этапе**, даже если кажется, что есть более удобная альтернатива — это ломает совместимость между этапами, которые пишутся в разных сессиях/аккаунтами.

---

## 2. Контракты между модулями (НЕ менять без обновления этого файла)

### infra/
- Prometheus доступен на `:9090`
- Grafana на `:3000`
- node_exporter на `:9100`
- cAdvisor на `:8080`
- Все сервисы поднимаются одной командой `docker compose up` из `infra/`
- **Docker-сеть:** все сервисы (включая будущие из api/ и deploy/) подключаются к внешней сети `incident-net` (`external: true` в compose-файлах модулей, саму сеть создаёт `infra/docker-compose.yml`). Это обязательно — без общей сети `data-generation/collector.py` и `api/` не достучатся до Prometheus по имени контейнера.
- **Версии образов — строго пины, не `:latest`:**
  - `prom/prometheus:v2.53.0`
  - `grafana/grafana:11.1.0`
  - `prom/node-exporter:v1.8.1`
  - `gcr.io/cadvisor/cadvisor:v0.49.1`
- **Persistence:** named volumes для Prometheus (`prometheus_data:/prometheus`) и Grafana (`grafana_data:/var/lib/grafana`), чтобы метрики и дашборды не терялись при `docker compose down` (без `-v`).
- **Grafana dashboard — только как код**, не кликами в UI: JSON-модель дашборда лежит в `infra/grafana/provisioning/dashboards/*.json`, источник данных — в `infra/grafana/provisioning/datasources/*.yml`. Всё должно подняться автоматически при старте контейнера, без ручной настройки через интерфейс.

### data-generation/
- Итоговый датасет: `data/raw/metrics_labeled.csv`
- Колонки: `timestamp, cpu, ram, latency, disk_io, network_io, deploy_flag, incident_label`
- `incident_label` — 0/1, размечается по факту синтетической нагрузки (Locust/stress-ng сценарии)
- Частота записи: 1 строка раз в 15 секунд

### ml-pipeline/
- Вход: `data/raw/metrics_labeled.csv`
- Выход:
  - `models/model.pkl` (обученный XGBoost через joblib)
  - `models/feature_pipeline.pkl` (сериализованная логика tsfresh-признаков — должна использоваться и в api/, одинаково)
  - `metrics/report.json` — `{precision, recall, f1, roc_auc}`

### api/
- Загружает `models/model.pkl` и `models/feature_pipeline.pkl`
- `POST /predict`
  - вход: `{"cpu": float, "ram": float, "latency": float, "disk_io": float, "network_io": float, "deploy_flag": int, "window_minutes": int}` (массив последних точек, не одна точка — модели нужна история)
  - выход: `{"probability": float, "shap_values": {"<feature>": float, ...}}`
- `GET /health` → `{"status": "ok"}`

### frontend/
- Обращается к API через переменную окружения `API_URL` (не хардкодить адрес)
- Эндпоинты использует только те, что описаны в api/ выше

### deploy/
- `docker-compose.yml` в корне репозитория объединяет все сервисы (infra, api, frontend)
- Каждый модуль — свой `Dockerfile` внутри своей директории, `deploy/` только собирает их вместе

---

## 3. Структура репозитория

```
project/
├── infra/
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── grafana/
├── data-generation/
│   ├── locust_scenarios.py
│   ├── stress_scenarios.sh
│   └── collector.py
├── ml-pipeline/
│   ├── features.py
│   ├── train.py
│   └── evaluate.py
├── api/
│   ├── main.py
│   ├── Dockerfile
│   └── tests/
├── frontend/
│   ├── src/
│   └── Dockerfile
├── deploy/
│   └── docker-compose.yml
└── ARCHITECTURE.md
```

---

## 4. Этап: infra/

**Цель:** рабочий стек мониторинга, метрики уже текут и видны в Grafana, всё воспроизводимо через код (без ручных кликов).

**Сделать:**
- `docker-compose.yml`: prometheus, node_exporter, cAdvisor, grafana — версии образов строго по пинам из раздела 2
- Создать сеть `incident-net` в этом compose-файле (она же `external: true` будет использоваться другими модулями)
- Volumes `prometheus_data` и `grafana_data` для персистентности
- `prometheus.yml`: scrape config для всех трёх источников
- `grafana/provisioning/datasources/prometheus.yml` — автоподключение Prometheus как источника данных
- `grafana/provisioning/dashboards/*.json` — JSON-модель дашборда с панелями CPU/RAM/latency/network (экспортировать из Grafana UI после ручной настройки одного раза, но в репозиторий кладётся именно JSON, не инструкция "настроить руками")

**Acceptance criteria:**
- `docker compose up` поднимает все 4 сервиса без ошибок, используя указанные версии образов
- В Prometheus (`:9090/targets`) все targets `UP`
- В Grafana виден dashboard с живыми данными сразу после первого старта контейнера, без участия пользователя
- `docker compose down` (без `-v`) и повторный `up` — данные и дашборд на месте (проверяет persistence)
- Сеть `incident-net` создана и видна в `docker network ls`

**Коммиты:** по каждому сервису отдельно (см. примеры в разделе 1), финальный — `feat(infra): complete monitoring stack setup`

---

## 5. Этап: data-generation/

**Цель:** размеченный датасет для обучения.

**Сделать:**
- `locust_scenarios.py` — сценарии нагрузки на тестовый эндпоинт
- `stress_scenarios.sh` — стресс по CPU/RAM/disk через stress-ng, с разной интенсивностью и длительностью
- `collector.py` — тянет метрики из Prometheus API за период экспериментов, маппит на `incident_label` по времени запуска/окончания стресс-сценариев, пишет в `data/raw/metrics_labeled.csv`

**Acceptance criteria:**
- CSV соответствует схеме контракта (раздел 2)
- В датасете есть оба класса (0 и 1), не вырожденный набор
- Скрипты запускаются без хардкода путей/портов (брать из `.env` или аргументов)

**Коммиты:** отдельно locust, отдельно stress-ng, отдельно collector. Финальный — `feat(data-generation): complete labeled dataset pipeline`

---

## 6. Этап: ml-pipeline/

**Цель:** обученная модель + метрики качества.

**Сделать:**
- `features.py` — tsfresh-признаки (rolling mean/std, lag, rate of change), вынести в отдельную переиспользуемую функцию/класс (её же потом импортирует api/)
- `train.py` — train/test split, обучение XGBoost, сохранение через joblib
- `evaluate.py` — расчёт precision/recall/f1/roc_auc → `metrics/report.json`, плюс SHAP summary

**Acceptance criteria:**
- `metrics/report.json` существует и содержит все 4 метрики
- `models/model.pkl` и `models/feature_pipeline.pkl` загружаются без ошибок отдельным скриптом-проверкой
- recall не принесён в жертву accuracy (датасет несбалансирован — это явно проверяется в тестах)

**Коммиты:** отдельно features, отдельно train, отдельно evaluate. Финальный — `feat(ml-pipeline): complete training pipeline with metrics report`

---

## 7. Этап: api/

**Цель:** модель доступна как HTTP API.

**Сделать:**
- `main.py` — FastAPI, эндпоинты `/predict` и `/health` (контракт — раздел 2)
- Использовать **тот же** `features.py`/`feature_pipeline.pkl` из ml-pipeline — не переписывать логику признаков заново
- `tests/` — минимум: тест на `/health`, тест на `/predict` с валидным и невалидным телом запроса
- `Dockerfile`

**Acceptance criteria:**
- Все тесты зелёные
- `/predict` возвращает JSON строго по контракту
- Контейнер собирается и запускается изолированно (`docker build && docker run`)

**Коммиты:** отдельно эндпоинты, отдельно тесты, отдельно Dockerfile. Финальный — `feat(api): complete prediction service`

---

## 8. Этап: frontend/

**Цель:** дашборд риска инцидентов.

**Сделать:**
- Страница с: текущей вероятностью риска (gauge/число), графиком метрик во времени, бар-чартом SHAP-вклада признаков
- `API_URL` через переменные окружения
- `Dockerfile`

**Acceptance criteria:**
- Собирается и запускается без ошибок
- Корректно обрабатывает состояние "API недоступен" (не белый экран)

**Коммиты:** по компонентам (gauge, график метрик, SHAP-бар-чарт). Финальный — `feat(frontend): complete risk dashboard`

---

## 9. Этап: deploy/

**Цель:** весь проект поднимается одной командой.

**Сделать:**
- Корневой `docker-compose.yml`, объединяющий infra + api + frontend
- `.env.example` со всеми переменными
- Краткий `README.md` в корне: как поднять весь проект с нуля

**Acceptance criteria:**
- `docker compose up` из корня поднимает всё, дашборд показывает реальный прогноз модели на живых метриках

**Коммиты:** отдельно compose-файл, отдельно .env.example, финальный — `feat(deploy): complete full-stack docker setup`

---

## 10. Как использовать этот файл по этапам

Для каждой сессии агента (в т.ч. на разных аккаунтах) давай:
1. Разделы 1, 2, 3 (правила, контракты, структура) — всегда
2. Раздел только текущего этапа (4–9) — не остальные

Это держит контекст минимальным и не даёт агенту "случайно" полезть переписывать чужой этап.
