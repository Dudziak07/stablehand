# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Trigger and delegation tests through the real Claude Code loader.

Runs every prompt of a triggers.yaml with `claude -p` inside the target repo and checks
whether the named skill was loaded (or, with --agent, whether the named subagent was
delegated to). File-editing tools are disallowed, so the target is never modified.

usage:
  uv run run_triggers.py --repo <target> --triggers <triggers.yaml> --skill <name> [--out results.json]
  uv run run_triggers.py --repo <target> --agent <name> --should "prompt" [--should-not "prompt"] ...
options:
  --claude <path>   CLI to use (default: `claude` on PATH)
  --max-turns N     turns per prompt (default 3; the load happens in the first turns)
  --resume          skip prompts already recorded in --out (for interrupted batches)
Exit code: 0 when every prompt behaved as expected, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

TIMEOUT = 900


def matches(call: str, name: str) -> bool:
    """The exact skill/agent name, or <plugin>:name."""
    return call.split(":", 1)[-1] == name


def load_cases(args: argparse.Namespace) -> list[tuple[str, str]]:
    if args.triggers:
        data = yaml.safe_load(Path(args.triggers).read_text(encoding="utf-8-sig")) or {}
        return [("should", p) for p in data.get("should_trigger") or []] + \
               [("should_not", p) for p in data.get("should_not_trigger") or []]
    return [("should", p) for p in args.should] + [("should_not", p) for p in args.should_not]


def run_prompt(claude: str, repo: str, prompt: str, max_turns: int) -> dict:
    cmd = [claude, "-p", prompt, "--output-format", "stream-json", "--verbose", "--max-turns", str(max_turns),
           "--no-session-persistence", "--disallowed-tools", "Edit,Write,NotebookEdit,Bash,PowerShell"]
    skills_listed, skill_calls, agent_calls, error, hit_max_turns = [], [], [], None, False
    try:
        proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"skills_listed": [], "skill_calls": [], "agent_calls": [], "error": f"timed out after {TIMEOUT}s"}
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "system" and msg.get("subtype") == "init":
            skills_listed = [str(s) for s in msg.get("skills") or []]
        elif msg.get("type") == "assistant":
            for block in msg.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    inp = block.get("input", {})
                    if block.get("name") == "Skill":
                        skill_calls.append(str(inp.get("skill") or inp.get("name") or inp))
                    elif block.get("name") in ("Agent", "Task"):
                        agent_calls.append(str(inp.get("subagent_type")))
        elif msg.get("type") == "result" and msg.get("is_error"):
            # Hitting --max-turns is expected (the load decision happens in the first turns);
            # the CLI then exits 1, which is not a failure of the test.
            if msg.get("subtype") == "error_max_turns":
                hit_max_turns = True
            else:
                error = msg.get("result") or msg.get("subtype")
    if proc.returncode != 0 and not error and not hit_max_turns:
        error = proc.stderr.strip()[-300:] or f"exit code {proc.returncode}"
    return {"skills_listed": skills_listed, "skill_calls": skill_calls, "agent_calls": agent_calls, "error": error}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--repo", required=True)
    p.add_argument("--claude", default=(os.name == "nt" and shutil.which("claude.exe")) or shutil.which("claude"))
    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--skill")
    target.add_argument("--agent")
    p.add_argument("--triggers")
    p.add_argument("--should", action="append", default=[])
    p.add_argument("--should-not", action="append", default=[])
    p.add_argument("--max-turns", type=int, default=3)
    p.add_argument("--out", default="trigger-results.json")
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()
    if not args.claude:
        p.error("claude CLI not found on PATH; pass --claude <path> (IDE extensions bundle one)")
    if os.name == "nt" and Path(args.claude).suffix.lower() in (".cmd", ".bat"):
        print(f"warning: {args.claude} is a .cmd shim that can mangle prompts with quotes or newlines; "
              "pass --claude <path to claude.exe>", file=sys.stderr)

    name = args.skill or args.agent
    cases = load_cases(args)
    if not cases:
        print("no prompts to run: give --triggers with should_trigger/should_not_trigger, or --should/--should-not")
        return 1
    out = Path(args.out)
    done = {r["prompt"]: r for r in json.loads(out.read_text(encoding="utf-8"))} if args.resume and out.is_file() else {}
    results = list(done.values())
    for expect, prompt in cases:
        if prompt in done:
            continue
        run = run_prompt(args.claude, args.repo, prompt, args.max_turns)
        hit = any(matches(c, name) for c in (run["agent_calls"] if args.agent else run["skill_calls"]))
        ok = run["error"] is None and (hit if expect == "should" else not hit)
        results.append({"expect": expect, "prompt": prompt, "ok": ok, **run})
        out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")  # resumable after each prompt
        status = "ERROR" if run["error"] else ("PASS" if ok else "FAIL")
        print(f"{status:5} [{expect}] {prompt[:80]} | skills={run['skill_calls']} agents={run['agent_calls']}"
              + (f" | {run['error'][:120]}" if run["error"] else ""))
        if run["error"] and "limit" in str(run["error"]).lower():
            print("Usage limit reached: stopping. Re-run with --resume after it resets.")
            return 1
    passed = sum(r["ok"] for r in results)
    print(f"{passed}/{len(results)} as expected  (results: {out})")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
