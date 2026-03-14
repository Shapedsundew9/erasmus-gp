# Development

| Principles | Development Environment | Build Environment | Deployment |
| ------------ | ------------------------- | ------------------- | ------------ |
| Mono-repo | VSCode | Docker | Google Cloud or AWS |
| Minimise distributed dependencies | Pylint | Devcontainer | Pypy |
| Design For Security | Pylance | Syft | Docker Hub |
| Dev config in repo | Black | Dependency Track | Medium |
| Maximise reuse | unittest | SBoM file | Google docs |
| Input syntax validation | Snyk | Full stack test | K8s |
| Input semantic validation | codecov.io | Github pipeline | Grafana |
| Data digitally signed | ChatGPT | SCA | Prometheus |
| JSON public data at rest | Git (Github) | SAST | |
| Leverage Generative AI | Github Co-pilot | | |
| | Gemini CLI | | |
| | AI Code reviewer | | |
| | Mermaid charts | | |
| | (Github) Markdown | | |

## Devcontainer Environment Variables & Secrets

This repository uses a secrets-safe devcontainer workflow:

- Shared config is committed.
- Sensitive values are injected from environment secrets.
- Personal access tokens and private keys must not be committed.

### Required and optional variables

- `POSTGRES_PASSWORD` (required for database auth)
- `PGADMIN_DEFAULT_PASSWORD` (required for pgAdmin login)
- `RELEASE_DATA_MANAGER_TOKEN` (optional; required only for `upload` / `sync` data release operations)
- `PRIVATE_KEY_PEM_B64` (optional; base64 PEM private key for signing flows)

### GitHub Codespaces

Define repository or organization Codespaces secrets using the same variable names.
The devcontainer reads these at startup.

### Local development without plaintext secrets in workspace files

Use host environment variables and launch VS Code from that shell.

#### Linux/macOS (bash/zsh)

```bash
export RELEASE_DATA_MANAGER_TOKEN="<new_pat_value>"
export PRIVATE_KEY_PEM_B64="$(base64 -w0 ~/.egppy/private_key.pem)"
code .
```

If your `base64` command does not support `-w0` (for example macOS):

```bash
export PRIVATE_KEY_PEM_B64="$(base64 ~/.egppy/private_key.pem | tr -d '\n')"
```

#### Windows PowerShell

```powershell
$env:RELEASE_DATA_MANAGER_TOKEN = "<new_pat_value>"
$env:PRIVATE_KEY_PEM_B64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME/.egppy/private_key.pem"))
code .
```

### Security note

If a PAT or private key is exposed in plain text (chat, logs, screenshots, or committed files),
revoke/rotate it immediately and replace it in your secret store.

### Unit test key requirements

Most unit tests do not require real secret values. In particular, signing-related unit tests
use ephemeral/generated key pairs and/or patched key loaders in test code.

- `PRIVATE_KEY_PEM_B64` is not required for standard unit-test runs.
- `RELEASE_DATA_MANAGER_TOKEN` is only required for real upload operations, not for mocked unit tests.

Real secret injection is only needed when validating runtime/integration flows that intentionally
exercise external services or real secret files.

### CI expectations

Pull requests should run unit tests without requiring repository or organization secrets.
If a test requires real credentials or external services, treat it as an integration test and keep
it out of the default PR unit-test gate.
