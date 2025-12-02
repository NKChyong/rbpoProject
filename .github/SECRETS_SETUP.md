# GitHub Secrets Configuration для P08

## 📍 Где настроить

```
Repository → Settings → Secrets and variables → Actions
```

## 🔐 Secrets (Repository secrets)

Нажмите **"New repository secret"** для каждого:

### Test Environment

| Name | Example Value | Description |
|------|---------------|-------------|
| `TEST_DATABASE_URL` | `sqlite+aiosqlite:///./test.db` | Test DB connection string |
| `JWT_SECRET_KEY` | `test-jwt-secret-key-min-32-chars-long` | JWT signing key для тестов |

### Staging Environment

| Name | Example Value | Description |
|------|---------------|-------------|
| `STAGING_DATABASE_URL` | `postgresql+asyncpg://user:pass@staging.example.com:5432/app` | Staging DB URL |
| `STAGING_JWT_SECRET` | `staging-jwt-secret-key-change-in-production` | JWT key для staging |
| `DEPLOY_TOKEN` | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx` | GitHub PAT для деплоя |

### Optional (для расширения)

| Name | Example Value | Description |
|------|---------------|-------------|
| `CODECOV_TOKEN` | `abc123...` | Codecov upload token |
| `DOCKER_USERNAME` | `your-dockerhub-user` | DockerHub login |
| `DOCKER_TOKEN` | `dckr_pat_xxx` | DockerHub access token |

## 📊 Variables (Repository variables)

Нажмите **"New repository variable"** для каждого:

| Name | Value | Description |
|------|-------|-------------|
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ENVIRONMENT` | `development` | Default environment |

## 🌍 Environments

### Создание Staging Environment:

1. Settings → Environments → **New environment**
2. Name: `staging`
3. Environment protection rules (optional):
   - ☑️ Required reviewers: `@your-username`
   - ☑️ Wait timer: 5 minutes
   - ☑️ Deployment branches: `main` only

### Environment-specific secrets:

После создания environment, добавьте специфичные секреты:

**Environment: staging**
- Можно переопределить `STAGING_DATABASE_URL` только для staging
- Добавить специфичные для окружения переменные

## ✅ Проверка конфигурации

После настройки секретов, workflow должен:

1. ✅ Использовать секреты в шагах (без отображения значений в логах)
2. ✅ Fallback на дефолтные значения если секрет не задан
3. ✅ Маскировать секреты в выводе команд

### Пример использования в workflow:

```yaml
- name: Configure application
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL || 'sqlite+aiosqlite:///./test.db' }}
    JWT_SECRET: ${{ secrets.JWT_SECRET_KEY || 'test-secret-key-for-ci' }}
  run: |
    echo "Database configured: ${DATABASE_URL%%:*}://..."
    # Значение не отобразится в логах
```

## 📸 Скриншот для отчета

Сделайте скриншот страницы:
```
Settings → Secrets and variables → Actions
```

Должно быть видно:
- ✅ Список имен секретов (TEST_DATABASE_URL, JWT_SECRET_KEY, etc.)
- ✅ Дата последнего обновления
- ❌ НЕ должны быть видны значения секретов

## 🔒 Безопасность

⚠️ **ВАЖНО:**

- Никогда не коммитьте реальные секреты в git
- Используйте сильные, уникальные значения для production
- Регулярно ротируйте секреты (особенно токены)
- Для production используйте secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Минимум прав для токенов (principle of least privilege)

## 🧪 Тестирование

После настройки, запустите workflow:

```bash
git push origin p08-cicd-minimal
```

Проверьте в Actions → Workflow run:
1. Секреты используются (в логах видны маски `***`)
2. Fallback значения работают если секрет не задан
3. Деплой в staging успешно использует переменные окружения

## 📝 Для отчета P08

**Что включить в PR:**

1. ✅ Скриншот Settings → Secrets (без значений)
2. ✅ Этот документ (SECRETS_SETUP.md)
3. ✅ Лог workflow run где используются секреты
4. ✅ Доказательство маскирования (*** в логах)

