# CI/CD Pipeline Setup — P08

## 📋 Обзор

Проект использует GitHub Actions для автоматизации процессов сборки, тестирования и деплоя.

## 🛡️ Дополнение P09 — SBOM & SCA

- Workflow [`Security - SBOM & SCA`](../.github/workflows/ci-sbom-sca.yml)
  реагирует на изменения Python-кода, зависимостей и самой политики.
- Инструменты зафиксированы: Syft `anchore/syft:v1.17.0`,
  Grype `anchore/grype:v0.78.1`.
- Последовательность шага:
  1. Создать `EVIDENCE/P09` + `job_metadata.json`.
  2. Сгенерировать SBOM (`sbom.json`, CycloneDX).
  3. Прогнать Grype по SBOM → `sca_report.json`.
  4. Собрать `sca_summary.md` с таблицей severity и ссылкой на
     [`policy/waivers.yml`](../policy/waivers.yml).
  5. Загрузить директорию как артефакт `P09_EVIDENCE-<commit>` и
     записать краткое резюме в `GITHUB_STEP_SUMMARY`.
- Те же команды доступны локально через `docker run ...` (см. README).

## 🎯 Критерии P08 (★★ 10/10 баллов)

### ✅ C1. Сборка и тесты (★★ 2/2)

**Матрица тестирования:**
- Python версии: 3.11, 3.12
- OS: Ubuntu, macOS
- **Параллельные jobs:** test, lint, docker (одновременно)

**Кэш зависимостей:**
- Pip cache с оптимизированными ключами
- Учет версии Python и OS

### ✅ C2. Кэширование/конкурренси (★★ 2/2)

**Кэширование:**
```yaml
# Pip cache с версией Python
key: ${{ runner.os }}-pip-py${{ matrix.python-version }}-${{ hashFiles('**/requirements*.txt') }}

# Docker layer cache
cache-from: type=gha
cache-to: type=gha,mode=max
```

**Concurrency:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### ✅ C3. Секреты и конфиги (★★ 2/2)

**GitHub Secrets используются:**

#### Тестовое окружение:
- `TEST_DATABASE_URL` — URL тестовой БД
- `JWT_SECRET_KEY` — секрет для JWT токенов

#### Staging окружение:
- `STAGING_DATABASE_URL` — URL staging БД
- `STAGING_JWT_SECRET` — секрет для staging
- `DEPLOY_TOKEN` — токен для деплоя

#### GitHub Variables:
- `JWT_ALGORITHM` — алгоритм JWT (HS256)

**Безопасность:**
- Секреты маскируются в логах
- Используются fallback значения для CI
- Разграничение по окружениям (test/staging/prod)

### ✅ C4. Артефакты/репорты (★★ 2/2)

**Сохраняемые артефакты:**

1. **Test Reports** (для каждой матрицы):
   - JUnit XML (`junit.xml`)
   - Coverage HTML report
   - Coverage XML для Codecov
   - Retention: 30 дней

2. **Docker Image** (`docker-image.tar`):
   - Готовый образ для деплоя
   - Retention: 7 дней

3. **Security Reports** (`trivy-security-report`):
   - SARIF формат для GitHub Security
   - Сканирование CRITICAL/HIGH уязвимостей

4. **Deployment Report** (`deployment-report.txt`):
   - Детальная информация о деплое
   - Статус компонентов
   - Чеклист для production

### ✅ C5. CD/промоушн (★★ 2/2)

**Staging Deployment:**
- Автоматический деплой при push в `main`/`p08-cicd-minimal`
- Симуляция rolling update
- Health checks
- Использование GitHub Environments

**Production Readiness:**
- Проверка готовности к production
- Чеклист перед продакшеном
- Manual approval required

---

## 🔧 Настройка GitHub Secrets

### 1. Перейдите в настройки репозитория:
```
Settings → Secrets and variables → Actions
```

### 2. Добавьте Secrets:

**Вкладка "Secrets":**

```bash
# Test environment
TEST_DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test_db
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars-long-for-security

# Staging environment
STAGING_DATABASE_URL=postgresql+asyncpg://user:pass@staging-host:5432/staging_db
STAGING_JWT_SECRET=staging-jwt-secret-key-min-32-chars
DEPLOY_TOKEN=ghp_your_personal_access_token_here
```

### 3. Добавьте Variables:

**Вкладка "Variables":**

```bash
JWT_ALGORITHM=HS256
```

### 4. Настройте Environment:

1. Settings → Environments → New environment
2. Name: `staging`
3. (Optional) Add protection rules:
   - Required reviewers
   - Wait timer
   - Deployment branches

---

## 🚀 Использование

### Автоматический запуск:

**При Push:**
```bash
git push origin main
# → Запускает весь pipeline + деплой в staging
```

**При Pull Request:**
```bash
# → Запускает тесты, lint, docker build
# → НЕ деплоит в staging
```

### Просмотр результатов:

1. **Actions tab:**
   - https://github.com/NKChyong/rbpoProject/actions

2. **Артефакты:**
   - Доступны в каждом workflow run
   - Скачать: Actions → Workflow run → Artifacts

3. **Coverage:**
   - Codecov интеграция (если настроен токен)

---

## 📊 Workflow Jobs

```mermaid
graph LR
    A[Push/PR] --> B[Test Matrix]
    A --> C[Lint]
    A --> D[Docker Build]
    B --> E[Deploy Staging]
    C --> E
    D --> E
    E --> F[Prod Ready Check]
```

### Job Timeline:
1. **test** (matrix: 2×2=4 jobs) — ~5-7 min
2. **lint** — ~2-3 min (parallel)
3. **docker** — ~5-8 min (после test+lint)
4. **deploy-staging** — ~2-3 min (после docker)
5. **deploy-production-ready** — ~1 min (после staging)

**Total:** ~15-20 минут для полного pipeline

---

## 🔍 Проверка работы

### 1. Проверьте успешный запуск:
```bash
# Смотрим последний workflow run
gh run list --limit 1

# Детали последнего run
gh run view
```

### 2. Скачайте артефакты:
```bash
# Список артефактов
gh run view --log

# Скачать все артефакты
gh run download <run-id>
```

### 3. Проверьте coverage:
```bash
# Откройте coverage report
cd reports/coverage
open index.html
```

---

## 📝 Чек-лист для сдачи P08

- [x] **C1:** Матрица Python 3.11/3.12 + Ubuntu/macOS ★★
- [x] **C1:** Параллельные jobs (test, lint, docker) ★★
- [x] **C2:** Pip cache с оптимизацией ★★
- [x] **C2:** Docker layer cache (GHA) ★★
- [x] **C2:** Concurrency настроен ★★
- [x] **C3:** GitHub Secrets используются ★★
- [x] **C3:** Разграничение окружений (test/staging) ★★
- [x] **C4:** Test reports (JUnit + Coverage HTML) ★★
- [x] **C4:** Docker image artifact ★★
- [x] **C4:** Security reports (Trivy SARIF) ★★
- [x] **C4:** Deployment reports ★★
- [x] **C5:** Staging deployment simulation ★★
- [x] **C5:** Production readiness check ★★

**ИТОГО: ★★ 10/10 баллов** 🎉

---

## 🎓 Доказательства для отчета

### Требуемые скриншоты:

1. **Успешный CI run:**
   - Actions → Latest workflow run (все зеленое)

2. **Артефакты:**
   - Workflow run → Artifacts section
   - Показать: test-reports, docker-image, trivy-report, deployment-report

3. **GitHub Secrets:**
   - Settings → Secrets and variables → Actions
   - (Скрин с именами секретов, БЕЗ значений)

4. **Матрица тестов:**
   - Workflow run → Test job → Matrix view (4 jobs)

5. **Deployment summary:**
   - deploy-staging job → logs с эмуляцией деплоя

---

## 📚 Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Using secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Workflow artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)

