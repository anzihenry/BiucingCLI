---
title: "共同架构契约实现与验证记录"
status: active
owner: project-maintainers
updated: 2026-10-09
---

# 共同架构契约实现与验证记录

[English](cross-platform-validation.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

本轮承接 [D01–D04 决策](../../../engineering/native/cross-platform-decisions.md)。验证日期：2026-09-24。
源码为 `e0d8cd9` 之后的本次工作区修改；最终提交号由提交时补充，不使用父提交代表新实现。
本记录说明本地验证范围，不代表远端 CI、完整 V3 或真机 V4/V5 验收完成。

## 实现范围

- Apple：四壳以 StateObject 持有 SessionOwner/稳定模型；遮挡不清理，显式关闭可等待，所有者释放兜底关闭。
- Android：业务操作放入 ViewModel 的作用域；清除所有者停止模型并关闭 native；关闭可等待、错误可观察，取消等待者不会取消共享关闭完成信号。
- HarmonyOS：WindowStage 持有 SessionOwner，以局部 LocalStorage 注入模型；销毁才关闭，拒绝新任务并等待在途操作；按手机/电脑/手表/电视组织界面，共用业务状态。
- 三端补 DI 负面案例、架构验收清单与记录 JSON 示例。新生成项目的记录初始为 `not_run`，不会继承本仓库的通过状态。

## 环境与产物

宿主为 macOS 27.0（26A428）、arm64。临时生成工程和日志位于
`/tmp/biucing-session-contracts/`；这些日志不随模板交付，也不作为永久 CI 存档。

| 平台 | 工具链与消费版本 | 执行环境 |
| --- | --- | --- |
| Apple | Xcode 27.0；Swift 6.4；SafeDI 2.0.0；FoundationKit/SharedCore/HomeFeature 0.1.0，HomeFeature 由本轮源码重建 | macOS 本机；iPhone 18 Pro / iOS 27.0；Apple Watch Series 12 46mm / watchOS 27.0；Apple TV 4K 第三代 / tvOS 27.0，后三者为 arm64 模拟器 |
| Android | JDK 17、Gradle 8.10.2、NDK 28.2.13676358；sharedcore 0.1.1，其余组件 0.1.0；修改的状态/UI 组件由本轮源码重建 | 宿主 JVM/JNI；Biucing_API_35、Android 15 手机模拟器 |
| HarmonyOS | SDK 6.1.1.125、hvigor 6.24.4、ohpm 6.1.2.285、Node 18.20.1；contracts/sharedcore/homefeature 0.1.0 由本轮源码生成；宿主 native 测试使用 Node 24.19.0 | 宿主测试和真实 SDK 编译；hdc 无已连接目标 |

临时工程中改变组件版本只用于避免覆盖已发布的不可变产物，没有修改模板的初始版本策略。

## 本轮结果

| 检查 | 结果 | 日志（相对临时目录） |
| --- | --- | --- |
| Apple 四壳 Debug 测试 | 每壳 5 项，共 20 项通过；包括稳定模型、独立所有者、重复关闭、关闭后拒绝工作和所有者释放 | `apple-{macos,ios,watchos,tvos}.log` |
| Apple DI | 缺失、重复、环路及真实 Swift 构造签名漂移按预期失败 | `apple-di-final.log` |
| Android 三壳构建 | 手机、Wear、TV 的 Debug/Release 共六种构建通过 | `android-shell-final.log` |
| Android 状态单元测试 | 3 项通过，包含关闭后丢弃延迟结果 | `android-state-final.log`、`device-demo/core/homestate/build/test-results/` |
| Android 宿主 JNI | 显式启用本机 JNI 库后 5 项通过，包含取消关闭等待者和取消/释放竞争 | `android-jni-final.log`、`device-demo/core/sharedcore/build/test-results/` |
| Android 手机仪器测试 | 3 项通过；包括 Activity 重建、设置返回后结果保留、ViewModelStore 清除与独立会话关闭 | `android-device.log` |
| Android DI | 四层图各四类错误，共 16 个反例按预期失败 | `android-di.log` |
| HarmonyOS 宿主桥接/模型 | 生产 native bridge、源模型队列/取消/关闭/隔离，以及注入、稳定所有者、延迟结果和失败清理测试通过 | `harmony-native.log` |
| HarmonyOS DI | 缺失/重复/环路检查通过；真实 ArkTS 壳构造类型反例被拒绝，恢复后重建通过 | `harmony-di.log` |
| HarmonyOS 单元/设备包 | `make test` 成功，测试集含 4 个 Hypium 案例；3 个 ohosTest 案例编译成功，未在设备执行 | `harmony-tests.log` |
| HarmonyOS 无源码消费 | 移走 components/shared 并 clean，Debug/Release HAP 均构建通过，随后恢复目录；产物无签名 | `harmony-no-source-{debug,release}.log` |
| CLI 回归与分发 | 199 项核心、11 项平台回归通过；wheel/sdist 及七类模板分发验证通过 | `python-core-final.log`、`python-platform-final.log`、`distribution-final.log` |

Android 默认 Gradle 配置会排除 CoreSessionTest；不能用普通 `testReleaseUnitTest` 成功声称 JNI 测试通过。
本轮另行编译宿主库，并使用 `-PhostNativePath=<本机库目录>` 执行，XML 报告为 5 项、零跳过、零失败。
HarmonyOS 宿主源码测试为 @Observed 提供身份装饰器，不能证明 ArkUI 响应式行为；Hypium 成功也不能代替生产桥在设备上运行。

## 仍须按设备验收

L01/L03/L04、I01–I04 已有局部自动化证据，但单元测试不等同于真实系统窗口/导航事件测试。
三端仍须逐设备补齐 L02 后台、实际业务退出/窗口销毁、进程重启以及 M01 输入与无障碍场景。
当前没有持久化恢复，L05 中恢复持久化状态部分不适用；不承诺恢复 native 句柄或执行中的任务。

本轮未重跑 Android Wear/TV 仪器测试，历史运行结果见平台验证记录；六种构建通过不补足新交互证据。
Apple 本轮壳测试为 Debug，不代表四平台 Release 真机验收。
HarmonyOS 尚无 ArkTS VM/真实 native 桥的设备运行证据，表冠、遥控器、窗口和观察更新必须补测。
HarmonyOS 的类型漂移反例覆盖壳图；组件真实签名由发布编译检查，尚无每个组件的类型错误注入案例。
本轮没有正式签名、安装升级、发布、性能或功耗验收，也没有新增数据库、跨设备同步和后台持续执行能力。

各生成工程的 `docs/architecture-acceptance.md` 提供复现入口与功能矩阵，
`docs/verification-record.example.json` 用于按源码、产物、设备和构建类型继续填写结果。
