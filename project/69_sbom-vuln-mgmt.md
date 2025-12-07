# 69. Политика работы с SBOM & уязвимостями зависимостей

Документ фиксирует практику P09: генерация SBOM, запуск SCA и
трекинг исключений (waivers).

## 1. Поток выполнения

1. Workflow `Security - SBOM & SCA`
   (`.github/workflows/ci-sbom-sca.yml`) срабатывает на `push`/`PR`
   при изменениях Python-кода, `requirements*.txt` и самой политики.
2. Syft (`anchore/syft:v1.38.0`) выпускает CycloneDX SBOM →
   `EVIDENCE/P09/sbom.json`.
3. Grype (`anchore/grype:v0.104.1`) сканирует SBOM и сохраняет отчёт
   `EVIDENCE/P09/sca_report.json`.
4. Скрипт собирает агрегированную таблицу severity (`sca_summary.md`)
   и пушит директорию целиком в артефакт `P09_EVIDENCE-<commit>`.
5. Журнал triage ведём в этом файле + `policy/waivers.yml`.

## 2. Структура `EVIDENCE/P09`

| Файл | Назначение |
|------|------------|
| `sbom.json` | CycloneDX SBOM (Syft) |
| `sca_report.json` | JSON отчёт Grype |
| `sca_summary.md` | Markdown с итогами, планами фикса/waivers |
| `job_metadata.json` | Привязка к commit/run_id/time |

Файлы остаются в репозитории (через `.gitkeep`) и загружаются в
артефакт GitHub Actions (retention 30 дней). Их можно прикладывать к
разделу DS1 итогового отчёта.

## 3. Политика реагирования

| Severity | Требование |
|----------|------------|
| Critical | Hotfix в течение 24 часов; блокирующий чек |
| High     | Оценка ≤72 часов, фикс ≤7 дней или waiver с ревью |
| Medium   | План фикса в спринте ≤30 дней |
| Low/Negl | Наблюдаем, документируем при массовых находках |

- SCA запускается для каждого PR, чтобы regression ловились до merge.
- В README описан способ ручного запуска (`workflow_dispatch`).
- Итоговая сводка попадает в `GITHUB_STEP_SUMMARY` → удобно ссылаться в PR.

## 4. Waiver-процесс

1. Зафиксировать находку в `policy/waivers.yml`.
2. Указать идентификатор (CVE/GHSA), пакет, версию, причину и срок
   пересмотра.
3. Приложить ссылку на задачу/issue, где хранится план исправления.
4. По окончании срока либо продлить waiver (осознанно), либо закрыть
   его фиксом (обновление зависимости/кода).

### 4.1 Активные waivers

#### Waiver: nth-check (CVE-2021-3803) {#waiver-nth-check}

- **Источник:** React build chain → `svgo` → `nth-check@1.0.2`.
- **Severity:** High (ReDoS).
- **Обоснование:** зависимость используется только на этапе сборки
  ассетов (`npm run build`). Production bundle не содержит уязвимый код.
- **Митигирующие меры:** ограничение доступа к CI runners,
  контроль входных данных (SVG) и план миграции на Vite.
- **План:** задача [issue #7](https://github.com/NKChyong/rbpoProject/issues/7),
  срок до 31.03.2026. После миграции waiver будет удалён.

#### Waiver: webpack-dev-server (GHSA-9jgg-88mc-972h) {#waiver-webpack-dev-server}

- **Источник:** `react-scripts@5.0.1` подтягивает `webpack-dev-server@4.15.2`.
- **Severity:** High (source leak при посещении злого сайта).
- **Обоснование:** dev server используется только локально; публикации
  через него не ведутся. Обновление до 5.2.1 требует миграции на новый
  инструментарий (CRA не поддерживает wds v5).
- **Митигирующие меры:** ограничение запуска dev server только на
  `localhost`, отключение проксирования внешних источников, контроль
  браузеров/расширений. В репозитории запрещено деплоить сборки,
  сделанные на dev server.
- **План:** [issue #8](https://github.com/NKChyong/rbpoProject/issues/8)
  описывает переход на Vite/Webpack 5. После миграции waiver снимем
  (ETA Q2 2026).

## 5. Как воспроизвести локально

```
docker run --rm -v $PWD:/work -w /work anchore/syft:v1.38.0 \
  packages dir:. -o cyclonedx-json > EVIDENCE/P09/sbom.json

docker run --rm -v $PWD:/work -w /work anchore/grype:v0.104.1 \
  sbom:/work/EVIDENCE/P09/sbom.json -o json > EVIDENCE/P09/sca_report.json

echo "# SCA summary" > EVIDENCE/P09/sca_summary.md
jq '[.matches[].vulnerability.severity] | group_by(.) | map({(.[0]): length}) | add' \
  EVIDENCE/P09/sca_report.json >> EVIDENCE/P09/sca_summary.md || true
```

> `docker` и `jq` должны быть доступны. В CI используется та же пара команд.

