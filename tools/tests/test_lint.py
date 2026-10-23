"""Tests for tools/lint.py. Run: uv run --with pytest --with pyyaml pytest tools/tests -q"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

LINT_PATH = Path(__file__).resolve().parents[1] / "lint.py"
spec = importlib.util.spec_from_file_location("stablehand_lint", LINT_PATH)
lint = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lint  # dataclasses resolve annotations through sys.modules
spec.loader.exec_module(lint)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


def codes(report, level=None):
    return {f.code for f in report.findings if level is None or f.level == level}


def run_path(path: Path, platform: str):
    report = lint.Report()
    lint.lint_path(report, path, platform)
    return report


GOOD_SKILL = """---
name: writing-tests
description: "Writes tests in this project's style. Use when asked to add or fix tests. Not for running the suite."
---
Write the test first.

Read [conventions](references/conventions.md) when choosing fixtures.
"""


@pytest.fixture
def good_skill(tmp_path):
    d = tmp_path / "skills" / "writing-tests"
    write(d / "SKILL.md", GOOD_SKILL)
    write(d / "references" / "conventions.md", "# Conventions\n")
    return d


def test_valid_skill_is_clean(good_skill):
    for platform in lint.PLATFORMS:
        assert not codes(run_path(good_skill, platform), "error"), platform


def test_crlf_frontmatter_parses(tmp_path):
    d = tmp_path / "writing-tests"
    write(d / "SKILL.md", GOOD_SKILL.replace("\n", "\r\n"))
    write(d / "references" / "conventions.md", "x")
    assert not codes(run_path(d, "claude-code"), "error")


def test_name_must_match_folder(tmp_path):
    d = tmp_path / "other-name"
    write(d / "SKILL.md", GOOD_SKILL.replace("references/conventions.md", "x.md"))
    write(d / "x.md", "x")
    assert "S005" in codes(run_path(d, "claude-code"), "error")


def test_unquoted_colon_breaks_yaml(tmp_path):
    d = tmp_path / "bad"
    write(d / "SKILL.md", "---\nname: bad\ndescription: Use when: deploying\n---\nbody\n")
    assert "S002" in codes(run_path(d, "antigravity"), "error")


def test_missing_reference_is_error(tmp_path):
    d = tmp_path / "writing-tests"
    write(d / "SKILL.md", GOOD_SKILL)
    assert "S020" in codes(run_path(d, "claude-code"), "error")


def test_placeholder_paths_are_not_checked(tmp_path):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", '---\nname: x-skill\ndescription: "X. Use when x."\n---\n'
          "Move bulk to `references/<topic>.md` and scripts to `scripts/*.py`.\n")
    assert "S020" not in codes(run_path(d, "claude-code"))


def test_orphan_reference_is_warning(good_skill):
    write(good_skill / "references" / "unused.md", "x")
    assert "S022" in codes(run_path(good_skill, "claude-code"), "warning")


def test_opencode_flags_claude_only_keys_and_metadata(tmp_path):
    d = tmp_path / "deploying"
    write(d / "SKILL.md", '---\nname: deploying\ndescription: "Deploys. Use when asked to deploy."\n'
          'disable-model-invocation: true\nmetadata:\n  opencode/autoinvoke: false\n---\nbody\n')
    report = run_path(d, "opencode")
    assert "S012" in codes(report, "warning")
    assert "S014" in codes(report, "error")


def test_claude_tool_names_flagged_outside_claude(tmp_path):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", '---\nname: x-skill\ndescription: "X. Use when x."\n---\nUse the Agent tool to delegate.\n')
    assert "S024" in codes(run_path(d, "opencode"), "warning")
    assert "S024" not in codes(run_path(d, "claude-code"))


def test_ignore_comment_suppresses(tmp_path):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", '---\nname: x-skill\ndescription: "X. Use when x."\n---\n'
          '<!-- stablehand-lint: ignore S024 -->\nUse the Agent tool to delegate.\n')
    assert "S024" not in codes(run_path(d, "opencode"))


def test_claude_agent_checks(tmp_path):
    f = write(tmp_path / "agents" / "reviewer.md",
              '---\nname: reviewer\ndescription: "Reviews."\ntools: Read, Grep, Bash\n'
              'permissionMode: yolo\nmodel: deepseek-chat\n---\nReview.\n')
    report = run_path(f, "claude-code")
    assert "A016" in codes(report, "error")
    assert "A015" in codes(report, "warning")
    assert "A013" not in codes(report)


def test_claude_tools_specifier_warns(tmp_path):
    f = write(tmp_path / "agents" / "rev.md",
              '---\nname: rev\ndescription: "Reviews."\ntools: Read, Bash(git diff *)\n---\nReview.\n')
    assert "A021" in codes(run_path(f, "claude-code"), "warning")


def test_antigravity_agent_unknown_tool_is_error(tmp_path):
    f = write(tmp_path / "agents" / "auditor.md",
              '---\nname: auditor\ndescription: "Audits."\ntools: [view_file, Read]\nmodel: pro\n---\nAudit.\n')
    report = run_path(f, "antigravity")
    assert "A031" in codes(report, "error")


def test_antigravity_agent_documented_tools_are_clean(tmp_path):
    f = write(tmp_path / "agents" / "auditor.md",
              '---\nname: auditor\ndescription: "Audits."\n'
              'tools: [view_file, write_to_file, replace_file_content, multi_replace_file_content, '
              'list_dir, find_by_name, grep_search, run_command, invoke_subagent, define_subagent, '
              'search_web, read_url_content]\n'
              'model: pro\n---\nAudit.\n')
    report = run_path(f, "antigravity")
    assert "A031" not in codes(report)
    assert "A032" not in codes(report)


def test_antigravity_agent_observed_tool_emits_info(tmp_path):
    f = write(tmp_path / "agents" / "auditor.md",
              '---\nname: auditor\ndescription: "Audits."\ntools: [view_file, codebase_search]\nmodel: pro\n---\nAudit.\n')
    report = run_path(f, "antigravity")
    assert "A032" in codes(report, "info")
    assert "A031" not in codes(report)


def test_antigravity_tools_must_be_list(tmp_path):
    f = write(tmp_path / "agents" / "auditor.md",
              '---\nname: auditor\ndescription: "Audits."\ntools: view_file\n---\nAudit.\n')
    assert "A030" in codes(run_path(f, "antigravity"), "error")


def test_opencode_agent_checks(tmp_path):
    f = write(tmp_path / "agents" / "code-reviewer.md",
              '---\ndescription: "Reviews."\nmode: subagent\nmodel: sonnet\ntools:\n  edit: false\n'
              'permission:\n  edit: deny\n  shell:\n    "*": deny\n    "git diff*": allow\n---\nReview.\n')
    report = run_path(f, "opencode")
    assert "A043" in codes(report, "error")
    assert "A044" in codes(report, "warning")
    assert "A047" not in codes(report)


def test_antigravity_rule_trigger(tmp_path):
    f = write(tmp_path / "rules" / "style.md", "---\ntrigger: alwaysOn\n---\nUse tabs.\n")
    assert "R001" in codes(run_path(f, "antigravity"), "error")


def test_claude_md_without_agents_import(tmp_path):
    write(tmp_path / "AGENTS.md", "# Facts\n")
    f = write(tmp_path / "CLAUDE.md", "# Claude\n")
    assert "I004" in codes(run_path(f, "claude-code"), "warning")


def test_project_opencode_collision(tmp_path):
    for base in (".claude/skills", ".opencode/skills"):
        d = tmp_path / base / "writing-tests"
        write(d / "SKILL.md", GOOD_SKILL.replace("references/conventions.md", "x.md"))
        write(d / "x.md", "x")
    report = lint.Report()
    lint.lint_project(report, tmp_path, ["claude-code", "opencode"])
    assert "P003" in codes(report, "error")


def test_project_flags_dead_workflows(tmp_path):
    (tmp_path / ".agents" / "workflows").mkdir(parents=True)
    report = lint.Report()
    lint.lint_project(report, tmp_path, ["antigravity"])
    assert "P002" in codes(report, "error")


def test_cli_exit_codes(good_skill, tmp_path):
    assert lint.main(["--platform", "claude-code", str(good_skill)]) == 0
    bad = tmp_path / "bad"
    write(bad / "SKILL.md", "no frontmatter\n")
    assert lint.main(["--platform", "claude-code", str(bad)]) == 1


def run_cards(folder: Path, today):
    report = lint.Report()
    lint.lint_cards(report, folder, today=today)
    return report


def test_card_recently_verified_is_clean(tmp_path):
    from datetime import date
    write(tmp_path / "x.md", "# Platform card: X\n\nLast verified: 2026-10-01.\n")
    assert codes(run_cards(tmp_path, date(2026, 10, 22))) == set()


def test_card_older_than_limit_warns(tmp_path):
    from datetime import date
    write(tmp_path / "x.md", "# Platform card: X\n\nLast verified: 2026-06-01. Versions checked: 1.0\n")
    assert codes(run_cards(tmp_path, date(2026, 10, 22)), "warning") == {"C002"}


def test_card_without_date_warns_and_other_files_are_skipped(tmp_path):
    from datetime import date
    write(tmp_path / "x.md", "# Platform card: X\n\nNo date here.\n")
    write(tmp_path / "guide.md", "# Writing guide\n")
    report = run_cards(tmp_path, date(2026, 10, 22))
    assert codes(report, "warning") == {"C001"}
    assert report.files_checked == 1


def test_antigravity_manifest_accepts_version_and_warns_on_unknown_keys(tmp_path):
    manifest = write(tmp_path / "plugin.json", '{"name": "x", "description": "d", "version": "2026.10.0", "bogus": 1}')
    report = lint.Report()
    lint.lint_antigravity_manifest(report, manifest)
    assert [f.message for f in report.findings if f.code == "M003"] == ["key 'bogus' may be rejected (the CLI schema disallows additional properties)"]


# --- hardening: wrong YAML types, BOM, empty values, fences, plugin paths, links ---
SKILL_HEAD = '---\nname: x-skill\ndescription: "X. Use when x."\n'


def skill(tmp_path, extra_fm="", body="body\n", name="x-skill"):
    d = tmp_path / name
    write(d / "SKILL.md", SKILL_HEAD + extra_fm + "---\n" + body)
    return d


def test_unhashable_skill_values_are_findings(tmp_path):
    d = skill(tmp_path, "effort: [high]\n1: numeric key\n")
    report = run_path(d, "claude-code")
    assert "S015" in codes(report, "warning")
    assert "S012" in codes(report, "warning")


def test_unhashable_claude_agent_values_are_findings(tmp_path):
    f = write(tmp_path / "agents" / "rev.md",
              '---\nname: rev\ndescription: "Reviews."\npermissionMode: [plan]\ncolor: {a: 1}\n'
              'effort: [low]\nmemory: [user]\n2: x\n---\nReview.\n')
    report = run_path(f, "claude-code")
    assert {"A016", "A018"} <= codes(report, "error")
    assert "A012" in codes(report, "warning")


def test_unhashable_antigravity_values_are_findings(tmp_path):
    f = write(tmp_path / "agents" / "auditor.md",
              '---\nname: auditor\ndescription: "Audits."\ntools: [view_file, {name: x}]\nmodel: [pro]\n'
              'commandExecutionPolicy: [off]\n---\nAudit.\n')
    report = run_path(f, "antigravity")
    assert {"A031", "A033", "A034"} <= codes(report, "error")
    rule = write(tmp_path / "rules" / "style.md", "---\ntrigger: [always_on]\n---\nUse tabs.\n")
    assert "R001" in codes(run_path(rule, "antigravity"), "error")


def test_unhashable_opencode_values_are_findings(tmp_path):
    f = write(tmp_path / "agents" / "rev.md",
              '---\ndescription: "Reviews."\nmode: [subagent]\npermission:\n  edit: [deny]\n'
              '  shell:\n    git: {diff: allow}\n---\nReview.\n')
    report = run_path(f, "opencode")
    assert {"A042", "A047"} <= codes(report, "error")
    assert sum(f.code == "A047" for f in report.findings) == 2


def test_utf8_bom_is_ignored(tmp_path):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", "\ufeff" + SKILL_HEAD + "---\nbody\n")
    assert not codes(run_path(d, "claude-code"), "error")
    from datetime import date
    write(tmp_path / "cards" / "x.md", "\ufeff# Platform card: X\n\nLast verified: 2026-06-01.\n")
    assert codes(run_cards(tmp_path / "cards", date(2026, 10, 22))) == {"C002"}


@pytest.mark.parametrize("value", ['""', '"   "'])
def test_empty_description_is_error(tmp_path, value):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", f"---\nname: x-skill\ndescription: {value}\n---\nbody\n")
    assert "S006" in codes(run_path(d, "claude-code"), "error")


def test_missing_name_is_warning_for_claude_and_error_for_opencode(tmp_path):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", '---\ndescription: "X. Use when x."\n---\nbody\n')
    assert "S003" in codes(run_path(d, "claude-code"), "warning")
    assert "S003" not in codes(run_path(d, "claude-code"), "error")
    assert "S003" in codes(run_path(d, "opencode"), "error")


def test_fenced_code_is_not_checked_for_links(tmp_path):
    d = skill(tmp_path, body="Example:\n\n```markdown\nSee [x](references/missing.md) and `scripts/nope.py`.\n```\n")
    assert "S020" not in codes(run_path(d, "claude-code"))


def test_links_are_normalised_and_decoded(tmp_path):
    d = skill(tmp_path, body="See [up](./../x.md) and [spaced](references/my%20file.md).\n")
    write(d / "references" / "my file.md", "x")
    report = run_path(d, "claude-code")
    assert "S021" in codes(report, "warning")
    assert "S020" not in codes(report)


def test_plugin_root_paths_are_checked(tmp_path):
    (tmp_path / ".claude-plugin").mkdir()
    write(tmp_path / "references" / "here.md", "x")
    d = skill(tmp_path / "skills", body="Read `${CLAUDE_PLUGIN_ROOT}/references/here.md` and "
              "`${CLAUDE_PLUGIN_ROOT}/references/gone.md`, or `${CLAUDE_PLUGIN_ROOT}/references/<topic>.md`.\n")
    report = run_path(d, "claude-code")
    assert [f.message for f in report.findings if f.code == "S020"] == \
        ["referenced file not found: ${CLAUDE_PLUGIN_ROOT}/references/gone.md"]


def test_shipped_claude_plugin_is_clean():
    root = Path(__file__).resolve().parents[2] / "platforms" / "claude-code"
    assert not codes(run_path(root, "claude-code"), "error")


def test_empty_frontmatter_is_recognised(tmp_path):
    doc = lint.read_doc(write(tmp_path / "x" / "SKILL.md", "---\n---\nbody\n"))
    assert doc.error is None and doc.frontmatter == {} and doc.body == "body\n"
    report = run_path(tmp_path / "x", "claude-code")
    assert "S006" in codes(report, "error")
    assert "S002" not in codes(report)


def test_walk_does_not_follow_links(tmp_path):
    d = skill(tmp_path)
    loop = d / "references" / "loop"
    loop.parent.mkdir()
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(d), str(loop))
    else:
        loop.symlink_to(d, target_is_directory=True)
    assert "S023" not in codes(run_path(d, "claude-code"))
    assert lint.walk_files(d) == [d / "SKILL.md"]


def test_opencode_agent_with_claude_only_keys_warns(tmp_path):
    f = write(tmp_path / "agents" / "rev.md",
              '---\ndescription: "Reviews."\nmode: subagent\npermissionMode: plan\nmaxTurns: 3\n'
              'tools:\n  Read: true\n---\nReview.\n')
    report = run_path(f, "opencode")
    a048 = [x for x in report.findings if x.code == "A048"]
    assert a048 and all(x.level == "warning" for x in a048)
    assert any("Claude Code tool names" in x.message for x in report.findings if x.code == "A044")


def oc_agent(tmp_path, permission: str) -> set:
    agent = write(tmp_path / ".opencode/agents/ro.md", f'---\ndescription: "Reviews."\nmode: subagent\npermission:\n{permission}---\nReview.\n')
    return {(f.level, f.code) for f in run_path(agent, "opencode").findings if f.code == "A049"}


def test_opencode_shell_without_bash_is_an_error(tmp_path):
    assert oc_agent(tmp_path, '  shell:\n    "*": deny\n') == {("error", "A049")}


def test_opencode_bash_without_shell_warns(tmp_path):
    assert oc_agent(tmp_path, '  bash: deny\n') == {("warning", "A049")}


def test_opencode_bash_and_shell_with_same_rules_are_clean(tmp_path):
    rules = '    "*": deny\n    "git diff --staged": allow\n'
    assert oc_agent(tmp_path, f"  bash:\n{rules}  shell:\n{rules}") == set()
