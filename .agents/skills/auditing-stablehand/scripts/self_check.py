# /// script
# requires-python = ">=3.11"
# ///
"""Self-check runner for the stablehand repository.

Runs sync verification, tool tests, card freshness, platform linters,
contract-to-implementation parity, release version consistency, and
available native plugin validators.

Usage:
  uv run .agents/skills/auditing-stablehand/scripts/self_check.py [--strict] [--skip-native]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PLATFORMS = ("claude-code", "antigravity", "opencode", "codex")


@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FAIL | SKIP
    detail: str
    output: str = ""


def find_repo_root() -> Path:
    """Resolve the stablehand repository root and verify its expected layout."""
    candidate = Path(__file__).resolve().parents[4]
    if (candidate / "contracts").is_dir() and (candidate / "platforms").is_dir():
        return candidate
    cwd = Path.cwd().resolve()
    if (cwd / "contracts").is_dir() and (cwd / "platforms").is_dir():
        return cwd
    sys.exit("error: must be run inside the stablehand repository (missing contracts/ and platforms/).")


def run_cmd(name: str, cmd: list[str], cwd: Path) -> CheckResult:
    """Execute a subprocess check and capture pass/fail status and concise detail."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    combined = "\n".join(part.strip() for part in (proc.stdout, proc.stderr) if part and part.strip())
    last_line = combined.splitlines()[-1] if combined else f"exit {proc.returncode}"
    status = "PASS" if proc.returncode == 0 else "FAIL"
    return CheckResult(name=name, status=status, detail=last_line, output=combined)


def check_parity(root: Path) -> CheckResult:
    """Verify every contract skill and agent exists in every implemented platform."""
    skills = sorted(p.stem for p in (root / "contracts" / "skills").glob("*.md"))
    agents = sorted(p.stem for p in (root / "contracts" / "agents").glob("*.md"))
    missing: list[str] = []
    checked = 0
    for platform in PLATFORMS:
        pdir = root / "platforms" / platform
        if not (pdir / "skills").is_dir():
            continue
        checked += 1
        for s in skills:
            if not (pdir / "skills" / s / "SKILL.md").is_file():
                missing.append(f"platforms/{platform}/skills/{s}/SKILL.md")
        for a in agents:
            ext = "toml" if platform == "codex" else "md"
            if not (pdir / "agents" / f"{a}.{ext}").is_file():
                missing.append(f"platforms/{platform}/agents/{a}.{ext}")
    if missing:
        return CheckResult("contract-parity", "FAIL", f"{len(missing)} missing", "\n".join(missing))
    return CheckResult("contract-parity", "PASS", f"{len(skills)} skills, {len(agents)} agents across {checked} platforms")


def check_versions(root: Path) -> CheckResult:
    """Verify release version consistency across manifests, README badge, and CHANGELOG."""
    claude_manifest = root / "platforms" / "claude-code" / ".claude-plugin" / "plugin.json"
    ag_manifest = root / "platforms" / "antigravity" / "plugin.json"
    readme = (root / "README.md").read_text(encoding="utf-8")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")

    claude_ver = json.loads(claude_manifest.read_text(encoding="utf-8-sig")).get("version")
    ag_ver = json.loads(ag_manifest.read_text(encoding="utf-8-sig")).get("version")
    readme_m = re.search(r"version-(\d{4}\.\d+\.\d+)-", readme)
    changelog_m = re.search(r"^## (\d{4}\.\d+\.\d+)\b", changelog, re.M)

    found = {
        "claude-plugin": claude_ver,
        "antigravity-plugin": ag_ver,
        "README": readme_m.group(1) if readme_m else None,
        "CHANGELOG": changelog_m.group(1) if changelog_m else None,
    }
    unique = set(found.values())
    if None in unique or len(unique) != 1:
        return CheckResult("version-sync", "FAIL", f"mismatch: {found}", json.dumps(found, indent=2))
    return CheckResult("version-sync", "PASS", f"all match {claude_ver}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all self-checks for the stablehand repository.")
    parser.add_argument("--strict", action="store_true", help="Pass --strict to platform and skill artifact linters.")
    parser.add_argument("--skip-native", action="store_true", help="Skip native CLI validators (agy, claude).")
    args = parser.parse_args(argv)

    root = find_repo_root()
    strict_flag = ["--strict"] if args.strict else []
    results: list[CheckResult] = [
        run_cmd("sync-check", ["uv", "run", "tools/sync.py", "--check"], root),
        run_cmd("pytest", ["uv", "run", "--with", "pytest", "--with", "pyyaml", "pytest", "tools/tests", "-q"], root),
        run_cmd("cards-freshness", ["uv", "run", "tools/lint.py", "--cards", "shared/references", "--strict"], root),
    ]

    for platform in PLATFORMS:
        if (root / "platforms" / platform / "skills").is_dir():
            results.append(run_cmd(
                f"lint:{platform}",
                ["uv", "run", "tools/lint.py", "--platform", platform, f"platforms/{platform}", *strict_flag],
                root,
            ))

    self_skill = ".agents/skills/auditing-stablehand"
    for platform in PLATFORMS:
        results.append(run_cmd(
            f"lint:self:{platform}",
            ["uv", "run", "tools/lint.py", "--platform", platform, self_skill, *strict_flag],
            root,
        ))

    results.append(check_parity(root))
    results.append(check_versions(root))

    if not args.skip_native:
        if shutil.which("agy"):
            results.append(run_cmd("native:agy", ["agy", "plugin", "validate", "--strict", "platforms/antigravity"], root))
        else:
            results.append(CheckResult("native:agy", "SKIP", "agy not found on PATH"))
        if shutil.which("claude"):
            results.append(run_cmd("native:claude", ["claude", "plugin", "validate", "."], root))
        else:
            results.append(CheckResult("native:claude", "SKIP", "claude not found on PATH"))

    width = max(len(r.name) for r in results)
    for r in results:
        print(f"{r.name:<{width}}  {r.status:<4}  {r.detail}")

    failures = [r for r in results if r.status == "FAIL"]
    if failures:
        print("\n--- Failure details ---")
        for r in failures:
            print(f"\n[{r.name}]\n{r.output}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
