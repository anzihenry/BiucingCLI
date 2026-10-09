---
title: "BiucingCLI 0.8.0 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-080-release-prep"></a>
# BiucingCLI 0.8.0 发布准备

[English](validation.en.md)

目标版本：`0.8.0`

验证日期：`2026-08-31`

<a id="scope"></a>
## 范围

跨模板加固：生成输入校验、公共 Make 契约、生产浏览器测试、后端生命周期、确定性 Worker 重试、原生凭证保护和签名/产物核验。

<a id="repo-level-evidence"></a>
## 仓库证据

通过检查：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info web-service
PYTHONPATH=src python3 -m biucingcli.cli info web-service --json
PYTHONPATH=src python3 -m biucingcli.cli info worker
PYTHONPATH=src python3 -m biucingcli.cli info worker --json
PYTHONPATH=src python3 -m biucingcli.cli info harmonyos
PYTHONPATH=src python3 -m biucingcli.cli --version
git diff --check
```

一个前端和一个 Web 项目的可读 dry-run、JSON plan、非交互生成、make help 冒烟也通过。

自动测试覆盖七 starter 渲染、公共 Make、无效输入拒绝、生成 Go 运行测试、前端生产浏览器配置、Apple 发布身份、Android 供应链/Bundle、HarmonyOS 锁/签名/产物。

<a id="template-evidence"></a>
## 模板证据

| 模板 | 本次验证 |
| --- | --- |
| `frontend` | 渲染测试验证 pnpm 锁、生产 Playwright、Nginx 工作流、doctor 和公共命令 |
| `web-service` | 生成 Go 测试覆盖超时/优雅关闭；验证 Docker healthcheck 和公共命令 |
| `microservice` | 生成 Go 测试通过 bufconn 测 HTTP/gRPC 关闭及真实 protobuf Ping；健康和命令契约通过 |
| `worker` | 生成 Go 测试覆盖确定性重试、耗尽、取消、调度继续；lint/build 连接通过 |
| `apple` | 自动 fixture 验证 Release workspace/xcarchive Bundle ID，拒绝调试后缀，确认签名/上传前通道顺序 |
| `android` | fixture 验证 Gradle 分发/依赖元数据、签名身份、AAB 完整性、签名证书 |
| `harmonyos` | fixture 验证精确 ohpm 锁、签名/profile/bundle 身份、原子签名注入恢复、无秘密泄露的失败 |

<a id="known-boundaries"></a>
## 已知边界

- 无 Apple/Play/AppGallery 凭证和应用记录不做真实上传。
- 本次原生签名/产物检查使用确定性 fixture；已有 0.7.0 工作站证据仍是最近的 SDK 真实构建记录。
- 生产浏览器/容器工作流由生成配置与回归测试覆盖，发布不要求启动长驻本地服务。

<a id="release-operation"></a>
## 发布操作

```bash
git commit -m "chore: release 0.8.0"
git tag -a v0.8.0 -m "Release 0.8.0"
git push origin main --follow-tags
gh release create v0.8.0 --title "BiucingCLI 0.8.0" --notes-file docs/releases/0.8.0/notes.md
```
