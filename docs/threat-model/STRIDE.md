# STRIDE Threat Analysis - Reading List API

> **Проект:** Reading List API
> **Версия:** 1.0
> **Дата:** Октябрь 2025
> **Автор:** NKChyong

## Введение

Данный документ содержит анализ угроз по методологии STRIDE для Reading List API. Анализ основан на потоках данных, идентифицированных в [DFD.md](./DFD.md), и связан с нефункциональными требованиями из [NFR.md](../security-nfr/NFR.md).

### STRIDE Категории

- **S** (Spoofing) - Подделка идентичности
- **T** (Tampering) - Изменение данных
- **R** (Repudiation) - Отказ от действий
- **I** (Information Disclosure) - Раскрытие информации
- **D** (Denial of Service) - Отказ в обслуживании
- **E** (Elevation of Privilege) - Повышение привилегий

---

## 1. Анализ угроз по потокам (Flow-based STRIDE)

### F2: POST /api/v1/auth/register (User Registration)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F2: /register** | **S: Spoofing** | R1 | Атакующий регистрирует аккаунт с чужим email | Email verification (будущее), rate limiting | NFR-07 | Integration тесты |
| **F2: /register** | **T: Tampering** | R2 | Подмена данных в запросе (XSS в username) | Input validation (Pydantic), output escaping | NFR-04 | Unit tests, SAST |
| **F2: /register** | **D: DoS** | R3 | Массовая регистрация ботами | Rate limiting (100 req/min per IP) | NFR-07 | Load testing |

**Обоснование:**
- Регистрация - entry point для атак, критический для безопасности системы
- Слабые пароли могут быть скомпрометированы → требуется валидация (NFR-01)
- Rate limiting предотвращает автоматизированные атаки

**Связанные тесты:**
- `tests/test_auth.py::test_register_user` ✅
- `tests/test_auth.py::test_register_duplicate_email` ✅
- `tests/test_errors.py::test_validation_error_missing_fields` ✅

---

### F3: POST /api/v1/auth/login (User Login)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F3: /login** | **S: Spoofing** | R4 | Брутфорс атака на пароли | Bcrypt CF=12 (slow hashing), rate limiting | NFR-01, NFR-07 | NFR-03 (p95 < 300ms) |
| **F3: /login** | **I: Info Disclosure** | R5 | Различные ошибки для "user not found" vs "wrong password" | Generic error: "Invalid credentials" | NFR-04 | tests/test_auth.py |
| **F3: /login** | **R: Repudiation** | R6 | Пользователь отрицает неуспешные попытки входа | Логирование всех login attempts (success/fail) | NFR-08 | Structured logs |

**Обоснование:**
- Login - самая частая точка атак (credential stuffing, brute force)
- Generic error messages предотвращают user enumeration
- Логирование критично для forensics и compliance

**Связанные тесты:**
- `tests/test_auth.py::test_login_success` ✅
- `tests/test_auth.py::test_login_invalid_credentials` ✅
- `tests/test_auth.py::test_login_nonexistent_user` ✅

---

### F4: GET /api/v1/entries (Read Entries)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F4: /entries** | **E: Elevation of Privilege** | R7 | IDOR: пользователь получает доступ к чужим entries | owner_id filtering в SQL WHERE clause | NFR-09 | tests/test_entries.py::test_get_entry_forbidden |
| **F4: /entries** | **I: Info Disclosure** | R8 | Утечка данных через verbose error messages | RFC7807 structured errors, no stack traces | NFR-04 | tests/test_errors.py |
| **F4: /entries** | **T: Tampering** | R9 | SQL injection через параметр ?status= | ORM (SQLAlchemy), параметризованные запросы | NFR-09 | Semgrep rules, unit tests |

**Обоснование:**
- IDOR (Insecure Direct Object Reference) - критическая уязвимость для multi-tenant систем
- Owner-based access control - основа безопасности Reading List
- SQL injection возможен в query parameters

**Связанные тесты:**
- `tests/test_entries.py::test_get_entry_forbidden` ✅
- `tests/test_entries.py::test_list_entries_with_status_filter` ✅
- `tests/test_errors.py::test_validation_error_invalid_status_filter` ✅

---

### F5: POST /api/v1/entries (Create Entry)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F5: /entries** | **T: Tampering** | R10 | XSS через поле `title` или `link` | Input validation (Pydantic), output escaping в React | NFR-04 | Unit tests, SAST |
| **F5: /entries** | **D: DoS** | R11 | Создание огромного количества entries одним пользователем | Rate limiting (1000 req/min per user) | NFR-07 | Load tests |
| **F5: /entries** | **I: Info Disclosure** | R12 | Утечка owner_id другого пользователя через error | owner_id берется из JWT, не из request body | NFR-02 | Unit tests |

**Обоснование:**
- XSS в title/link может скомпрометировать других пользователей
- DoS через создание записей может заполнить БД
- owner_id должен всегда браться из токена, не из input

**Связанные тесты:**
- `tests/test_entries.py::test_create_entry` ✅
- `tests/test_entries.py::test_create_entry_unauthorized` ✅
- `tests/test_entries.py::test_create_entry_invalid_kind` ✅

---

### F7: Nginx → FastAPI (Internal Proxy)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F7: Proxy** | **S: Spoofing** | R13 | Header injection (X-Forwarded-For spoofing) | Доверие только внутренним IP, validation headers | - | Config review |
| **F7: Proxy** | **T: Tampering** | R14 | Man-in-the-middle в internal network | mTLS для production (рекомендация) | NFR-06 | Infrastructure review |

**Обоснование:**
- Internal HTTP без TLS уязвим к MITM, если сеть скомпрометирована
- Header spoofing может обойти rate limiting или логирование

**Связанные артефакты:**
- `nginx.conf` configuration review
- Docker network isolation

---

### F9: JWT Validation (Auth Service)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F9: JWT** | **S: Spoofing** | R15 | Подделка JWT токена с слабым секретом | Сильный JWT secret (256+ бит), алгоритм HS256/RS256 | NFR-02 | Unit tests |
| **F9: JWT** | **R: Repudiation** | R16 | Использование скомпрометированного токена после logout | Token blacklist/revocation | NFR-02 | tests/test_auth.py::test_logout |
| **F9: JWT** | **I: Info Disclosure** | R17 | Утечка JWT в логах или URL | JWT только в Authorization header, не в URL | NFR-08 | Log analysis |

**Обоснование:**
- JWT безопасность критична для всей системы аутентификации
- Короткий TTL (15 min) снижает риск компрометации access token
- Logout должен инвалидировать refresh token

**Связанные тесты:**
- `tests/test_auth.py::test_refresh_token` ✅
- `tests/test_auth.py::test_refresh_invalid_token` ✅
- `tests/test_auth.py::test_logout` ✅

---

### F13: User Service → PostgreSQL (Password Storage)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F13: DB Write** | **I: Info Disclosure** | R18 | Утечка plain-text паролей при DB dump | Bcrypt hashing, никогда не хранить plain-text | NFR-01 | Unit tests |
| **F13: DB Write** | **T: Tampering** | R19 | SQL injection при создании пользователя | ORM (SQLAlchemy), параметризованные запросы | NFR-09 | Semgrep, SAST |

**Обоснование:**
- Пароли - самые чувствительные данные в системе
- Хеширование критично для защиты при DB breach
- ORM предотвращает SQL injection

**Связанные тесты:**
- `tests/test_auth.py::test_register_user` (проверяет хеширование) ✅
- Unit tests для `user_service.py`

---

### F14: Entry Service → PostgreSQL (Entry Operations)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F14: DB Query** | **E: Elevation of Privilege** | R20 | Обход owner_id фильтра через IDOR | Все queries включают WHERE owner_id = current_user_id | NFR-09 | Integration tests |
| **F14: DB Query** | **I: Info Disclosure** | R21 | Утечка записей других пользователей | RBAC: только admin может видеть все entries | NFR-09 | tests/test_entries.py::test_admin_can_access_all_entries |

**Обоснование:**
- owner_id filtering - основной механизм data isolation
- Админ должен иметь отдельную логику для доступа ко всем данным
- Каждый query должен проходить code review на IDOR

**Связанные тесты:**
- `tests/test_entries.py::test_get_entry_forbidden` ✅
- `tests/test_entries.py::test_admin_can_access_all_entries` ✅

---

### F15: Entry Service → External Metadata API (Optional)

| Поток/Элемент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|---------|-----------------|----------|---------------|-------------------|
| **F15: External API** | **T: Tampering** | R22 | Внешний API возвращает вредоносные данные | Валидация response, whitelist URLs | - | Unit tests (mock API) |
| **F15: External API** | **D: DoS** | R23 | Внешний API недоступен или медленный | Timeout (5s), retry logic, circuit breaker | - | Integration tests |
| **F15: External API** | **S: SSRF** | R24 | SSRF через user-controlled URL | Whitelist allowed domains, no internal IPs | - | Security tests |

**Обоснование:**
- Внешние API не доверяются и могут быть скомпрометированы
- SSRF может привести к доступу к internal resources
- Timeout критичен для предотвращения DoS

**Связанные артефакты:**
- Mock tests для external API (если реализовано)
- Whitelist configuration

---

## 2. Анализ угроз по компонентам (Component-based STRIDE)

### Компонент: FastAPI Backend

| Компонент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------|------------------|---------|-----------------|----------|---------------|-------------------|
| **FastAPI** | **D: DoS** | R25 | Memory exhaustion через большие payloads | Request size limit (10 MB) | - | Configuration |
| **FastAPI** | **I: Info Disclosure** | R26 | Debug mode в production раскрывает stack traces | DEBUG=False в production | - | Config review |
| **FastAPI** | **R: Repudiation** | R27 | Отсутствие логирования критических действий | Structured logging с request_id | NFR-08 | Log analysis |

**Обоснование:**
- Debug mode в production - классическая ошибка конфигурации
- Request size limits предотвращают memory exhaustion
- Логирование критично для audit trail

**Связанные артефакты:**
- `app/main.py` configuration
- `app/core/logging.py` implementation

---

### Компонент: PostgreSQL Database

| Компонент | Угроза (STRIDE) | Risk ID | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------|------------------|---------|-----------------|----------|---------------|-------------------|
| **PostgreSQL** | **I: Info Disclosure** | R28 | Утечка DB dump с чувствительными данными | Encrypted backups, restricted access | NFR-11 | Backup procedure review |
| **PostgreSQL** | **T: Tampering** | R29 | Прямое подключение к БД минуя приложение | Firewall rules, DB user permissions | - | Infrastructure review |
| **PostgreSQL** | **E: Elevation of Privilege** | R30 | DB user имеет больше прав чем нужно | Принцип least privilege, отдельный user для app | - | DB audit |

**Обоснование:**
- БД содержит все критичные данные
- Прямой доступ к БД обходит application-level controls
- Least privilege критичен для ограничения impact при компрометации

**Связанные артефакты:**
- PostgreSQL configuration
- IAM/user permissions audit

---

## 3. Сводная таблица угроз

### По категориям STRIDE

| Категория | Количество угроз | Высокий риск | Средний риск | Низкий риск |
|-----------|------------------|--------------|--------------|-------------|
| **S** (Spoofing) | 5 | R4, R15 | R1, R13 | - |
| **T** (Tampering) | 7 | R9, R19 | R2, R10, R14, R22 | - |
| **R** (Repudiation) | 3 | - | R6, R16, R27 | - |
| **I** (Info Disclosure) | 6 | R18, R21 | R5, R8, R17, R28 | R26 |
| **D** (Denial of Service) | 5 | - | R3, R11, R23, R25 | - |
| **E** (Elevation of Privilege) | 4 | R7, R20 | R30 | - |

**Итого:** 30 идентифицированных угроз

---

## 4. Покрытие NFR

Связь STRIDE угроз с NFR из P03:

| NFR ID | Связанные угрозы | Покрытие |
|--------|------------------|----------|
| **NFR-01** (Passwords) | R4, R18 | ✅ Полное |
| **NFR-02** (JWT) | R15, R16, R17 | ✅ Полное |
| **NFR-04** (Errors) | R5, R8, R12 | ✅ Полное |
| **NFR-06** (HTTPS) | R14 | ⚠️ Частичное |
| **NFR-07** (Rate Limiting) | R1, R3, R4, R11 | 🔄 Planned |
| **NFR-08** (Logging) | R6, R17, R27 | ✅ Полное |
| **NFR-09** (SQL Injection) | R7, R9, R19, R20, R21 | ✅ Полное |

---

## 5. Приоритизация угроз (Top 10)

| Ранг | Risk ID | Угроза | STRIDE | Приоритет | Статус контроля |
|------|---------|--------|--------|-----------|-----------------|
| 1 | R4 | Брутфорс атака на /login | S | 🔴 Critical | ✅ Implemented |
| 2 | R7 | IDOR в /entries | E | 🔴 Critical | ✅ Implemented |
| 3 | R18 | Утечка plain-text паролей | I | 🔴 Critical | ✅ Implemented |
| 4 | R20 | Обход owner_id фильтра | E | 🔴 Critical | ✅ Implemented |
| 5 | R9 | SQL injection в query params | T | 🔴 High | ✅ Implemented |
| 6 | R15 | Подделка JWT токена | S | 🔴 High | ✅ Implemented |
| 7 | R10 | XSS через title/link | T | 🟡 High | ✅ Implemented |
| 8 | R3 | DoS через массовую регистрацию | D | 🟡 Medium | 🔄 Planned |
| 9 | R5 | User enumeration через errors | I | 🟡 Medium | ✅ Implemented |
| 10 | R22 | External API tampering | T | 🟡 Medium | 📝 N/A (не реализовано) |

---

## 6. Gaps и рекомендации

### Текущие gaps

1. **Rate Limiting (NFR-07)**: Не полностью реализовано
   - **Рекомендация:** Добавить slowapi middleware
   - **Срок:** P06-Security-Hardening

2. **HTTPS для internal communication (NFR-06)**: HTTP между Nginx и Backend
   - **Рекомендация:** mTLS для production
   - **Срок:** P05-Infrastructure

3. **PostgreSQL SSL**: Соединение к БД не шифруется
   - **Рекомендация:** Включить `sslmode=require`
   - **Срок:** P05-Infrastructure

4. **External API security (F15)**: Не реализовано
   - **Рекомендация:** Whitelist + validation при реализации
   - **Срок:** Future feature

### Сильные стороны

1. ✅ **Strong authentication**: Bcrypt CF=12, JWT с коротким TTL
2. ✅ **SQL injection protection**: 100% через ORM
3. ✅ **IDOR prevention**: owner_id filtering на всех endpoints
4. ✅ **Error handling**: RFC7807, no stack traces
5. ✅ **Logging**: Structured JSON logs с request_id

---

## 7. Ссылки

- [Data Flow Diagram (DFD)](./DFD.md)
- [Risk Register](./RISKS.md)
- [NFR Documentation](../security-nfr/NFR.md)
- [OWASP STRIDE Threat Modeling](https://owasp.org/www-community/Threat_Modeling_Process)
- [Microsoft STRIDE](https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)

---

## История изменений

| Дата       | Версия | Изменения                    | Автор    |
|------------|--------|------------------------------|----------|
| 2025-10-13 | 1.0    | Первая версия STRIDE анализа | NKChyong |
