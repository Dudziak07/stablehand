"""Tests for tools/lint.py. Run: uv run --with pytest --with pyyaml pytest tools/tests -q"""

import importlib.util
import json
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
          'when_to_use: Deploy after review\nmetadata:\n  opencode/autoinvoke: false\n---\nbody\n')
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
    assert "P003" in codes(report, "warning")


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
              '---\ndescription: "Reviews."\nmode: [subagent]\npermissions:\n'
              '  - action: shell\n    resource: "*"\n    effect: [deny]\n---\nReview.\n')
    report = run_path(f, "opencode")
    assert "A042" in codes(report, "error")
    assert "A047" in codes(report, "error")


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


def test_missing_name_is_a_warning_on_every_platform(tmp_path):
    d = tmp_path / "x-skill"
    write(d / "SKILL.md", '---\ndescription: "X. Use when x."\n---\nbody\n')
    for platform in lint.PLATFORMS:
        assert "S003" in codes(run_path(d, platform), "warning"), platform
        assert "S003" not in codes(run_path(d, platform), "error"), platform


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


def oc_agent(tmp_path, permissions: str) -> set:
    agent = write(tmp_path / ".opencode/agents/ro.md", f'---\ndescription: "Reviews."\nmode: subagent\npermissions:\n{permissions}---\nReview.\n')
    return {(f.level, f.code) for f in run_path(agent, "opencode").findings if f.code in ("A046", "A047", "A049")}


def test_opencode_v1_action_bash_is_an_error(tmp_path):
    assert oc_agent(tmp_path, '  - action: bash\n    resource: "*"\n    effect: deny\n') == {("error", "A049")}


def test_opencode_v1_action_task_is_an_error(tmp_path):
    assert oc_agent(tmp_path, '  - action: task\n    resource: "*"\n    effect: deny\n') == {("error", "A049")}


def test_opencode_v1_permission_map_warns(tmp_path):
    agent = write(tmp_path / ".opencode/agents/ro.md",
                  '---\ndescription: "Reviews."\nmode: subagent\npermission:\n  edit: deny\n---\nReview.\n')
    assert ("warning", "A049") in {(f.level, f.code) for f in run_path(agent, "opencode").findings if f.code == "A049"}


def test_opencode_v2_permissions_shell_and_subagent_are_clean(tmp_path):
    rules = ('  - action: edit\n    resource: "*"\n    effect: deny\n'
             '  - action: shell\n    resource: "*"\n    effect: deny\n'
             '  - action: shell\n    resource: "git diff --staged"\n    effect: allow\n'
             '  - action: subagent\n    resource: "*"\n    effect: deny\n')
    assert oc_agent(tmp_path, rules) == set()


def test_antigravity_agent_flash_lite_and_new_documented_tools(tmp_path):
    f = write(tmp_path / "agents" / "sweeper.md",
              '---\nname: sweeper\ndescription: "Sweeps."\n'
              'tools: [view_file, manage_task, schedule, send_message, manage_subagents, '
              'ask_question, generate_image, call_mcp_tool, run_workflow]\n'
              'model: flash_lite\n---\nSweep.\n')
    report = run_path(f, "antigravity")
    assert not ({"A031", "A032", "A033"} & codes(report))


def test_antigravity_agent_model_facing_alias_is_error_with_hint(tmp_path):
    f = write(tmp_path / "agents" / "worker.md",
              '---\nname: worker\ndescription: "Edits."\ntools: [read_file, edit_file, write_file]\n---\nWork.\n')
    report = run_path(f, "antigravity")
    msgs = [x.message for x in report.findings if x.code == "A031" and x.level == "error"]
    assert len(msgs) == 3
    assert any("view_file" in m for m in msgs)
    assert any("replace_file_content" in m for m in msgs)
    assert any("write_to_file" in m for m in msgs)


def test_antigravity_skill_disable_model_invocation(tmp_path):
    d = skill(tmp_path, "disable-model-invocation: true\n")
    assert not codes(run_path(d, "antigravity"), "warning")
    bad = skill(tmp_path / "bad", 'disable-model-invocation: "yes"\n')
    assert "S015" in codes(run_path(bad, "antigravity"), "warning")


def test_antigravity_manifest_v1_schema_keys_and_checks(tmp_path):
    root = tmp_path / "good-plugin"
    write(root / "assets" / "logo.svg", "<svg/>")
    write(root / "skills" / "hello" / "SKILL.md", GOOD_SKILL.replace("writing-tests", "hello").replace("references/conventions.md", "x.md"))
    write(root / "skills" / "hello" / "x.md", "x")
    manifest = write(root / "plugin.json",
                     '{"$schema":"https://antigravity.google/schemas/v1/plugin.json","name":"good-plugin",'
                     '"displayName":"Good Plugin","description":"Does good things.","version":"1.0.0",'
                     '"disabled":false,"logo":"assets/logo.svg","suggestedPrompts":["One","Two","Three"],'
                     '"author":{"name":"Team","url":"https://example.com"},"homepage":"https://example.com",'
                     '"repository":"https://github.com/example/good","license":"MIT","keywords":["good"]}')
    report = lint.Report()
    lint.lint_antigravity_manifest(report, manifest)
    assert report.findings == []

    multi = tmp_path / "multi"
    write(multi / "skills" / "hello" / "SKILL.md", GOOD_SKILL.replace("writing-tests", "hello").replace("references/conventions.md", "x.md"))
    write(multi / "skills" / "hello" / "x.md", "x")
    write(multi / "plugin.json", '{"bogus": 1}')
    write(multi / ".antigravity-plugin" / "plugin.json", '{"name": "Multi_Plugin", "description": "d", "source": "old", "logo": "assets/missing.svg", "suggestedPrompts": ["1", "2", "3", "4"]}')
    mreport = run_path(multi, "antigravity")
    assert "M003" in codes(mreport, "warning")
    assert "M004" in codes(mreport, "warning")
    assert any("deprecated" in f.message for f in mreport.findings if f.code == "M003")


def test_shipped_all_platforms_and_maintainer_skill_are_clean():
    repo_root = Path(__file__).resolve().parents[2]
    for platform in lint.PLATFORMS:
        report = run_path(repo_root / "platforms" / platform, platform)
        assert not codes(report, "error"), (platform, report.findings)
        assert not codes(report, "warning"), (platform, report.findings)
    maintainer = repo_root / ".agents" / "skills" / "auditing-stablehand"
    for platform in lint.PLATFORMS:
        report = run_path(maintainer, platform)
        assert not codes(report, "error"), (platform, report.findings)
        assert not codes(report, "warning"), (platform, report.findings)


def _run_cli(monkeypatch, capsys, argv):
    monkeypatch.setattr(sys, "argv", ["lint.py", *argv])
    code = lint.main()
    captured = capsys.readouterr()
    return code, captured.out


def test_cli_json_clean_skill(good_skill, monkeypatch, capsys):
    code, out = _run_cli(monkeypatch, capsys, ["--json", "--platform", "claude-code", str(good_skill)])
    assert code == 0
    data = json.loads(out)
    assert data == {
        "files_checked": 1,
        "errors": 0,
        "warnings": 0,
        "infos": 0,
        "findings": [],
    }


def test_cli_json_invalid_skill(tmp_path, monkeypatch, capsys):
    bad = tmp_path / "skills" / "bad-skill"
    write(bad / "SKILL.md", "---\nname: Wrong_Name\ndescription: \"Short.\"\n---\nBody.\n")
    code, out = _run_cli(monkeypatch, capsys, ["--json", "--platform", "claude-code", str(bad)])
    assert code == 1
    data = json.loads(out)
    assert data["files_checked"] == 1
    assert data["errors"] > 0
    assert data["errors"] == sum(1 for f in data["findings"] if f["level"] == "error")
    assert data["warnings"] == sum(1 for f in data["findings"] if f["level"] == "warning")
    assert data["infos"] == sum(1 for f in data["findings"] if f["level"] == "info")
    for finding in data["findings"]:
        assert set(finding) == {"level", "code", "path", "message"}


def test_cli_json_warnings_and_strict(tmp_path, monkeypatch, capsys):
    warn_skill = tmp_path / "skills" / "warn-skill"
    write(warn_skill / "SKILL.md", "---\ndescription: \"Does something.\"\n---\nBody.\n")
    code, out = _run_cli(monkeypatch, capsys, ["--json", "--platform", "claude-code", str(warn_skill)])
    assert code == 0
    data = json.loads(out)
    assert data["errors"] == 0
    assert data["warnings"] > 0

    strict_code, strict_out = _run_cli(
        monkeypatch, capsys, ["--json", "--strict", "--platform", "claude-code", str(warn_skill)]
    )
    assert strict_code == 1
    strict_data = json.loads(strict_out)
    assert strict_data == data


def test_cli_json_project_and_cards(tmp_path, monkeypatch, capsys):
    proj = tmp_path / "proj"
    write(proj / ".claude" / "skills" / "ok-skill" / "SKILL.md",
          GOOD_SKILL.replace("writing-tests", "ok-skill").replace("references/conventions.md", "x.md"))
    write(proj / ".claude" / "skills" / "ok-skill" / "x.md", "x")
    write(proj / ".claude" / "skills" / "bad-skill" / "SKILL.md",
          "---\nname: Bad\ndescription: \"Does stuff.\"\n---\nBody.\n")

    code, out = _run_cli(monkeypatch, capsys, ["--json", "--project", str(proj)])
    assert code == 1
    proj_data = json.loads(out)
    assert proj_data["files_checked"] == 2
    assert proj_data["errors"] >= 1
    assert any(f["code"] == "S004" for f in proj_data["findings"])

    cards = tmp_path / "cards"
    write(cards / "broken-card.md", "# Platform card: Test\nNo metadata here.\n")
    c_code, c_out = _run_cli(monkeypatch, capsys, ["--json", "--cards", str(cards)])
    assert c_code == 0
    cards_data = json.loads(c_out)
    assert cards_data["files_checked"] == 1
    assert cards_data["warnings"] == 1
    assert any(f["code"] == "C001" for f in cards_data["findings"])


def test_cli_json_deterministic_sorting(tmp_path, monkeypatch, capsys):
    d1 = tmp_path / "skills" / "z-skill"
    write(d1 / "SKILL.md", "---\nname: z-skill\ndescription: \"Does stuff.\"\n---\nBody.\n")
    d2 = tmp_path / "skills" / "a-skill"
    write(d2 / "SKILL.md", "---\nname: Wrong\ndescription: \"Does stuff.\"\n---\nBody.\n")

    code, out = _run_cli(monkeypatch, capsys, ["--json", "--platform", "claude-code", str(d1), str(d2)])
    assert code == 1
    data = json.loads(out)
    keys = [(f["path"], lint.LEVELS.index(f["level"]), f["code"]) for f in data["findings"]]
    assert keys == sorted(keys)
    assert len(keys) >= 2


def test_cli_default_human_readable_output(good_skill, monkeypatch, capsys):
    code, out = _run_cli(monkeypatch, capsys, ["--platform", "claude-code", str(good_skill)])
    assert code == 0
    assert "0 error(s), 0 warning(s), 0 info - 1 file(s) checked" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_codex_agent_valid_toml_is_clean(tmp_path):
    f = write(
        tmp_path / ".codex" / "agents" / "artifact-reviewer.toml",
        'name = "artifact-reviewer"\n'
        'description = "Reviews artifacts."\n'
        'sandbox_mode = "read-only"\n'
        'model_reasoning_effort = "high"\n'
        'nickname_candidates = ["Reviewer"]\n'
        'developer_instructions = "Review carefully and stay read-only."\n',
    )
    report = run_path(f, "codex")
    assert report.findings == []
    for effort in ("none", "max"):
        f_eff = write(
            tmp_path / ".codex" / "agents" / f"eff-{effort}.toml",
            f'name = "eff-{effort}"\ndescription = "Test."\nmodel_reasoning_effort = "{effort}"\ndeveloper_instructions = "Test."\n',
        )
        assert run_path(f_eff, "codex").findings == []


def test_codex_agent_invalid_toml_and_fields(tmp_path):
    bad_toml = write(tmp_path / "agents" / "broken.toml", 'name = "broken\n')
    assert "A050" in codes(run_path(bad_toml, "codex"), "error")

    missing = write(tmp_path / "agents" / "missing.toml", 'model = ""\nunknown_key = 1\n')
    rep = run_path(missing, "codex")
    assert {"A051", "A052", "A053", "A056"} <= codes(rep, "error")
    assert "A056" in codes(rep, "warning")

    bad_enums = write(
        tmp_path / "agents" / "bad-enums.toml",
        'name = "Bad Name"\n'
        'description = "Test."\n'
        'sandbox_mode = "yolo"\n'
        'model_reasoning_effort = "ultra"\n'
        'developer_instructions = "Use the Agent tool."\n',
    )
    rep2 = run_path(bad_enums, "codex")
    assert {"A054", "A055"} <= codes(rep2, "error")
    assert {"A051", "S024"} <= codes(rep2, "warning")

    danger = write(
        tmp_path / "agents" / "danger.toml",
        'name = "danger"\n'
        'description = "Test."\n'
        'sandbox_mode = "danger-full-access"\n'
        'developer_instructions = "' + ("line\\n" * 305) + '"\n',
    )
    rep3 = run_path(danger, "codex")
    assert {"A054", "A003"} <= codes(rep3, "warning")


def test_codex_project_detection_and_lint(tmp_path):
    write(tmp_path / "AGENTS.override.md", "---\nfoo: bar\n---\n# Override\n")
    write(
        tmp_path / ".codex" / "agents" / "rev.toml",
        'name = "rev"\ndescription = "Reviews."\nsandbox_mode = "read-only"\ndeveloper_instructions = "Review."\n',
    )
    d = tmp_path / ".agents" / "skills" / "my-skill"
    write(d / "SKILL.md", GOOD_SKILL.replace("writing-tests", "my-skill").replace("references/conventions.md", "x.md"))
    write(d / "x.md", "x")

    assert "codex" in lint.detect_platforms(tmp_path)
    report = lint.Report()
    lint.lint_project(report, tmp_path, ["codex"])
    assert "I003" in codes(report, "warning")
    assert not codes(report, "error")
