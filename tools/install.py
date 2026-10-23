# /// script
# requires-python = ">=3.12"
# ///
"""Install stablehand into a platform.

  uv run tools/install.py <platform> --scope workspace   # wire THIS checkout: open the stablehand
                                                         # repo in the platform and the skills load
  uv run tools/install.py claude-code                    # user/project: prints the plugin commands
  uv run tools/install.py antigravity [--scope user|project --project DIR]
  uv run tools/install.py opencode    [--scope user|project --project DIR]
Platform "all" wires every implementation that exists (workspace scope only).
Options:
  --copy        copy files instead of linking (links follow `git pull` automatically)
  --uninstall   remove what a previous install created
  --dry-run     print the actions without changing anything
  --force       replace existing paths that stablehand did not create

Links are directory junctions on Windows (no admin rights needed) and symlinks elsewhere.
Agent files are always copied, because file symlinks need extra privileges on Windows.
Every install writes .stablehand-install.json in the target root so --uninstall knows
exactly what to remove.
"""

from __future__ import annotations

import argparse
import contextlib
import itertools
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS_DIR = ROOT / "platforms"
MANIFEST = ".stablehand-install.json"


def is_link(path: Path) -> bool:
    return os.path.islink(path) or os.path.isjunction(path)


def is_ours(dst: Path, known: dict[str, str]) -> bool:
    """A link into this checkout or one we recorded, or a copy we recorded that is still a real path."""
    if is_link(dst):
        try:
            return str(dst) in known or Path(os.path.realpath(dst)).is_relative_to(ROOT)
        except OSError:
            return False
    return known.get(str(dst)) == "copy"


class Installer:
    def __init__(self, target_root: Path, dry_run: bool, force: bool, copy: bool):
        self.target_root, self.dry_run, self.force, self.copy = target_root, dry_run, force, copy
        self.previous = read_manifest(target_root)
        self.known = {e["path"]: e["kind"] for e in self.previous["created"]}
        self.dirs: list[str] = list(self.previous["dirs"])
        self.created: list[dict] = []
        self.skipped: list[str] = []

    def say(self, message: str) -> None:
        print(("[dry-run] " if self.dry_run else "") + message)

    def make_dirs(self, path: Path) -> None:
        """Create path and remember which folders were new, so --uninstall can remove them if empty."""
        missing = list(itertools.takewhile(lambda p: not p.exists(), [path, *path.parents]))
        path.mkdir(parents=True, exist_ok=True)
        self.dirs += [str(p) for p in missing if str(p) not in self.dirs]

    def clear(self, dst: Path) -> bool:
        if not os.path.lexists(dst):
            return True
        if not (self.force or is_ours(dst, self.known)):
            print(f"skip {dst}: exists and was not created by stablehand (use --force to replace)")
            self.skipped.append(str(dst))
            return False
        self.say(f"replace {dst}")
        if not self.dry_run:
            remove(dst)
        return True

    def place_dir(self, src: Path, dst: Path) -> None:
        if not self.clear(dst):
            return
        kind = "copy" if self.copy else "link"
        self.say(f"{kind} {dst} -> {src}")
        if not self.dry_run:
            self.make_dirs(dst.parent)
            if self.copy:
                shutil.copytree(src, dst)
            elif os.name == "nt":
                import _winapi
                _winapi.CreateJunction(str(src), str(dst))
            else:
                dst.symlink_to(src, target_is_directory=True)
        self.created.append({"path": str(dst), "kind": kind})

    def place_file(self, src: Path, dst: Path) -> None:
        if not self.clear(dst):
            return
        self.say(f"copy {dst}")
        if not self.dry_run:
            self.make_dirs(dst.parent)
            shutil.copy2(src, dst)
        self.created.append({"path": str(dst), "kind": "copy"})

    def finish(self, platform: str) -> int:
        """Remove what the previous install created but this one no longer does, then record this install."""
        current = {e["path"] for e in self.created} | set(self.skipped)
        for entry in self.previous["created"]:
            path = Path(entry["path"])
            if entry["path"] in current or not os.path.lexists(path):
                continue
            if is_ours(path, self.known):
                self.say(f"remove {path} (no longer installed)")
                if not self.dry_run:
                    remove(path)
            else:
                print(f"skip {path}: changed since stablehand created it; remove it by hand")
                self.skipped.append(str(path))
        if not self.dry_run:
            self.make_dirs(self.target_root)
            write_manifest(self.target_root, platform, self.created, self.dirs)
        return skipped_status(self.skipped)


def skipped_status(skipped: list[str]) -> int:
    if skipped:
        print(f"error: left {len(skipped)} path(s) untouched that stablehand did not create (listed above); "
              "use --force to replace them or remove them by hand", file=sys.stderr)
    return 1 if skipped else 0


def remove(path: Path) -> None:
    if is_link(path):
        os.unlink(path) if os.path.islink(path) else os.rmdir(path)
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def read_manifest(target_root: Path) -> dict:
    path = target_root / MANIFEST
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    return {"platform": data.get("platform"), "created": data.get("created", []), "dirs": data.get("dirs", [])}


def write_manifest(target_root: Path, platform: str, created: list[dict], dirs: list[str]) -> None:
    data = {"platform": platform, "source": str(ROOT), "created": created, "dirs": dirs}
    (target_root / MANIFEST).write_text(json.dumps(data, indent=2), encoding="utf-8")


def uninstall(target_root: Path, args: argparse.Namespace) -> int:
    if not (target_root / MANIFEST).is_file():
        print(f"nothing to uninstall: no {MANIFEST} in {target_root}")
        return 0
    data = read_manifest(target_root)
    known = {e["path"]: e["kind"] for e in data["created"]}
    kept = []
    for entry in data["created"]:
        path = Path(entry["path"])
        if not os.path.lexists(path):
            continue
        if args.force or is_ours(path, known):
            print(("[dry-run] " if args.dry_run else "") + f"remove {path}")
            if not args.dry_run:
                remove(path)
        else:
            print(f"skip {path}: changed since stablehand created it (use --force to remove it)")
            kept.append(entry)
    if not args.dry_run:
        if kept:
            write_manifest(target_root, data["platform"], kept, data["dirs"])
        else:
            (target_root / MANIFEST).unlink()
            for d in sorted(data["dirs"], key=lambda d: len(Path(d).parts), reverse=True):
                with contextlib.suppress(OSError):
                    Path(d).rmdir()  # only folders the install created, and only when empty
    return skipped_status([e["path"] for e in kept])


def opencode_link_hint(args: argparse.Namespace) -> None:
    if os.name == "nt" and not args.copy:
        print("hint: --copy avoids OpenCode's external_directory prompt for junction targets outside the project")


def require_port(platform: str, *parts: str) -> Path:
    src = PLATFORMS_DIR / platform
    if not all((src / p).exists() for p in parts):
        sys.exit(f"The {platform} implementation does not exist yet. Create it first: see platforms/{platform}/BOOTSTRAP.md")
    return src


def wire_workspace(platform: str, args: argparse.Namespace) -> int:
    """Link the platform implementation into this checkout's own platform folders."""
    links = {
        # Claude Code loads a folder with .claude-plugin/plugin.json under .claude/skills/ as <name>@skills-dir.
        "claude-code": [(PLATFORMS_DIR / "claude-code", ROOT / ".claude" / "skills" / "stablehand")],
        "antigravity": [(PLATFORMS_DIR / "antigravity", ROOT / ".agents" / "plugins" / "stablehand")],
        "opencode": [(PLATFORMS_DIR / "opencode" / "skills", ROOT / ".opencode" / "skills"),
                     (PLATFORMS_DIR / "opencode" / "agents", ROOT / ".opencode" / "agents")],
    }[platform]
    target_root = {"claude-code": ROOT / ".claude", "antigravity": ROOT / ".agents", "opencode": ROOT / ".opencode"}[platform]
    if args.uninstall:
        return uninstall(target_root, args)
    if not (PLATFORMS_DIR / platform / "skills").is_dir():
        print(f"skip {platform}: no implementation yet (see platforms/{platform}/BOOTSTRAP.md)")
        return 0
    installer = Installer(target_root, args.dry_run, args.force, args.copy)
    for src, dst in links:
        if src.is_dir():
            installer.place_dir(src, dst)
    status = installer.finish(platform)
    hint = {
        "claude-code": "Open this folder in Claude Code and accept the trust prompt; the skills appear as /stablehand:<skill>\n(already open? run /reload-plugins).",
        "antigravity": "Open this folder in Antigravity; the skills appear as /stablehand:<skill>. Check with: agy plugin validate .agents/plugins/stablehand (/skills does not list plugin skills).",
        "opencode": "Open this folder in OpenCode; check with: opencode agent list",
    }[platform]
    print(hint)
    if platform == "opencode":
        opencode_link_hint(args)
    return status


def install_claude(args: argparse.Namespace) -> int:
    plugin = PLATFORMS_DIR / "claude-code"
    print("Claude Code installs stablehand through its plugin system:\n")
    print("  From GitHub:")
    print("    claude plugin marketplace add Dudziak07/stablehand")
    print(f"    claude plugin install stablehand@stablehand --scope {args.scope}")
    print("\n  From this checkout:")
    print(f"    claude plugin marketplace add \"{ROOT}\"")
    print(f"    claude plugin install stablehand@stablehand --scope {args.scope}")
    print("\n  For development, without installing:")
    print(f"    claude --plugin-dir \"{plugin}\"")
    print("\nInside a session the same works as /plugin marketplace add ... and /plugin install ...")
    return 0


def install_antigravity(args: argparse.Namespace) -> int:
    src = require_port("antigravity", "plugin.json", "skills")
    target_root = (args.project / ".agents" / "plugins") if args.scope == "project" else Path.home() / ".gemini" / "config" / "plugins"
    if args.uninstall:
        return uninstall(target_root, args)
    installer = Installer(target_root, args.dry_run, args.force, args.copy)
    installer.place_dir(src, target_root / "stablehand")
    status = installer.finish("antigravity")
    print("\nReload in Antigravity (CLI: /skills reload), then check with: agy plugin validate <plugin folder>, or run /stablehand:designing-agent-setups. /skills does not list plugin skills.")
    return status


def install_opencode(args: argparse.Namespace) -> int:
    src = require_port("opencode", "skills")
    target_root = (args.project / ".opencode") if args.scope == "project" else Path.home() / ".config" / "opencode"
    if args.uninstall:
        return uninstall(target_root, args)
    installer = Installer(target_root, args.dry_run, args.force, args.copy)
    for skill in sorted(p for p in (src / "skills").iterdir() if p.is_dir()):
        installer.place_dir(skill, target_root / "skills" / skill.name)
        for other in (Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills"):
            if (other / skill.name).exists():
                print(f"warning: {other / skill.name} has the same name; OpenCode requires unique skill names")
    agents = src / "agents"
    if agents.is_dir():
        for agent in sorted(agents.glob("*.md")):
            installer.place_file(agent, target_root / "agents" / agent.name)
    status = installer.finish("opencode")
    print("\nRestart OpenCode, then check: opencode agent list")
    opencode_link_hint(args)
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install stablehand into a platform.")
    parser.add_argument("platform", choices=["claude-code", "antigravity", "opencode", "all"])
    parser.add_argument("--scope", choices=["workspace", "user", "project"], default="user")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--copy", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    args.project = args.project.resolve()
    if args.scope == "workspace":
        platforms = ["claude-code", "antigravity", "opencode"] if args.platform == "all" else [args.platform]
        return max(wire_workspace(p, args) for p in platforms)
    if args.platform == "all":
        parser.error("platform 'all' is only valid with --scope workspace")
    handler = {"claude-code": install_claude, "antigravity": install_antigravity, "opencode": install_opencode}
    return handler[args.platform](args)


if __name__ == "__main__":
    sys.exit(main())
