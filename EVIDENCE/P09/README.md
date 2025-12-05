# P09 — SBOM & SCA Evidence

Эта директория заполняется автоматически job `Security - SBOM & SCA`
(`.github/workflows/ci-sbom-sca.yml`). После каждого запуска здесь
оказываются материалы, привязанные к конкретному коммиту:

- `sbom.json` — CycloneDX SBOM, сгенерированный Syft (`anchore/syft:v1.38.0`);
- `sca_report.json` — отчёт Grype (`anchore/grype:v0.104.1`) поверх SBOM;
- `sca_summary.md` — агрегированная сводка по severity + ссылка на waiver-политику;
- `job_metadata.json` — техническая привязка к `commit/run_id`.

Все файлы загружаются как артефакт `P09_EVIDENCE-<commit>` и могут быть
использованы в DS-разделе или для дальнейшей ретроспективы.

