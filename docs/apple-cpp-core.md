# Apple 核心、静态组件与四平台验证

更新：2026-09-23。技术基线和职责见 [完整架构](apple-shell-component-architecture.md)。

模版一次生成 iOS、macOS、watchOS、tvOS 四个平台壳。Swift 6.4+ 工具链使用 Swift 6
语言模式；核心为 C++20。源码开发使用 SwiftPM/CMake，壳消费独立发布的静态 XCFramework。

| 发布单元 | 编译模块 | 依赖 |
| --- | --- | --- |
| FoundationKit | ProductContracts、DesignSystem | 无 |
| SharedCore | CoreNative、SharedCore | 无 |
| HomeFeature | HomeFeature | 精确版本的 FoundationKit |

壳通过平台适配器把 SharedCore 注入 HomeFeature。应用作用域共享工厂，窗口/页面作用域
拥有独立会话。C++ 实现不透明句柄、操作提交状态、协作取消、固定宽度错误与诊断；
Swift 包装负责后台串行调度、任务保活和异步关闭。

SafeDI 2.0.0 官方 CLI 使用固定下载摘要，分别生成组件内部与壳公开工厂的构造代码。
业务 SDK 不暴露 SafeDI 类型；描述输入与实际接口的一致性由生成代码的 Swift 编译验证。
壳侧只读取 Composition/DI，构建阶段不扫描组件内部源码。

## 本地验收

环境：Xcode 27.0（27A266a）、Apple Swift 6.4、Apple Clang 21、Tuist 4.209.0。
Tuist 的模版固定版本已与本次验证一致。所有应用构建使用 `CODE_SIGNING_ALLOWED=NO`。

全新生成工程执行：

```sh
make components-bootstrap generate
make verify XCODEBUILD='xcodebuild -derivedDataPath DerivedData/final CODE_SIGNING_ALLOWED=NO'
```

| 验证 | 结果 |
| --- | --- |
| 静态 SDK | 5 个模块全部打包为 XCFramework；覆盖 macOS、iOS 真机/模拟器、watchOS 真机/模拟器、tvOS 真机/模拟器 |
| C ABI / CMake Release | 1 项 C 客户端测试通过，覆盖值、溢出、输出不变、诊断、取消、独立会话状态 |
| Swift 核心 | 5 项测试通过，覆盖错误映射、预取消、重复关闭和并发提交/关闭 |
| 功能组件 | 1 项注入确定性服务的状态测试通过 |
| SafeDI | 正确图生成成功；缺失依赖和循环依赖按预期原因失败 |
| iOS Simulator | 构建通过，3 项壳测试通过 |
| macOS 实机 | 构建通过，3 项壳测试通过 |
| watchOS Simulator | 构建通过，3 项壳测试通过 |
| tvOS Simulator | 构建通过，3 项壳测试通过 |
| SwiftLint | 27 个 Swift 文件，0 violations |
| 独立版本升级 | HomeFeature 0.1.1 单独发布，继续消费 FoundationKit 0.1.0，壳验证通过 |
| 无源码消费 | 移走 Components/ 和 Shared/ 后，四壳再次全部构建成功 |
| Xcode 直接构建 | 人为引入 MissingFactory 后，SafeDI 构建阶段拒绝构建；恢复后四壳构建通过 |

每个平台的 3 项壳测试覆盖真实二进制调用及关闭、应用工厂创建独立会话、资源 bundle 交付。
没有把组件源码测试结果当作二进制消费方的验证结果。

SDK 清单记录每个切片的平台和架构、静态归档类型、源文件摘要、工具链、依赖、资源、
Swift interface/ABI 描述及符号说明。静态对象包含 DWARF，最终应用归档负责生成 dSYM。
同版本不可覆盖；产品锁包含完整依赖组合和清单摘要。

模版 Python 回归覆盖：锁定清单不可替换、产物篡改、缺失锁拒绝源码回退、资源与切片缺失、
独立版本升级、覆盖依赖一致性、CI/Release 禁止覆盖，以及 FAT 动态库不得伪装成静态归档。

本次验收日志位于开发机 `/tmp/biucing-architecture-final/`，是本地临时证据，不随模版发布。

## 尚未验证或不属于本次实现

- 真机 SDK 的切片编译已验证；iOS/watchOS/tvOS 真机运行尚未验证。
- 未使用真实开发者签名、执行 macOS 公证或上传商店。
- Windows/Linux CMake CI 已配置但没有本次远端运行结果。
- 四平台完整 CI 工作流已提供，需配置 `apple-swift64` macOS runner 后启用。
- Android 模版已提供 Kotlin/JNI 与二进制组件基线，见 [Android 验证](android-component-verification.md)；
  Apple 工程不会同时生成 Android 壳。HarmonyOS/Node-API、Windows/Linux UI 及适配器仍待实现。
- 外部产物托管和认证由团队配置；默认实现是本地不可变仓库及明确的目录/清单契约。
- 当前示例没有真实业务数据库、迁移或长任务进度回调；后续组件须继续落实相关契约。

这些自动化测试也不替代每个平台的完整交互、无障碍或性能验收。
