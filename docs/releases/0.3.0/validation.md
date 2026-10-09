---
title: "BiucingCLI 0.3.0 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-030-release-prep"></a>
# BiucingCLI 0.3.0 发布准备

[English](validation.en.md)

这是准备 `0.3.0` 的具体执行清单，比[通用发布清单](../../guides/releasing.md)更窄：

- 本文针对单一版本；
- 根据当时仓库状态与已知 `0.3.0` 范围制定；
- `0.3.0` 交付后可作为历史证据，或由下一版本准备记录接替。

配合以下文档：

- [生成器产品化计划](../../initiatives/feature/generator-productization/plan.md)
- [发布清单](../../guides/releasing.md)
- [验证矩阵](../../guides/verification-matrix.md)

<a id="1-confirm-the-030-story"></a>
## 1. 确认 0.3.0 版本叙事

修改版本前确认声明与代码一致：

- 模板元数据已扩展，通过 CLI 暴露；
- 已交付 `biucing list --json` 和 `biucing info --json`；
- create 支持 `--set key=value`、`--non-interactive`；
- 有元数据和占位符一致性的仓库验证；
- list/info golden 纳入自动测试；
- 仓库已有发布与验证文档。

任一声明与检出代码不符时，先修产品或收缩声明，再提升版本。

<a id="2-version-touchpoints-for-030"></a>
## 2. 0.3.0 版本修改位置

一次同步更新：

| 文件 | 0.3.0 操作 |
| --- | --- |
| `README.md` | 目标从 `0.2.0` 改为 `0.3.0`，功能摘要同步 |
| `CHANGELOG.md` | 在 `0.2.0` 上方添加 `0.3.0 - YYYY-MM-DD` |
| `pyproject.toml` | 设置 `[project].version = "0.3.0"` |
| `src/biucingcli/__init__.py` | 设置 `__version__ = "0.3.0"` |
| `tests/test_cli.py` | 更新预期 `biucing 0.3.0` |
| `docs/initiatives/feature/generator-productization/plan.md` | 复核计划项是否应标记完成或收紧 |

<a id="3-recommended-030-command-sequence"></a>
## 3. 建议命令顺序

版本位置更新后依次执行：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info web-service
PYTHONPATH=src python3 -m biucingcli.cli info web-service --json
```

再做至少一次脚本化冒烟：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create web-service demo-service --output-dir /tmp/biucing-0.3.0-check --non-interactive --set project_name=demo-service --set module_name=github.com/example/demo-service
```

若修改共享 create、元数据传递或占位符解析，再做一个原生模板冒烟：

```bash
PYTHONPATH=src python3 -m biucingcli.cli create apple demo-apple --output-dir /tmp/biucing-0.3.0-check --non-interactive --set project_name=demo-apple --set bundle_identifier=com.example.demoapple
```

<a id="4-minimum-030-fresh-proof"></a>
## 4. 最低新验证要求

`0.3.0` 重点是生成器产品化，不是新增模板家族，最低实际要求：

- 全仓库自动检查通过；
- 新脚本化路径重新生成一个 Docker 模板；
- 同样重新生成一个原生模板；
- validate 保持通过；
- list/info 在 golden 下稳定。

建议组合：

- Docker：`web-service`
- 原生：`apple`

若 Android 或 microservice 流程有实质变化，用受影响模板替换，不机械沿用默认组合。

<a id="5-draft-changelog-shape-for-030"></a>
## 5. 变更记录草稿结构

保持面向用户，强调：

- 更丰富元数据和清晰成熟度/验证信号；
- 可脚本化的机器可读 list/info；
- `--set` 与非交互失败行为改善 create；
- 更强仓库验证及输出 golden 保护；
- 更完整发布/验证文档。

内部重构只有改变用户 CLI 或发布门槛时才需详写。

<a id="6-standardized-evidence-note-for-030"></a>
## 6. 标准证据说明

发布准备说明使用：

```md
## BiucingCLI 0.3.0 Release Evidence

- Target version: `0.3.0`
- Verification date: `YYYY-MM-DD`
- Repo-level checks:
  - `python3 -m unittest discover -s tests`
  - `PYTHONPATH=src python3 -m biucingcli.cli validate`
  - `PYTHONPATH=src python3 -m biucingcli.cli list`
  - `PYTHONPATH=src python3 -m biucingcli.cli list --json`
  - `PYTHONPATH=src python3 -m biucingcli.cli info web-service`
  - `PYTHONPATH=src python3 -m biucingcli.cli info web-service --json`
- Fresh template proof:
  - `web-service`: `create --non-interactive --set ...` completed
  - `apple`: `create --non-interactive --set ...` completed
- Version surfaces updated:
  - `README.md`
  - `CHANGELOG.md`
  - `pyproject.toml`
  - `src/biucingcli/__init__.py`
  - `tests/test_cli.py`
- Release notes focus:
  - metadata
  - JSON inspection
  - scriptable create flow
  - repo validation
  - release discipline
- Known limitations:
  - `none` or explicit note
```

<a id="7-final-release-command-block"></a>
## 7. 最终发布命令

验证仓库并定稿 CHANGELOG 后：

```bash
git status --short
git add README.md CHANGELOG.md pyproject.toml src/biucingcli/__init__.py tests/test_cli.py docs/initiatives/feature/generator-productization/plan.md docs/guides/releasing.md docs/guides/verification-matrix.md docs/releases/0.3.0/validation.md
git commit -m "Prepare release 0.3.0"
git tag -a v0.3.0 -m "Release 0.3.0"
git push origin main --follow-tags
gh release create v0.3.0 --title "BiucingCLI 0.3.0" --notes-file CHANGELOG.md
```

工作区含无关实验时缩小 `git add` 范围。
