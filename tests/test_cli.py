from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner  # type: ignore[import]

from biucingcli.cli import app

runner = CliRunner()


def test_domains_lists_all() -> None:
    result = runner.invoke(app, ["domains"])
    assert result.exit_code == 0
    for domain in ("frontend", "devops", "testing"):
        assert domain in result.stdout


def test_frontend_list() -> None:
    result = runner.invoke(app, ["frontend", "list"])
    assert result.exit_code == 0
    assert "Stacks" in result.stdout


def test_export_config(tmp_path: Path) -> None:
    target = tmp_path / "config.yaml"
    result = runner.invoke(app, ["configure", "export", str(target)])
    assert result.exit_code == 0
    assert target.exists()
    assert "Exported configuration" in result.stdout
