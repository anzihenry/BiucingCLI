from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner  # type: ignore[import]

from biucingcli.cli import app

runner = CliRunner()


def test_domains_lists_all() -> None:
    result = runner.invoke(app, ["domains"])
    assert result.exit_code == 0
    for domain in ("frontend", "mobile", "backend", "devops", "testing", "desktop"):
        assert domain in result.stdout


def test_frontend_list() -> None:
    result = runner.invoke(app, ["frontend", "list"])
    assert result.exit_code == 0
    assert "Stacks" in result.stdout


def test_backend_list() -> None:
    result = runner.invoke(app, ["backend", "list"])
    assert result.exit_code == 0
    assert "Stacks" in result.stdout
    # Check for Go-related stacks
    assert "gin" in result.stdout.lower()
    assert "echo" in result.stdout.lower()


def test_mobile_list() -> None:
    result = runner.invoke(app, ["mobile", "list"])
    assert result.exit_code == 0
    assert "Stacks" in result.stdout
    # Check for Swift and Kotlin stacks
    assert "swift" in result.stdout.lower()
    assert "kotlin" in result.stdout.lower()


def test_devops_list() -> None:
    result = runner.invoke(app, ["devops", "list"])
    assert result.exit_code == 0
    assert "Stacks" in result.stdout
    # Check for Python DevOps stack
    assert "python-devops" in result.stdout.lower()


def test_desktop_list() -> None:
    result = runner.invoke(app, ["desktop", "list"])
    assert result.exit_code == 0
    assert "Stacks" in result.stdout
    # Check for C++ cross-platform stack
    assert "cpp-cross-platform" in result.stdout.lower()


def test_export_config(tmp_path: Path) -> None:
    target = tmp_path / "config.yaml"
    result = runner.invoke(app, ["configure", "export", str(target)])
    assert result.exit_code == 0
    assert target.exists()
    assert "Exported configuration" in result.stdout
