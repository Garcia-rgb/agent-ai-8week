"""CLI 的对外契约。

这里锁的是会被外部依赖的两件事：``doctor`` 的**退出码语义**（部署脚本与 CI 按它判定），
以及各子命令的参数默认值。用例都不连真实语料库，所以跑得很快。
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from support_agent import __version__
from support_agent.cli import (
    EXIT_ISSUES,
    EXIT_OK,
    FAIL,
    OK,
    WARN,
    _render,
    build_parser,
    main,
)
from support_agent.config import get_settings


def test_render_all_ok_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert _render([("configuration", OK, "app_env=development")]) == EXIT_OK
    assert "all checks passed" in capsys.readouterr().out


def test_render_warning_does_not_fail() -> None:
    """未配远程模型是受支持的默认模式（退回本地规则模型），不能因此让 CI 变红。"""
    assert _render([("model", WARN, "not configured")]) == EXIT_OK


def test_render_strict_promotes_warnings() -> None:
    assert _render([("model", WARN, "not configured")], strict=True) == EXIT_ISSUES


def test_render_failure_fails_even_without_strict() -> None:
    assert _render([("embedding", FAIL, "onnxruntime missing")]) == EXIT_ISSUES


def test_render_counts_failures_and_warnings_separately(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = _render([("model", WARN, "not configured"), ("embedding", FAIL, "boom")])
    assert code == EXIT_ISSUES
    assert "1 failure(s), 1 warning(s)" in capsys.readouterr().out


def test_doctor_returns_zero_on_a_fresh_checkout(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """空库 + 没配模型的仓库（新克隆、CI）应该退出 0，只有 FAIL 才算失败。"""
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path / 'fresh.db'}")
    monkeypatch.setenv("EMBEDDING_BACKEND", "hash")
    get_settings.cache_clear()
    assert main(["doctor"]) == EXIT_OK


def test_version_subcommand_prints_the_package_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["version"]) == EXIT_OK
    assert __version__ in capsys.readouterr().out


def test_no_subcommand_prints_help_without_failing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == EXIT_OK
    assert "usage" in capsys.readouterr().out.lower()


def test_serve_defaults_to_loopback() -> None:
    args = build_parser().parse_args(["serve"])
    assert (args.host, args.port, args.reload) == ("127.0.0.1", 8000, False)


def test_doctor_strict_flag_is_parsed() -> None:
    assert build_parser().parse_args(["doctor", "--strict"]).strict is True
    assert build_parser().parse_args(["doctor"]).strict is False


def test_version_flag_exits_without_running_a_subcommand() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0


def test_python_dash_m_entry_point_works() -> None:
    """`python -m support_agent version` 是 Makefile 与文档里用的入口，单独守一条。

    ``__main__.py`` 只有几行，但它一旦坏掉，README 与 Makefile 里所有 `python -m` 命令都会失效。
    """
    result = subprocess.run(
        [sys.executable, "-m", "support_agent", "version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert __version__ in result.stdout
