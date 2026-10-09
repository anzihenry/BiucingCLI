---
title: "BiucingCLI 0.7.0 发布准备"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-070-release-prep"></a>
# BiucingCLI 0.7.0 发布准备

[English](validation.en.md)

目标版本：`0.7.0`

验证日期：`2026-08-01`

<a id="scope"></a>
## 范围

完成原生分发前能力，增加 Apple/Android 交付自动化、Android 签名和 Bundle 检查、HarmonyOS 本地签名与发布打包，并记录三平台新的真实构建证据。

<a id="repo-level-evidence"></a>
## 仓库证据

准备期间通过：

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m biucingcli.cli validate
PYTHONPATH=src python3 -m biucingcli.cli list --json
PYTHONPATH=src python3 -m biucingcli.cli info harmonyos
```

<a id="native-evidence"></a>
## 原生证据

| 模板 | 等级 | 命令和结果 |
| --- | --- | --- |
| `apple` | real-build | 新 iOS/macOS 项目完成生成、lint、构建、单元测试；iOS 安装、启动并在模拟器目视检查 |
| `android` | real-build | 新项目通过 make doctor/lint/test/build/bundle-release/artifact-info；Biucing_API_35 上 make test-ui：1 项测试，0 失败，0 跳过 |
| `harmonyos` | real-build | 新项目通过 make bootstrap/verify，含 doctor、lint、Hypium、未签名 HAP、产物指纹 |

<a id="release-delivery-boundaries"></a>
## 发布交付边界

- Apple archive/TestFlight/Connect 需 `APP_STORE_CONNECT_API_KEY_PATH`、`MATCH_GIT_URL`、开发团队和已配置 Connect 应用。
- Android Google Play 需 `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`、发布签名与已配置 Play 应用。
- HarmonyOS 有本地签名材料时验证签名并生成已签 HAP，AppGallery/企业上传仍属产品交接。

这些依赖账户的交付步骤都没有在本记录中标为完成。

<a id="release-operation"></a>
## 发布操作

```bash
git commit -m "chore: release 0.7.0"
git tag -a v0.7.0 -m "Release 0.7.0"
git push origin main --follow-tags
gh release create v0.7.0 --title "BiucingCLI 0.7.0" --notes-file docs/releases/0.7.0/notes.md
```
