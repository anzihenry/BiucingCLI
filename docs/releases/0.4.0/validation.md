---
title: "BiucingCLI 0.4.0 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-040-release-prep"></a>
# BiucingCLI 0.4.0 发布准备

[English](validation.en.md)

这是准备 `0.4.0` 的具体清单，比[通用发布清单](../../guides/releasing.md)更窄：

- 针对单一版本；
- 根据当时仓库与已知 `0.4.0` 范围制定；
- 交付后可作为历史证据或由下一版本准备文件接替。

配合以下文档：

- [模板组合设计](../../initiatives/feature/template-portfolio/design.md)
- [发布清单](../../guides/releasing.md)
- [验证矩阵](../../guides/verification-matrix.md)

<a id="1-confirm-the-040-story"></a>
## 1. 确认版本叙事

修改版本前确认代码支持这些声明：

- create 支持 `--dry-run`、`--plan`、JSON 预览/清单；
- 非交互失败一次报告全部缺失必填值；
- 元数据暴露验证等级、环境假设和工作流标签；
- 仓库验证检查更强模板契约及家族必需目录项；
- Worker 作为第六个 starter 交付；
- Worker 生成项目有真实 `go test ./...` 验证。

声明与代码不符时先修产品或删减声明，再提升版本。

<a id="2-version-touchpoints-for-040"></a>
## 2. 版本修改位置

同步更新：

| 文件 | 0.4.0 操作 |
| --- | --- |
| `README.md` | 目标从 `0.3.0` 改为 `0.4.0`，功能摘要同步 |
| `CHANGELOG.md` | 将 Unreleased 草稿改为带日期的 `0.4.0 - YYYY-MM-DD` |
| `pyproject.toml` | `[project].version = "0.4.0"` |
| `src/biucingcli/__init__.py` | `__version__ = "0.4.0"` |
| `tests/test_cli.py` | 预期改为 `biucing 0.4.0` |
| `docs/initiatives/feature/template-portfolio/design.md` | 复核阶段状态及声明是否需收紧 |

<a id="3-recommended-040-command-sequence"></a>
## 3. 建议命令顺序

更新版本后依次执行：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info web-service
PYTHONPATH=src python3 -m biucingcli.cli info web-service --json
PYTHONPATH=src python3 -m biucingcli.cli info worker
PYTHONPATH=src python3 -m biucingcli.cli info worker --json
```

最低生成器 UX 冒烟：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create frontend preview-app --output-dir /tmp/biucing-0.4.0-check --dry-run
PYTHONPATH=src python3 -m biucingcli.cli create web-service plan-service --output-dir /tmp/biucing-0.4.0-check --module-name github.com/example/plan-service --plan --json
```

每个改动 starter 家族至少一次真实脚本化创建：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create web-service demo-service --output-dir /tmp/biucing-0.4.0-check --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service
PYTHONPATH=src python3 -m biucingcli.cli create worker demo-worker --output-dir /tmp/biucing-0.4.0-check --non-interactive --set project_name=demo-worker --set module_name=github.com/example/demo-worker
```

<a id="4-minimum-040-fresh-proof"></a>
## 4. 最低新验证要求

本版本同时改变生成器和 starter 组合，因此要求：

- 仓库自动检查全部通过；
- 至少一个 Docker starter 走新预览/创建路径重新生成；
- 新 Worker 重新生成，并在生成目录测试；
- 更强契约下 validate 通过；
- info/JSON 查询仍反映预期产品能力。

建议组合：

- 既有 Docker starter：`web-service`
- 新 starter：`worker`

若最终版本再改原生输出，增加原生冒烟，不假定旧证据足够。

<a id="5-draft-changelog-shape-for-040"></a>
## 5. 变更记录草稿结构

面向用户，强调：

- `--dry-run`、`--plan`、JSON 清单带来的生成器 UX 改善；
- 更强元数据和仓库契约验证；
- 用于后台任务的新 Worker；
- 扩展能力对应的发布/验证文档。

内部细节只有影响用户 CLI 或发布门槛时才需详写。

<a id="6-standardized-evidence-note-for-040"></a>
## 6. 标准证据说明

准备说明正文使用：

```md
## BiucingCLI 0.4.0 Release Evidence

- Target version: `0.4.0`
- Verification date: `YYYY-MM-DD`
- Repo-level checks:
  - `python3 -m unittest discover -s tests`
  - `PYTHONPATH=src python3 -m biucingcli.cli validate`
  - `PYTHONPATH=src python3 -m biucingcli.cli list`
  - `PYTHONPATH=src python3 -m biucingcli.cli list --json`
  - `PYTHONPATH=src python3 -m biucingcli.cli info web-service`
  - `PYTHONPATH=src python3 -m biucingcli.cli info web-service --json`
  - `PYTHONPATH=src python3 -m biucingcli.cli info worker`
  - `PYTHONPATH=src python3 -m biucingcli.cli info worker --json`
- Generator UX smoke:
  - `create frontend ... --dry-run`
  - `create web-service ... --plan --json`
- Fresh template proof:
  - `web-service`: `create --non-interactive --set ...` completed
  - `worker`: `create --non-interactive --set ...` completed
  - generated `worker` project: `go test ./...` completed
- Version surfaces updated:
  - `README.md`
  - `CHANGELOG.md`
  - `pyproject.toml`
  - `src/biucingcli/__init__.py`
  - `tests/test_cli.py`
- Release notes focus:
  - generator UX
  - stronger template contract
  - new worker starter
  - release discipline
- Known limitations:
  - `none` or explicit note
```

<a id="7-final-release-command-block"></a>
## 7. 最终发布命令

仓库验证并定稿变更记录后：

```bash
git status --short
git add README.md CHANGELOG.md pyproject.toml src/biucingcli/__init__.py tests/test_cli.py docs/initiatives/feature/template-portfolio/design.md docs/guides/releasing.md docs/guides/verification-matrix.md docs/releases/0.4.0/validation.md
git commit -m "Prepare release 0.4.0"
git tag -a v0.4.0 -m "Release 0.4.0"
git push origin main --follow-tags
gh release create v0.4.0 --title "BiucingCLI 0.4.0" --notes-file CHANGELOG.md
```

有无关本地实验时缩小 `git add` 范围。
