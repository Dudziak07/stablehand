"""Tests for tools/sync.py. Run with the linter tests."""

import importlib.util
import sys
from pathlib import Path

SYNC_PATH = Path(__file__).resolve().parents[1] / "sync.py"
spec = importlib.util.spec_from_file_location("stablehand_sync", SYNC_PATH)
sync = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sync
spec.loader.exec_module(sync)


def test_empty_contract_frontmatter_means_no_references(tmp_path, monkeypatch):
    monkeypatch.setattr(sync, "CONTRACTS", tmp_path)
    (tmp_path / "a.md").write_text("---\n---\n# a\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("---\nid: b\nreferences:\n---\n# b\n", encoding="utf-8")
    (tmp_path / "c.md").write_text("﻿---\nreferences: [x.md, \"@platform\"]\n---\n", encoding="utf-8")
    assert sync.contract_references("a", "opencode") == []
    assert sync.contract_references("b", "opencode") == []
    assert sync.contract_references("c", "opencode") == ["x.md", "opencode.md"]


def test_skill_without_contract_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(sync, "ROOT", tmp_path)
    monkeypatch.setattr(sync, "CONTRACTS", tmp_path / "contracts" / "skills")
    for skill in ("known", "orphan"):
        (tmp_path / "platforms" / "opencode" / "skills" / skill).mkdir(parents=True)
    (tmp_path / "contracts" / "skills").mkdir(parents=True)
    (tmp_path / "contracts" / "skills" / "known.md").write_text("---\nid: known\n---\n", encoding="utf-8")
    assert sync.skills_without_contract("opencode") == ["platforms/opencode/skills/orphan"]
