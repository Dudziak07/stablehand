# Security Policy

## Supported versions

stablehand uses calendar versioning (`YYYY.M.N`). Security updates apply only to the latest release and `main`.

| Version | Supported |
|---|---|
| `2026.11.x` (latest) | Yes |
| `< 2026.11.0` | No |

## Scope

Security reports are most helpful for:

- **CLI tools** in [`tools/`](tools/) and [`.agents/skills/auditing-stablehand/scripts/self_check.py`](.agents/skills/auditing-stablehand/scripts/self_check.py) (path traversal, symlink/junction handling, unintended file writes, command injection);
- **Plugin manifests and installation hooks** under [`platforms/`](platforms/) and [`.claude-plugin/`](.claude-plugin/);
- **Read-only boundary bypasses** in shipped agents (`artifact-reviewer`, `scenario-runner`, `platform-researcher`);
- **Evaluation runners or fixtures** executing unexpected commands outside scratch workspaces.

## Reporting a vulnerability

**Do not report security vulnerabilities through public GitHub issues or pull requests.**

Report vulnerabilities privately through GitHub Security Advisories:

- <https://github.com/Dudziak07/stablehand/security/advisories/new>

Please include:

- A description of the issue and affected files, platform, or tool;
- Minimal steps or a proof of concept to reproduce the issue;
- Impact assessment (what an attacker or untrusted repository could read, write, or execute).

## Response timeline

- **Acknowledgement:** within 7 days of receiving the report.
- **Fix and disclosure:** we will coordinate a fix and publish release notes once a patched version is available.
