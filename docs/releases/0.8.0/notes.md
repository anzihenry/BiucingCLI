---
title: "BiucingCLI 0.8.0"
status: recorded
owner: project-maintainers
updated: 2026-10-09
---

<a id="biucingcli-080"></a>
# BiucingCLI 0.8.0

[English](notes.en.md)

从创建、运行到发布打包加固所有 starter。

<a id="highlights"></a>
## 亮点

- 七模板写入前验证输入，提供相同 bootstrap、doctor、lint、test、verify、build、clean、help Make 命令。
- 前端提交 pnpm 锁，在真实浏览器工作流测试生产 Nginx 镜像。
- Web/Micro 强制有界超时、健康、优雅关闭；Micro 提供真实且测试过的 protobuf Ping gRPC 契约。
- Worker 重试耗尽、指数退避、取消和周期调度有确定性测试。
- Apple 防止 worktree Bundle ID 后缀进入签名 archive，签名前和 archive 后核验身份。
- Android/HarmonyOS 交付前验证依赖来源、签名身份和包产物。
- 三原生模板保护文档指定凭证/签名位置，HarmonyOS 临时签名注入已加固。

<a id="compatibility"></a>
## 兼容性

既有公开 make 工作流保留，新公共命令提供跨模板自动化入口。无效或不兼容创建选项在写目标前失败，不再接受或静默忽略。

<a id="distribution-boundary"></a>
## 分发边界

验证本地生成、运行契约、签名输入和发布产物。真实 Connect、Play、AppGallery 提交仍需产品账户、应用记录、凭证和审核配置，不宣称商店提交。

<a id="verification"></a>
## 验证

证据和环境边界见 [0.8.0 发布准备](validation.md)。
