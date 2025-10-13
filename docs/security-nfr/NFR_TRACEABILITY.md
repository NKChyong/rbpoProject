# NFR Traceability Matrix - Матрица трассируемости

> **Проект:** Reading List API
> **Версия:** 1.0
> **Дата:** Октябрь 2025

## Введение

Данный документ устанавливает связи между нефункциональными требованиями (NFR), пользовательскими историями (User Stories), задачами разработки (Tasks), тестами и релизами. Это обеспечивает прозрачность реализации и возможность отслеживания прогресса.

---

## 1. Матрица NFR ↔ User Stories

| NFR ID | NFR Название                      | Связанные Stories                                | Приоритет | Status      |
|--------|-----------------------------------|--------------------------------------------------|-----------|-------------|
| NFR-01 | Хранение паролей                  | AUTH-001: Регистрация пользователя               | High      | ✅ Done     |
|        |                                   | AUTH-002: Аутентификация пользователя            | High      | ✅ Done     |
| NFR-02 | JWT токены                        | AUTH-002: Аутентификация пользователя            | High      | ✅ Done     |
|        |                                   | AUTH-003: Refresh токен механизм                 | High      | ✅ Done     |
|        |                                   | AUTH-004: Logout и отзыв токенов                 | Medium    | ✅ Done     |
| NFR-03 | Производительность аутентификации | PERF-001: Нагрузочное тестирование login         | High      | 🔄 Planned  |
|        |                                   | PERF-002: Оптимизация DB запросов                | Medium    | 🔄 Planned  |
| NFR-04 | Структурированные ошибки          | API-001: Единообразная обработка ошибок          | Medium    | ✅ Done     |
|        |                                   | API-002: Request ID для трейсинга                | Medium    | ✅ Done     |
| NFR-05 | Уязвимости зависимостей           | SEC-001: Настройка Semgrep в CI                  | High      | ✅ Done     |
|        |                                   | SEC-002: Процесс управления уязвимостями         | High      | 🔄 Planned  |
| NFR-06 | HTTPS Only                        | INFRA-001: Настройка TLS в production            | High      | 🔄 Planned  |
|        |                                   | INFRA-002: HTTPS redirect и HSTS                 | High      | 🔄 Planned  |
| NFR-07 | Rate Limiting                     | SEC-003: Реализация rate limiting middleware     | Medium    | 🔄 Planned  |
|        |                                   | SEC-004: Rate limit мониторинг                   | Low       | 🔄 Planned  |
| NFR-08 | Логирование безопасности          | LOG-001: Структурированное логирование           | Medium    | ✅ Done     |
|        |                                   | LOG-002: Security events logging                 | Medium    | ✅ Done     |
| NFR-09 | SQL Injection защита              | SEC-005: Код-ревью на SQL injection              | High      | ✅ Done     |
|        |                                   | SEC-006: SAST проверки в CI                      | High      | ✅ Done     |
| NFR-10 | Session Management                | AUTH-005: Multi-device session management        | Low       | 📝 Backlog  |
| NFR-11 | Backup и восстановление           | INFRA-003: Автоматические бэкапы БД              | Medium    | 🔄 Planned  |
|        |                                   | INFRA-004: Disaster recovery процедура           | Medium    | 📝 Backlog  |
| NFR-12 | Мониторинг доступности            | OBS-001: Healthcheck endpoint                    | Medium    | ✅ Done     |
|        |                                   | OBS-002: Uptime monitoring                       | Medium    | 🔄 Planned  |

### Легенда статусов
- ✅ **Done**: Реализовано и протестировано
- 🔄 **Planned**: Запланировано к реализации
- 📝 **Backlog**: В бэклоге, приоритет низкий
- ❌ **Blocked**: Заблокировано зависимостями

---

## 2. Детальная трассировка: NFR → Stories → Tasks

### NFR-01: Хранение паролей

**User Stories:**
- **AUTH-001**: Как новый пользователь, я хочу зарегистрироваться в системе
- **AUTH-002**: Как пользователь, я хочу войти в систему с помощью email и пароля

**Tasks:**
- `TASK-001`: Настроить bcrypt с cost factor 12
- `TASK-002`: Реализовать хеширование при регистрации
- `TASK-003`: Реализовать верификацию пароля при логине
- `TASK-004`: Написать unit-тесты для password hashing
- `TASK-005`: Код-ревью на отсутствие plain-text паролей в логах

**Тесты:**
- `tests/test_auth.py::test_register_user` ✅
- `tests/test_auth.py::test_login_success` ✅
- `tests/test_auth.py::test_login_invalid_credentials` ✅
- `tests/test_password_security.py` (unit) ✅

**Milestone:** P00-MVP ✅

---

### NFR-02: JWT токены

**User Stories:**
- **AUTH-002**: Аутентификация пользователя
- **AUTH-003**: Обновление токена через refresh token
- **AUTH-004**: Выход из системы

**Tasks:**
- `TASK-010`: Настроить JWT с TTL: access=15min, refresh=7days
- `TASK-011`: Реализовать `/auth/login` endpoint
- `TASK-012`: Реализовать `/auth/refresh` endpoint
- `TASK-013`: Реализовать `/auth/logout` endpoint
- `TASK-014`: Написать integration тесты для токенов

**Тесты:**
- `tests/test_auth.py::test_login_success` ✅
- `tests/test_auth.py::test_refresh_token` ✅
- `tests/test_auth.py::test_refresh_invalid_token` ✅
- `tests/test_auth.py::test_logout` ✅

**Milestone:** P00-MVP ✅

---

### NFR-03: Производительность аутентификации

**User Stories:**
- **PERF-001**: Нагрузочное тестирование /login endpoint

**Tasks:**
- `TASK-020`: Настроить Locust / k6 для load testing
- `TASK-021`: Создать сценарий нагрузочного теста для /login
- `TASK-022`: Запустить baseline тест и собрать метрики
- `TASK-023`: Оптимизировать медленные операции (если p95 > 300ms)
- `TASK-024`: Документировать результаты тестирования

**Тесты:**
- `tests/load/test_login_performance.py` 🔄

**Milestone:** P04-Performance 🔄

---

### NFR-04: Структурированные ошибки

**User Stories:**
- **API-001**: Единообразная обработка ошибок во всех endpoints
- **API-002**: Request ID для отслеживания запросов

**Tasks:**
- `TASK-030`: Реализовать custom ApiError exception
- `TASK-031`: Добавить middleware для Request-ID
- `TASK-032`: Стандартизировать error responses (code, message, details)
- `TASK-033`: Написать contract tests для error format

**Тесты:**
- `tests/test_errors.py::test_error_response_structure` ✅
- `tests/test_errors.py::test_validation_error_*` ✅
- `tests/test_health.py::test_health_check` ✅

**Milestone:** P00-MVP ✅

---

### NFR-05: Уязвимости зависимостей

**User Stories:**
- **SEC-001**: Автоматическое сканирование зависимостей в CI
- **SEC-002**: Процесс управления уязвимостями

**Tasks:**
- `TASK-040`: Настроить Semgrep в GitHub Actions
- `TASK-041`: Настроить custom правила для секретов
- `TASK-042`: Документировать процесс патчинга уязвимостей
- `TASK-043`: Настроить алерты для Critical/High CVE

**Тесты:**
- `.github/workflows/ci.yml` (Security Checks) ✅
- `.semgrep.yaml` ✅

**Milestone:** P01-Setup ✅

---

### NFR-06: HTTPS Only

**User Stories:**
- **INFRA-001**: Настройка TLS сертификатов в production
- **INFRA-002**: HTTPS redirect и HSTS headers

**Tasks:**
- `TASK-050`: Получить TLS сертификаты (Let's Encrypt)
- `TASK-051`: Настроить nginx/ingress для HTTPS
- `TASK-052`: Настроить HTTP → HTTPS redirect
- `TASK-053`: Добавить HSTS header
- `TASK-054`: Тестирование с SSL Labs

**Тесты:**
- Manual testing: SSL Labs scan 🔄
- `tests/integration/test_https_redirect.py` 🔄

**Milestone:** P05-Infrastructure 🔄

---

### NFR-07: Rate Limiting

**User Stories:**
- **SEC-003**: Защита API от flood атак

**Tasks:**
- `TASK-060`: Выбрать библиотеку rate limiting (slowapi)
- `TASK-061`: Реализовать IP-based rate limiting (100 req/min)
- `TASK-062`: Реализовать User-based rate limiting (1000 req/min)
- `TASK-063`: Добавить X-RateLimit-* headers
- `TASK-064`: Написать integration тесты

**Тесты:**
- `tests/test_rate_limiting.py` 🔄

**Milestone:** P06-Security-Hardening 🔄

---

### NFR-08: Логирование безопасности

**User Stories:**
- **LOG-001**: Структурированное логирование всех запросов
- **LOG-002**: Логирование security events

**Tasks:**
- `TASK-070`: Настроить structured logging (JSON)
- `TASK-071`: Добавить request_id в каждый лог
- `TASK-072`: Логировать auth/authz события
- `TASK-073`: Настроить log aggregation (опционально)

**Тесты:**
- `tests/test_logging.py` (unit) ✅
- Manual verification: log format ✅

**Milestone:** P00-MVP ✅

---

### NFR-09: SQL Injection защита

**User Stories:**
- **SEC-005**: Код-ревью на SQL injection
- **SEC-006**: SAST проверки в CI

**Tasks:**
- `TASK-080`: Аудит всех DB запросов (убрать raw SQL)
- `TASK-081`: Настроить Semgrep правила для SQL injection
- `TASK-082`: Обучить команду OWASP Top 10
- `TASK-083`: Добавить SAST в CI pipeline

**Тесты:**
- Semgrep rules ✅
- Code review checklist ✅
- `tests/test_sql_injection.py` (security tests) 🔄

**Milestone:** P01-Setup ✅

---

### NFR-10: Session Management

**User Stories:**
- **AUTH-005**: Поддержка нескольких активных сессий

**Tasks:**
- `TASK-090`: Спроектировать схему для multi-session
- `TASK-091`: Реализовать хранение refresh tokens в БД
- `TASK-092`: Реализовать лимит 5 активных сессий
- `TASK-093`: Реализовать endpoint для просмотра сессий
- `TASK-094`: Написать integration тесты

**Тесты:**
- `tests/test_session_management.py` 📝

**Milestone:** P07-UX-Improvements 📝

---

### NFR-11: Backup и восстановление

**User Stories:**
- **INFRA-003**: Автоматические бэкапы БД
- **INFRA-004**: Disaster recovery процедура

**Tasks:**
- `TASK-100`: Настроить автоматические бэкапы PostgreSQL (pg_dump)
- `TASK-101`: Настроить хранение бэкапов (S3 / другое)
- `TASK-102`: Написать скрипт восстановления
- `TASK-103`: Провести disaster recovery drill
- `TASK-104`: Документировать процедуру

**Тесты:**
- Manual testing: restore from backup 🔄
- DR drill report 📝

**Milestone:** P08-Operations 📝

---

### NFR-12: Мониторинг доступности

**User Stories:**
- **OBS-001**: Healthcheck endpoint
- **OBS-002**: Uptime monitoring

**Tasks:**
- `TASK-110`: Реализовать `/health` endpoint
- `TASK-111`: Добавить проверки DB connectivity
- `TASK-112`: Настроить external uptime monitor (UptimeRobot)
- `TASK-113`: Настроить алерты при downtime

**Тесты:**
- `tests/test_health.py::test_health_check` ✅
- External monitoring dashboard 🔄

**Milestone:** P00-MVP (частично) ✅, P09-Observability 🔄

---

## 3. NFR → Tests Matrix

| NFR ID | Unit Tests | Integration Tests | E2E Tests | Load Tests | Security Tests |
|--------|-----------|-------------------|-----------|------------|----------------|
| NFR-01 | ✅ 5 tests | ✅ 3 tests        | -         | -          | ✅ 2 tests     |
| NFR-02 | ✅ 3 tests | ✅ 4 tests        | -         | -          | ✅ 1 test      |
| NFR-03 | -          | -                 | -         | 🔄 TBD     | -              |
| NFR-04 | ✅ 2 tests | ✅ 6 tests        | -         | -          | -              |
| NFR-05 | -          | -                 | -         | -          | ✅ CI checks   |
| NFR-06 | -          | 🔄 TBD            | 🔄 TBD    | -          | 🔄 TBD         |
| NFR-07 | -          | 🔄 TBD            | -         | 🔄 TBD     | ✅ Semgrep     |
| NFR-08 | ✅ 2 tests | -                 | -         | -          | -              |
| NFR-09 | -          | ✅ All DB tests   | -         | -          | ✅ Semgrep     |
| NFR-10 | -          | 📝 TBD            | -         | -          | -              |
| NFR-11 | -          | 📝 Manual         | -         | -          | -              |
| NFR-12 | -          | ✅ 2 tests        | 🔄 TBD    | -          | -              |

**Легенда:**
- ✅ Implemented
- 🔄 Planned / In Progress
- 📝 Backlog
- `-` Not Applicable

---

## 4. Release Plan & Milestones

### Milestone: P00-MVP (✅ Done)
**Дата:** Октябрь 2025
**NFR Scope:**
- ✅ NFR-01: Хранение паролей
- ✅ NFR-02: JWT токены
- ✅ NFR-04: Структурированные ошибки
- ✅ NFR-08: Логирование безопасности
- ✅ NFR-09: SQL Injection защита (partial)
- ✅ NFR-12: Healthcheck endpoint

**Deliverables:**
- Базовая аутентификация (регистрация, логин, refresh, logout)
- CRUD для entries с owner-based access control
- Структурированные ошибки и логирование
- Docker Compose для локального запуска
- CI/CD pipeline с базовыми проверками

---

### Milestone: P01-Setup (✅ Done)
**Дата:** Октябрь 2025
**NFR Scope:**
- ✅ NFR-05: Уязвимости зависимостей (CI setup)
- ✅ NFR-09: SQL Injection защита (SAST)

**Deliverables:**
- README.md и SECURITY.md
- `.gitattributes`, `.pre-commit-config.yaml`
- GitHub Actions CI/CD
- Semgrep security checks

---

### Milestone: P02-Code-Review (✅ Done)
**Дата:** Октябрь 2025
**Scope:**
- ✅ CODEOWNERS
- ✅ REVIEW_CHECKLIST.md
- ✅ GIT_WORKFLOW.md
- ✅ Branch protection rules

---

### Milestone: P03-NFR (🔄 Current)
**Дата:** Октябрь 2025
**NFR Scope:**
- 🔄 Документирование всех NFR
- 🔄 BDD сценарии
- 🔄 Матрица трассируемости

**Deliverables:**
- `docs/security-nfr/NFR.md`
- `docs/security-nfr/NFR_BDD.md`
- `docs/security-nfr/NFR_TRACEABILITY.md`

---

### Milestone: P04-Performance (🔄 Planned)
**Дата:** Ноябрь 2025
**NFR Scope:**
- 🔄 NFR-03: Производительность аутентификации

**Deliverables:**
- Нагрузочные тесты (Locust/k6)
- Отчет по производительности
- Оптимизации (если требуется)

---

### Milestone: P05-Infrastructure (🔄 Planned)
**Дата:** Ноябрь 2025
**NFR Scope:**
- 🔄 NFR-06: HTTPS Only
- 🔄 NFR-11: Backup и восстановление (partial)

**Deliverables:**
- TLS настройка для production
- Автоматические бэкапы БД
- Infrastructure as Code (Terraform/Ansible)

---

### Milestone: P06-Security-Hardening (🔄 Planned)
**Дата:** Декабрь 2025
**NFR Scope:**
- 🔄 NFR-07: Rate Limiting

**Deliverables:**
- Rate limiting middleware
- Security hardening checklist
- Penetration testing report

---

### Milestone: P07-UX-Improvements (📝 Backlog)
**Дата:** TBD
**NFR Scope:**
- 📝 NFR-10: Session Management

**Deliverables:**
- Multi-device session management
- Active sessions UI

---

### Milestone: P08-Operations (📝 Backlog)
**Дата:** TBD
**NFR Scope:**
- 📝 NFR-11: Backup и восстановление (full)

**Deliverables:**
- DR процедура
- DR drill отчет

---

### Milestone: P09-Observability (📝 Backlog)
**Дата:** TBD
**NFR Scope:**
- 📝 NFR-12: Мониторинг доступности (full)

**Deliverables:**
- Prometheus/Grafana dashboards
- Alerting setup
- SLA reporting

---

## 5. Dependencies & Blockers

| NFR ID | Зависит от          | Блокеры                                |
|--------|---------------------|----------------------------------------|
| NFR-03 | NFR-01, NFR-02      | Нужна staging среда для load testing   |
| NFR-06 | -                   | Нужен production environment           |
| NFR-07 | -                   | Выбор библиотеки rate limiting         |
| NFR-10 | NFR-02              | Нужна схема БД для хранения sessions   |
| NFR-11 | NFR-06              | Нужен S3 bucket или другое хранилище   |
| NFR-12 | NFR-06, NFR-11      | Нужен external monitoring сервис       |

---

## 6. Risk Matrix

| NFR ID | Риск                                          | Вероятность | Влияние | Митигация                                  |
|--------|-----------------------------------------------|-------------|---------|---------------------------------------------|
| NFR-03 | Performance не достигнет порога < 300ms       | Medium      | High    | Profiling, DB optimization, caching         |
| NFR-05 | Критическая уязвимость без патча              | Low         | High    | Временное mitigation, риск acceptance       |
| NFR-06 | TLS misconfiguration                          | Low         | High    | Использовать проверенные конфигурации       |
| NFR-07 | Rate limiting слишком строгий (UX impact)     | Medium      | Medium  | A/B testing, monitoring user feedback       |
| NFR-11 | Backup не восстанавливается корректно         | Low         | High    | Регулярные DR drills                        |

---

## 7. Compliance & Standards

| NFR ID | OWASP Top 10 | CWE | GDPR | ISO 27001 | PCI DSS |
|--------|--------------|-----|------|-----------|---------|
| NFR-01 | A02          | 259 | Art.32| A.9.4.3   | 8.2.3   |
| NFR-02 | A07          | 613 | Art.32| A.9.4.2   | 8.1.6   |
| NFR-05 | A06          | -   | -    | A.12.6.1  | 6.2     |
| NFR-06 | A02          | 319 | Art.32| A.13.1.1  | 4.1     |
| NFR-09 | A03          | 89  | -    | A.14.2.5  | 6.5.1   |

**Ссылки:**
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [GDPR](https://gdpr-info.eu/)

---

## 8. Sign-off & Approvals

| NFR ID | Dev Lead | QA Lead | Security Lead | Product Owner |
|--------|----------|---------|---------------|---------------|
| NFR-01 | ✅        | ✅       | ✅             | ✅             |
| NFR-02 | ✅        | ✅       | ✅             | ✅             |
| NFR-03 | 🔄        | 🔄       | 🔄             | 🔄             |
| NFR-04 | ✅        | ✅       | ✅             | ✅             |
| NFR-05 | ✅        | ✅       | ✅             | ✅             |
| NFR-06 | 🔄        | 🔄       | 🔄             | 🔄             |
| NFR-07 | 🔄        | 🔄       | 🔄             | 🔄             |
| NFR-08 | ✅        | ✅       | ✅             | ✅             |
| NFR-09 | ✅        | ✅       | ✅             | ✅             |
| NFR-10 | 📝        | 📝       | 📝             | 📝             |
| NFR-11 | 📝        | 📝       | 📝             | 📝             |
| NFR-12 | ✅        | 🔄       | 🔄             | ✅             |

---

## Ссылки

- [NFR документ](./NFR.md)
- [NFR BDD сценарии](./NFR_BDD.md)
- [Git Workflow](../GIT_WORKFLOW.md)
- [Review Checklist](../REVIEW_CHECKLIST.md)
- [Project README](../../README.md)

## История изменений

| Дата       | Версия | Изменения                          | Автор    |
|------------|--------|------------------------------------|----------|
| 2025-10-13 | 1.0    | Первая версия матрицы трассируемости | NKChyong |
