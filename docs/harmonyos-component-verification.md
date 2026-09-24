# HarmonyOS 核心、字节码组件与壳验证

本轮共同契约变更的新增验证见[实现与验证记录](cross-platform-architecture-verification.md)；以下保留原阶段证据，不能自动视为新实现的复测结果。

更新：2026-09-24。设计与决策见 [HarmonyOS 架构](harmonyos-shell-component-architecture.md)。

## 本地环境

macOS arm64；DevEco 内置 Node 18.20.1、ohpm 6.1.2.285、hvigor/plugin 6.24.4、
HarmonyOS SDK 6.1.1.125（API 24 工具）、Native Clang 15.0.4、CMake 3.28.2。
生成工程的兼容/目标声明为 `5.0.0(12)`。组件生产和消费使用同一受检工具链。

## 已执行的验收

| 检查 | 结果与边界 |
| --- | --- |
| 共享源码 | 同步脚本纳入 HarmonyOS；C++/C ABI 来源与 Apple、Android 一致 |
| C ABI | CMake Release 的 C 客户端测试通过，包含错误、输出不变、取消与会话隔离 |
| 宿主 Node-API | 使用生产 bridge.cpp 编译宿主插件；完整 int64、溢出、非法输入、类型标记、取消、重叠调用拒绝、关闭及 GC 保活通过 |
| ArkTS 包装与模型 | SDK TypeScript 编译器转译实际非 UI 源码，在宿主测试输入复制、串行队列、取消、关闭、会话隔离与 Fake 注入通过 |
| 字节码 HAR | contracts、sharedcore、homefeature 三个 SDK 真实编译并独立发布；下游使用预编译 contracts |
| 原生切片 | SharedCore 的 arm64-v8a 和 x86_64 ELF 库编译、打包通过；功能 HAR 不携带原生核心 |
| 原生符号 | 发布未剥离库；实际 readelf 检查包含 `.debug_info` 与 `.debug_line` |
| Hypium | 3 项通过：应用标识、已发布 HomeFactory 注入 Fake、取消订阅及幂等通知 |
| DI | 组件/壳构造图分别生成；缺失依赖与环路反例正确失败；真实 ArkTS 编译校验生成调用 |
| 直接构建门禁 | 壳描述人为引入缺失绑定时，直接 hvigor 构建失败；恢复后正常构建 |
| 产品 HAP | `make verify` 通过，产出无签名 HAP，包含五类设备声明、两个 ABI 的唯一核心库与 libc++ 运行库 |
| 设备测试包 | `make build-device-tests` 成功编译实际 SharedCore 调用/关闭/取消/隔离测试；未在设备执行 |
| 单组件升级 | HomeFeature 0.1.1 单独发布，仍消费 contracts 0.1.0，显式锁定安装后 HAP 构建通过 |
| 本地覆盖限制 | 实际设置覆盖后，直接 hvigor 的 Release 和 CI 构建均按预期拒绝；清除后恢复 |
| 无源码消费 | 移走 `components/` 和 `shared/`，执行 clean 后 Debug/Release HAP 均构建成功 |
| Python 分发 | wheel、sdist、从 sdist 重建 wheel 的 472 项资源字节/执行位一致，全部七类模版安装生成通过 |
| 初始化流程 | `make components-bootstrap`、`make bootstrap`、`make doctor`、冻结第三方锁校验通过 |
| Python 回归 | 新增 10 项组件测试；核心套件 199 项通过；平台套件 11 项通过（Swift 缓存受限单项改用临时缓存复测通过） |

宿主转译测试不等于 ArkTS VM/设备运行；native 交叉编译不等于对应设备运行。
Hypium 的 Fake 服务测试验证公共组件契约，不能代替真实 Node-API 在 HarmonyOS 上的执行。

## 可复现入口

配置工具链 PATH、DEVECO_SDK_HOME 与 HOS_SDK_HOME 后，全新生成工程：

```sh
make components-bootstrap
make bootstrap
make core-test
make test-native
make verify-di
make verify
make build-device-tests
```

源码移除验收应在可丢弃的生成工程中进行：把 `components/`、`shared/` 移到产品之外，
分别执行以下两条命令，再恢复源码目录：

```sh
hvigorw clean assembleHap --mode module -p module=entry@default --no-daemon
hvigorw clean assembleHap --mode module -p module=entry@default -p buildMode=release --no-daemon
```

产品与组件锁必须保留；不需要源代码来解析、安装或验证已发布 SDK。
原生设备测试位于 `entry/src/ohosTest/ets/test/List.test.ets`。连接受支持设备并配置
合法测试签名后，可通过 DevEco 执行该测试集；当前没有已连接设备或本次签名凭证。

本地临时日志位于 `/tmp/biucing-harmony-work/`，不随模版交付。
仓库提供手动触发的 `harmonyos-components.yml`，需要配置 `harmonyos-sdk611` runner；
本轮没有远端执行记录，不应将该工作流视为已经启用的合入门禁。

## 明确未完成的外部验收

- `hdc list targets` 返回空：尚无 HarmonyOS 模拟器或真机运行结果。
- 当前 SDK 明确拒绝 armeabi-v7a；不声明支持该架构或其他应用模型的轻量手表。
- 手表旋钮/圆屏、电视遥控器焦点、大屏多窗口、无障碍与性能/功耗需产品级验收。
- 没有使用真实开发者签名、上传市场或配置远端产物/符号服务器。
- 当前核心是架构示例，没有真实业务数据库、格式迁移、跨设备同步或进度回调。

hvigor 在字节码 HAR 的资源合并阶段会输出同名资源重复声明警告；本次对应同一组件
资源在 SDK 与生成中间资源表中的重复来源，编译和打包通过。业务组件增加资源后仍需
检查命名冲突及最终设备显示，不能把本次结果扩展为任意资源组合的兼容保证。
