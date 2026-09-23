# {{DISPLAY_NAME}}

四个平台壳：iOS、macOS、watchOS、tvOS。默认操作平台为 `{{APPLE_PLATFORM_NAME}}`；
`make build PLATFORM=ios` 可切换。`--platform` 只选择默认值，始终生成四个平台。

Swift 6.4+ 工具链、Swift 6 语言模式、SwiftUI、C++20、Tuist、SafeDI 2.0.0。
组件源码随模版提供以便开发，产品壳只消费预编译静态 XCFramework。

## 开始

```sh
make bootstrap                  # 安装工具；首次构建 SDK、生成精确锁、生成四平台工程
make doctor
make lint
make core-test core-swift-test component-test di-test
make build test                 # 默认平台
make build-all test-all         # 四个平台；需要对应模拟器
open {{PROJECT_NAME}}.xcworkspace
```

已有工具时首次执行 `make components-bootstrap generate`。
组件初次构建包含真机、模拟器以及声明支持的全部架构，耗时比单平台源码构建更长。
`make generate`、`make build` 不会自动改用组件源码；缺少锁定产物必须先同步产物仓库。
将生成的 `Dependencies/components.lock.json` 提交到版本库。

## 职责与依赖

```text
Apps/{ios,macos,watchos,tvos}/   入口、根导航、生命周期、应用配置
Composition/                   平台服务、公开工厂、SafeDI 壳组装
Dependencies/                  精确声明与锁文件
Components/                    组件开发 Swift Package（不由壳源码引用）
  Sources/ProductContracts/    服务协议与类型明确的功能输出
  Sources/DesignSystem/        视觉默认值与公开定制接口
  Sources/HomeFeature/         功能界面、状态、组件内部组装
  DI/                         SafeDI 生成输入
  Resources/                  功能默认资源
Shared/Core/                   独立 C++20 核心、C ABI、Apple 包装层
```

发布单元：`FoundationKit`（ProductContracts、DesignSystem）、`SharedCore`
（CoreNative、SharedCore）、`HomeFeature`。各自独立版本化，HomeFeature 精确依赖 FoundationKit。
HomeFeature 不包含 C++ 核心副本；壳统一链接 SharedCore。依赖图不能循环。

示例的计算规则、操作提交计数在 C++ 会话内；Swift 包装负责调度、取消和关闭，
HomeFeature 管理界面状态并发出 `HomeOutput`，跨功能导航由壳处理。
窗口/页面持有一组功能会话；离开时异步关闭，已接受任务持有资源直到安全结束。
未来应用级任务应提升到应用作用域，不要复用页面消失时取消的任务。

## 二进制交付与联调

```sh
# 发布整个初始组合；相同版本不能重复发布
make components-bootstrap

# 独立开发功能 SDK；依赖组件使用声明版本的二进制
./scripts/components build --component HomeFeature --version 0.1.1
# 在 Dependencies/components.json 中更新 HomeFeature 为 0.1.1 后：
./scripts/components lock
make generate

# 个人本地二进制联调（不改正式锁）
./scripts/components override set HomeFeature /absolute/path/HomeFeature/0.1.1
./scripts/components override info
make generate
./scripts/components override clear HomeFeature
```

产物仓库默认为被 Git 忽略的 `.artifacts/`，可设置 `COMPONENT_REGISTRY=/absolute/path`。
将完整的 `组件名/版本/` 目录同步到团队不可变存储即可共享；本模版不配置任何外部托管账户。
组件提取到独立仓库后，继续交付相同目录和清单契约，产品壳无需获得组件源码。
具体产物上传/下载服务由团队接入；注册表应作为受信任的发布来源。

清单包括工具链、源码修订和内容摘要、平台/架构、最低系统、接口版本、精确依赖、
逐文件 SHA-256、资源与符号说明。静态库保存对象 DWARF；最终应用归档生成 dSYM。
发布版本不可覆盖，修改必须新发版本；团队联调用不可变预发布版本。
本地覆盖被 Git 忽略，依赖组合仍需一致，CI 和 Release 构建明确拒绝本地覆盖。
Xcode 构建阶段也校验已解析文件与锁，避免直接点 Build 绕过校验。

## SafeDI 与二进制边界

使用固定版本、校验下载摘要的官方 SafeDITool。`DI/Graph.swift` 是独立的生成输入，
不作为业务源码编译、不随 SDK 暴露；生成的构造代码会编译到对应模块。
这属于 SafeDI CLI 集成，不要求在 SDK 公共接口上声明 SafeDI 宏或协议。
修改构造函数时同时更新 DI 输入；真实 Swift 编译检查描述与接口是否一致。

组件内部生成并编译自己的图。壳只描述公开工厂和平台实现，不能扫描组件隐藏源码。
`make di-test` 验证正确图、缺失依赖和循环依赖；壳构建验证公开工厂实际可调用。
保留显式初始化依赖、明确作用域和独立于 DI 销毁的 `close()`，不引入全局服务定位器。

## C++ 契约与跨平台扩展

查看 [Shared/Core/README.md](Shared/Core/README.md)。普通输入调用期间借用、结果复制；
有状态对象用不透明句柄，同句柄串行；取消令牌是明确允许并发的原子入口。
错误码为固定宽度整数，失败不提交结果；异常不会穿过 C ABI。
输入最多 1,000,000 个 Int64，溢出、取消时结果与成功计数保持不变。

Swift 包装在独立队列执行，接受工作与关闭按序排队；关闭停止接收、取消并等待安全结束。
示例为有界批量计算，无进度回调。增加长任务时必须明确回调执行环境、限频与过期通知策略。
Android/JNI、HarmonyOS/Node-API、Windows/Linux 适配器尚未生成；它们可以复用 CMake 核心，
但必须为对应平台重新编译。业务持久化、数据库和数据迁移由具体产品确定。

## 验证与交付

- `core-test`：C 客户端验证 ABI、溢出、失败不修改结果、取消及状态提交。
- `core-swift-test`：Swift 错误、关闭、取消、并发提交与关闭。
- `component-test`：注入可预测服务的功能测试；SwiftUI Preview 使用固定数据。
- `di-test`：SafeDI 正确图和两个失败案例。
- `test-all`：四壳验证真实二进制调用、关闭和资源交付。

`make release-generate` 清除调试 ID 后缀并检查锁定组件；`make archive/beta/release PLATFORM=...`
选择独立平台，Bundle ID 为 `{{BUNDLE_IDENTIFIER}}.<platform>`。每个平台需分别在 Apple Developer
注册标识和配置签名，具体要求见 [docs/release-delivery.md](docs/release-delivery.md)。
模版提供交付入口，真机运行、真实签名和商店上传必须在具体产品上验收。

## Worktree Workflow

缓存、DerivedData 与 debug bundle identifier 按工作树隔离。
`make worktree-info` 查看，`make worktree-doctor` 校验，`make clean-worktree` 清理构建缓存。
本地组件覆盖与 `.artifacts/` 也在当前工作树内；删除缓存不会删除正式依赖锁。
