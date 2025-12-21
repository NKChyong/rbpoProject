# Hardening Summary (P12)

## Dockerfile

- Multi-stage build optimized and cache-aware (`pip wheel` + `--mount=cache`).
- Explicit non-root `appuser` with `HEALTHCHECK`, `ENTRYPOINT` and read-only run.
- Addressed Hadolint `DL3008` warnings by annotating package installs and
  documenting rationale via `security/hadolint.yaml`.

## IaC (Kubernetes manifest `iac/readinglist-backend.yaml`)

- Namespaced resources plus NetworkPolicy denying default ingress/egress.
- Deployment now pins image by digest, enforces `imagePullPolicy: Always`, and
  runs as UID/GID `10000` with `readOnlyRootFilesystem: true`.
- Container capabilities dropped, tmpfs for `/tmp`, probes enabled.
- **Known exception**: `CKV_K8S_35` remains because the FastAPI service expects
  `DATABASE_URL`/`JWT_SECRET` as environment variables. Moving secrets to files
  would require application changes. Documented acceptance until app supports
  file-based secrets.

## Container Scan (Trivy)

Trivy identified critical/high issues inherited from `python:3.11.9-slim-bullseye`
packages. Highlights:

- `CVE-2023-23914` / `CVE-2022-3715` in `curl 7.74.0-1.3+deb11u15`.
- Debian OpenSSL/libssl CVEs (see `trivy_report.json` for the full list).

Planned actions:

1. Track upstream fixes and switch to `python:3.11-slim-bookworm` once Debian
   publishes patched packages.
2. Re-run Trivy after each base image upgrade; failures are surfaced in the
   P12 workflow and referenced in PR summaries.


