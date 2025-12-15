# P11 — Evidence for OWASP ZAP Baseline

В этот каталог складываются артефакты автоматического DAST-скана:

- `zap_baseline.html` — подробный отчёт;
- `zap_baseline.json` — машинно-читаемый отчёт (используется для суммаризации);
- `zap_summary.txt` — короткая сводка по количеству алертов.

Отчёты генерируются workflow `.github/workflows/ci-p11-dast.yml`. При локальном запуске:

```bash
COMPOSE_PROJECT_NAME=p11local docker compose up -d db backend
docker run --rm \
  --network p11local_readinglist-network \
  -v $PWD/EVIDENCE/P11:/zap/wrk \
  zaproxy/zap-stable \
  zap-baseline.py \
    -t http://backend:8000 \
    -r zap_baseline.html \
    -J zap_baseline.json \
    -d -m 4 -T 300
COMPOSE_PROJECT_NAME=p11local docker compose down -v
```

## Примечание

- 2025-12-15: Последний отчёт получен из ветки `p11-dast-zap`, summary лежит в `zap_summary.txt`.

