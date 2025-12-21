# P12 – IaC & Container Security Evidence

Artifacts in this folder are produced by the `Security - IaC & Container (P12)`
workflow (`.github/workflows/ci-p12-iac-container.yml`) and the helper
commands from the course snippets.

| File | Description |
| --- | --- |
| `hadolint_report.json` | Static analysis of `Dockerfile` with repo-specific config. |
| `checkov_report.json` | Checkov scan for `iac/readinglist-backend.yaml`. |
| `trivy_report.json` | High/Critical findings for the `readinglist:local` image. |
| `hardening_summary.md` | Manual log of mitigations and outstanding risks. |

To refresh reports locally:

```bash
docker run --rm -v $PWD:/work hadolint/hadolint \
  hadolint -f json -c /work/security/hadolint.yaml /work/Dockerfile \
  > EVIDENCE/P12/hadolint_report.json

docker build -t readinglist:local .

docker run --rm -v $PWD:/work bridgecrew/checkov \
  -d /work/iac -o json --compact \
  --config-file /work/security/checkov.yaml --skip-download \
  > EVIDENCE/P12/checkov_report.json

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $PWD:/work aquasec/trivy:0.53.0 image readinglist:local \
  --format json --severity CRITICAL,HIGH \
  --output /work/EVIDENCE/P12/trivy_report.json
```


