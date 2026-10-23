"""Repository version rules (contracts/README.md, "Versioning"). Run with the linter tests."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALVER = re.compile(r"^(20\d{2})\.([1-9]|1[0-2])\.(0|[1-9]\d*)$")
MANIFESTS = [ROOT / "platforms/claude-code/.claude-plugin/plugin.json", ROOT / "platforms/antigravity/plugin.json"]


def key(version: str) -> tuple[int, ...]:
    return tuple(int(x) for x in version.split("."))


def contract_versions() -> dict[str, str]:
    found = {}
    for path in (ROOT / "contracts").rglob("*.md"):
        m = re.search(r"^version:\s*(\S+)\s*$", path.read_text(encoding="utf-8"), re.M)
        if m:
            found[path.relative_to(ROOT).as_posix()] = m.group(1)
    return found


def test_every_contract_has_a_calendar_version():
    versions = contract_versions()
    assert len(versions) >= 10
    bad = {p: v for p, v in versions.items() if not CALVER.match(v)}
    assert not bad, f"use YYYY.M.N (no leading zero in the month): {bad}"


def test_manifests_carry_the_current_release():
    newest = max(contract_versions().values(), key=key)
    for manifest in MANIFESTS:
        version = json.loads(manifest.read_text(encoding="utf-8"))["version"]
        assert CALVER.match(version), f"{manifest}: {version}"
        assert key(version) >= key(newest), f"{manifest} is {version}, older than contract version {newest}"
    assert len({json.loads(m.read_text(encoding="utf-8"))["version"] for m in MANIFESTS}) == 1, "plugin manifests disagree"
