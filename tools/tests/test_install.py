"""Tests for tools/install.py. Everything runs inside tmp_path: ROOT, the project and the home folder are faked."""

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

INSTALL_PATH = Path(__file__).resolve().parents[1] / "install.py"
spec = importlib.util.spec_from_file_location("stablehand_install", INSTALL_PATH)
install = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = install
spec.loader.exec_module(install)


def write(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_link(src: Path, dst: Path) -> None:
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(src), str(dst))
    else:
        dst.symlink_to(src, target_is_directory=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = (tmp_path / "repo").resolve()
    for platform in ("opencode", "antigravity"):
        for skill in ("alpha", "beta"):
            write(root / "platforms" / platform / "skills" / skill / "SKILL.md")
    write(root / "platforms" / "opencode" / "agents" / "rev.md")
    write(root / "platforms" / "antigravity" / "plugin.json", "{}")
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(install, "ROOT", root)
    monkeypatch.setattr(install, "PLATFORMS_DIR", root / "platforms")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    return root


@pytest.fixture
def project(tmp_path):
    p = (tmp_path / "proj").resolve()
    p.mkdir()
    return p


def manifest_paths(target_root: Path) -> set[str]:
    data = json.loads((target_root / install.MANIFEST).read_text(encoding="utf-8"))
    return {Path(e["path"]).relative_to(target_root).as_posix() for e in data["created"]}


@pytest.mark.parametrize("copy", [False, True])
def test_opencode_install_reinstall_uninstall(repo, project, copy):
    args = ["opencode", "--scope", "project", "--project", str(project)] + (["--copy"] if copy else [])
    target = project / ".opencode"
    assert install.main(args) == 0
    assert (target / "skills" / "alpha" / "SKILL.md").is_file()
    assert (target / "agents" / "rev.md").is_file()
    assert install.is_link(target / "skills" / "alpha") is not copy

    shutil.rmtree(repo / "platforms" / "opencode" / "skills" / "beta")
    assert install.main(args) == 0  # reinstall needs no --force and drops what is no longer shipped
    assert not os.path.lexists(target / "skills" / "beta")
    assert manifest_paths(target) == {"skills/alpha", "agents/rev.md"}

    assert install.main(args + ["--uninstall"]) == 0
    assert not target.exists()  # entries and the folders the install created are gone
    assert project.is_dir()
    assert (repo / "platforms" / "opencode" / "skills" / "alpha" / "SKILL.md").is_file()


@pytest.mark.parametrize("copy", [False, True])
def test_antigravity_install_reinstall_uninstall(repo, project, copy):
    args = ["antigravity", "--scope", "project", "--project", str(project)] + (["--copy"] if copy else [])
    assert install.main(args) == 0
    assert (project / ".agents" / "plugins" / "stablehand" / "plugin.json").is_file()
    assert install.main(args) == 0
    assert install.main(args + ["--uninstall"]) == 0
    assert not (project / ".agents").exists()
    assert (repo / "platforms" / "antigravity" / "plugin.json").is_file()


def test_unknown_real_directory_needs_force(repo, project):
    mine = write(project / ".opencode" / "skills" / "alpha" / "mine.txt", "keep")
    args = ["opencode", "--scope", "project", "--project", str(project)]
    assert install.main(args) == 1
    assert mine.read_text(encoding="utf-8") == "keep"
    assert "skills/alpha" not in manifest_paths(project / ".opencode")

    assert install.main(args + ["--uninstall"]) == 0
    assert mine.is_file()  # never recorded, so never removed

    assert install.main(args + ["--force"]) == 0
    assert not mine.exists()
    assert install.is_link(project / ".opencode" / "skills" / "alpha")


def test_workspace_refuses_real_folder_and_honours_copy(repo):
    mine = write(repo / ".opencode" / "skills" / "mine" / "SKILL.md", "keep")
    assert install.main(["opencode", "--scope", "workspace"]) == 1
    assert mine.read_text(encoding="utf-8") == "keep"

    shutil.rmtree(repo / ".opencode")
    assert install.main(["opencode", "--scope", "workspace", "--copy"]) == 0
    skills = repo / ".opencode" / "skills"
    assert skills.is_dir() and not install.is_link(skills)
    assert install.main(["opencode", "--scope", "workspace", "--uninstall"]) == 0
    assert not (repo / ".opencode").exists()


def test_is_ours_rule(repo, tmp_path):
    inside, outside = tmp_path / "link-in", tmp_path / "link-out"
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    make_link(repo / "platforms" / "opencode" / "skills", inside)
    make_link(elsewhere, outside)
    real = tmp_path / "real"
    real.mkdir()
    assert install.is_ours(inside, {})
    assert not install.is_ours(outside, {})
    assert install.is_ours(outside, {str(outside): "link"})
    assert not install.is_ours(real, {})
    assert install.is_ours(real, {str(real): "copy"})
    assert not install.is_ours(real, {str(real): "link"})  # a recorded link replaced by a real folder
    assert not install.is_ours(repo / "platforms", {})  # under ROOT but not a link
