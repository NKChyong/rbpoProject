# Reading List API

> 🎓 **Проект курса "Разработка Безопасного ПО"** (HSE SecDev 2025)

REST API для управления списком материалов к прочтению (книги, статьи, видео, подкасты). Реализовано с использованием FastAPI, PostgreSQL и лучших практик безопасности.

[![CI/CD Pipeline](https://github.com/NKChyong/rbpoProject/actions/workflows/ci.yml/badge.svg)](https://github.com/NKChyong/rbpoProject/actions/workflows/ci.yml)
[![Security - SBOM & SCA](https://github.com/NKChyong/rbpoProject/actions/workflows/ci-sbom-sca.yml/badge.svg)](https://github.com/NKChyong/rbpoProject/actions/workflows/ci-sbom-sca.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org)
[![codecov](https://codecov.io/gh/NKChyong/rbpoProject/branch/main/graph/badge.svg)](https://codecov.io/gh/NKChyong/rbpoProject)

---

## ✅ CI/CD

- Workflow `ci.yml` запускается на `push` и `pull_request`, использует кэш pip, ограничивает права (`contents: read`) и concurrency по `workflow+ref`.
- Job `lint` проверяет `ruff`, `black`, `isort`. Job `tests` крутится на матрице (`ubuntu`/`macOS` × Python 3.11/3.12), собирает `pytest` + покрытие, выгружает `junit-*`, `coverage-*.xml` и `coverage-html`.
- После зелёных тестов ветки `main` job `deploy-staging` разворачивает HTML-отчёт покрытия на GitHub Pages (environment `staging`) и оставляет ссылку в summary. Это эмуляция CD/промоушна.
- Все отчёты дополнительно доступны в артефактах Actions (`reports/`, `coverage-html/`) и пригодны для ревью.

### Secrets и vars для CI

| Имя                   | Тип        | Где задать                                      | Назначение                              |
|-----------------------|------------|-------------------------------------------------|-----------------------------------------|
| `JWT_SECRET`          | Repository Secret | Settings → Secrets and variables → Actions | Токен для тестов/линтеров (маскируется) |
| `DATABASE_URL`        | Repository Secret | Settings → Secrets and variables → Actions | Подключение к БД на staging/dry-run     |
| `STAGING_API_URL`     | Repository Variable | Settings → Secrets and variables → Actions | Адрес API, прокидывается в тесты        |
| `STAGING_DOMAIN`      | Repository Variable | Settings → Secrets and variables → Actions | Публичная ссылка стейджа/отчётов        |

> Secrets/vars не логируются, используются через `${{ secrets.* }}`/`${{ vars.* }}`. Для приватных форков доступен только `JWT_SECRET`, остальные можно задать в `org` scope.

---

## 🚀 Запуск проекта через Docker

### Требования

- Docker и Docker Compose

### Запуск

```bash
docker-compose up --build
```

Эта команда автоматически:
- ✅ Запустит PostgreSQL
- ✅ Применит миграции БД
- ✅ Запустит бэкенд (FastAPI)
- ✅ Соберёт и запустит фронтенд (React)

**Через 2-3 минуты приложение будет доступно:**
- 🌐 **Фронтенд**: http://localhost:3000
- 🔌 **API**: http://localhost:8000
- 📖 **Swagger UI**: http://localhost:8000/api/docs

### Остановка проекта

```bash
docker-compose down
```

### Удаление всех данных

```bash
docker-compose down -v
```

---

## 🧪 Запуск тестов через Docker

### 1. Запустить контейнеры в фоновом режиме

```bash
docker-compose up -d
```

### 2. Запустить тесты

```bash
docker-compose exec backend pytest -v
```

### 3. Запустить тесты с покрытием кода

```bash
docker-compose exec backend pytest --cov=app --cov-report=term
```

**Ожидаемый результат:**
- ✅ Все 32 теста проходят
- ✅ Покрытие кода > 80%

---

## 📋 Дополнительные команды

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Загрузка тестовых данных

```bash
docker-compose exec backend python scripts/seed_data.py
```

Тестовые пользователи:
- User: `alice` / `Alic3Strong!45`
- User: `bob` / `B0bStrong!45`
- Admin: `admin` / `AdminSecur3!45`

### Создание admin пользователя

```bash
docker-compose exec backend python scripts/create_admin.py admin@example.com admin securepass
```

---

## 📖 Возможности

- **Аутентификация**: JWT-токены (access + refresh), регистрация, логин
- **Роли**: user (по умолчанию), admin
- **CRUD**: Полное управление записями (title, kind, link, status, description)
- **Фильтрация**: По статусу (to_read, in_progress, completed, archived)
- **Пагинация**: limit/offset для списков
- **Безопасность**: Owner-only доступ, защита от IDOR, валидация входных данных
- **Типизация**: book, article, video, podcast, other
- **Асинхронность**: Высокая производительность через async/await
- **React Frontend**: Веб-интерфейс для работы с API

---

## 🔒 Безопасность

- **JWT токены**: Stateless аутентификация с access и refresh токенами
- **Bcrypt**: Безопасное хеширование паролей (cost factor 12)
- **RBAC**: Контроль доступа на основе ролей (user/admin)
- **Парольная политика**: минимум 12 символов, верхний/нижний регистр, цифры и символ
- **Owner-only**: Пользователи могут работать только со своими записями
- **Валидация**: Pydantic валидация всех входных данных
- **CORS**: Настроенные разрешенные домены
- **Request ID**: Трейсинг всех запросов для аудита
- **No IDOR**: Защита от Insecure Direct Object References

Если нашли уязвимость, см. [SECURITY.md](SECURITY.md) для контакта.

---

## 📝 Технологии

- **Python 3.11+** - язык программирования
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy 2.0** - асинхронная ORM
- **PostgreSQL 16** - реляционная база данных
- **Asyncpg** - асинхронный драйвер PostgreSQL
- **Alembic** - управление миграциями БД
- **Pydantic** - валидация данных
- **JWT** - токен-аутентификация
- **Bcrypt** - хеширование паролей
- **Pytest** - фреймворк тестирования (32 теста, покрытие 80%+)
- **Docker & Docker Compose** - контейнеризация
- **React** - фронтенд фреймворк
- **GitHub Actions** - CI/CD

---

## 🔄 CI/CD Pipeline (P08 ★★ 10/10)

Проект оснащен полноценным CI/CD pipeline на GitHub Actions:

### ⚡ Возможности:

- **✅ C1: Матричное тестирование** — Python 3.11/3.12 × Ubuntu/macOS (4 параллельных jobs)
- **✅ C2: Кэширование** — pip dependencies + Docker layers (GHA cache)
- **✅ C2: Concurrency** — автоматическая отмена устаревших запусков
- **✅ C3: Secrets Management** — безопасное управление секретами для test/staging/prod
- **✅ C4: Артефакты** — test reports, coverage HTML, Docker images, security scans
- **✅ C5: CD/Staging** — автоматический деплой в staging при push в main

### 📊 Pipeline Jobs:

1. **Test Matrix** (4 jobs) — линтеры + тесты с coverage для всех версий
2. **Security Checks** — поиск секретов, security scanning
3. **Docker Build** — сборка образа с Trivy scan
4. **Deploy Staging** — симуляция деплоя в staging окружение
5. **Production Ready** — проверка готовности к production

### 🚀 Запуск:

```bash
git push origin main  # → Запускает полный pipeline с деплоем
```

**Подробности:** См. [docs/CI_CD_SETUP.md](docs/CI_CD_SETUP.md)

---

## 🛡️ SBOM & SCA (P09)

- Workflow [`Security - SBOM & SCA`](.github/workflows/ci-sbom-sca.yml) запускается на `push`/`pull_request`
  и вручную через `workflow_dispatch`. Он фиксирует версию инструментов
  (Syft `anchore/syft:v1.17.0`, Grype `anchore/grype:v0.78.1`) для
  воспроизводимости.
- Результаты попадают в `EVIDENCE/P09/`:
  `sbom.json`, `sca_report.json`, `sca_summary.md`, `job_metadata.json`.
  Директория автоматически архивируется как артефакт
  `P09_EVIDENCE-<commit>` и приложена к job summary.
- Политика triage и waivers описана в
  [`project/69_sbom-vuln-mgmt.md`](project/69_sbom-vuln-mgmt.md) +
  файл [`policy/waivers.yml`](policy/waivers.yml). Первый waiver закрывает
  известную ReDoS-уязвимость `nth-check@1.0.2` (CVE-2021-3803), которая
  появляется в цепочке CRA → svgo и не попадает в production-бандл.
- Локально ту же процедуру можно повторить (при наличии Docker):

  ```bash
  mkdir -p EVIDENCE/P09
  docker run --rm -v $PWD:/work -w /work anchore/syft:v1.17.0 \
    packages dir:. -o cyclonedx-json > EVIDENCE/P09/sbom.json
  docker run --rm -v $PWD:/work -w /work anchore/grype:v0.78.1 \
    sbom:/work/EVIDENCE/P09/sbom.json -o json > EVIDENCE/P09/sca_report.json
  ```

---

## 👥 Автор

Проект разработан для курса "Разработка Безопасного ПО" (HSE SecDev 2025)
**Нгуен Куиет Чыонг** - Студент БПИ238 ФКН ПИ

По вопросам безопасности см. [SECURITY.md](SECURITY.md)

---
