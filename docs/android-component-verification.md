# Android 共享核心、二进制组件与壳验证

更新：2026-09-23。职责与决策见 [Android 架构](android-shell-component-architecture.md)。

本次在 macOS arm64、JDK 17、Gradle 8.10.2、AGP 8.7.3、Kotlin 2.0.21 环境验证。
Dagger 2.52 使用 Java annotation processor；NDK 28.2.13676358、CMake 3.22.1
构建 arm64-v8a 和 x86_64 原生库，核心语言标准为 C++20。
模拟器为 Android API 35；本次没有 Android 真机运行记录。

## 2026-09-23 手机壳基线验收

| 验证 | 结果 |
| --- | --- |
| 初始组件发布 | 七个 AAR 全部构建、发布并生成精确锁；SharedCore 包含两个 ABI 的 JNI 库及匹配未剥离符号 |
| 共享 C ABI | CMake Release 的 C 客户端测试通过，覆盖错误、取消、溢出、输出不变和会话隔离 |
| 主机 JVM/JNI | 4 项测试通过：值/溢出/隔离、并发/关闭、取消与关闭竞争、已取消协程不提交 |
| Home 组件 | 2 项 Fake 服务测试通过：真实公开工厂注入、失败状态映射 |
| Dagger | SDK 和壳各自正常生成；缺失绑定、循环依赖共 4 个反例按预期诊断失败 |
| 产品壳 | Debug、R8 压缩 Release、JVM 测试、Android lint 通过 |
| Debug 模拟器 | 2 项仪器测试通过：二进制服务与会话、资源/UI 计算/导航/Activity 重建 |
| 压缩 Release 运行 | 使用本地默认测试密钥签名，直接安装启动 APK；通过 UIAutomator 读取界面，确认计算得到 42、设置页显示注入的 beta 环境 |
| 无 SDK 源码消费 | 移走 components、core、feature、shared 四个源码目录，clean 后 Debug/Release 全部重新构建成功 |
| 独立版本升级 | 单独发布 Home 0.1.1，其余 SDK 仍为 0.1.0；显式更新锁后壳构建通过 |
| 产物与锁回归 | 6 项 Python 测试通过：篡改、清单替换、覆盖策略、依赖一致性、独立升级、原生归属和共享源码一致性 |
| 模版回归 | 188 项 Python core 测试通过；Android AAPT2 特殊文本资源编译通过 |
| 平台回归 | 11 项通过；Swift 编译缓存受沙箱限制的单项在允许缓存写入后复测通过 |
| 分发 | wheel、sdist、从 sdist 重建的 wheel，以及全部七类模版生成验证通过 |

SDK 校验先验证锁定清单摘要，再验证清单中的产物摘要。源码同步检查确保 Apple 和
Android 的 C++/C ABI 来自根目录 `shared/core/`，平台模版中的副本不允许独立漂移。
NDK 产物的 ELF LOAD 段使用 16 KB 对齐；16 KB 系统上的运行尚需对应设备验收。

## 可复现入口

全新生成工程，在 SDK 已安装固定 NDK/CMake 后运行：

```sh
make components-bootstrap
make core-test
./scripts/test-native
./scripts/verify-di
./gradlew :app:assembleDebug :app:assembleRelease :app:testDebugUnitTest :app:lint
make test-ui
```

`make components-bootstrap` 为初始 SDK 创建锁；已有组件锁不会被 bootstrap 默默替换。
第三方 Gradle 锁随模版交付，组件坐标与内容另由产品锁管理。升级必须显式修改声明、
执行 `scripts/components lock` 和 `resolve`，并按需要更新 Gradle 锁。

本次验收工程与日志在 `/private/tmp/biucing-android-architecture/`，属于开发机临时证据，
不随模版或发行包交付。核心验证工程为 `android-arch` 和 `android-final`。

## 边界与已发现的验证限制

- Debug 仪器测试与压缩 Release 直接运行是两条独立证据。额外尝试让现有
  AndroidJUnitRunner 在压缩 Release 下执行时，运行器因缺少 `androidx.tracing.Trace`
  而在执行测试前崩溃；没有将这个失败算作通过，也没有为通过测试而放宽产品混淆规则。
  模版保持 Debug 仪器测试；Release 使用实际压缩 APK 做独立运行验证。
- 测试签名仅用于本地安装；没有正式签名、AAB 商店上传或商店审核验收。
- 外部 Maven 托管、认证和符号服务由团队配置；默认实现是本地不可变目录仓库。
- CI 工作流已提供但本次未在远端运行；主机 JNI 测试不能替代设备 ABI 验收。
- 真实数据库/文件迁移、同步、后台任务与长任务进度仍按具体产品扩展。

## 2026-09-24 Wear OS / TV 补齐

本次沿用上述工具链，产品扩为 app、wear、tv；SDK 扩为十个 AAR，SharedCore
增加 armeabi-v7a。新增设备验证使用官方 API 34 ARM64 系统镜像。

- 十个 SDK 的 Release 构建与共享 Home 状态单元测试通过。
- 三个应用的 Debug、R8 Release、Android Lint 全部通过（Lint 无错误，保留版本目录建议等警告）。
- Wear OS 圆屏：2 项仪器测试通过，包括旋钮 MotionEvent 驱动列表滚动、真实 JNI
  计算 42、页面导航与 Activity 重建后的状态保留。
- Android TV：1 项仪器测试通过，包括方向键/确认键、焦点恢复、真实 JNI 计算与 Activity 重建。
- Dagger：homestate SDK 和三个壳的缺失绑定/循环依赖，共 8 个反例全部正确拒绝，正常图恢复编译通过。
- 移走 components、core、feature、shared 后，clean 重建三个应用的 Debug/R8 Release 成功，手机 JVM 测试通过。
- 生成器 core 回归 189 项、平台回归 11 项与 AAPT2 特殊文本资源编译通过；wheel、sdist 和七类模板的安装生成验证通过。

日志与工程位于 `/private/tmp/biucing-android-devices/`。设备间会话彼此独立；未实现
手机与手表的伴侣同步。本次 ARMv7 已编译并验证 ELF/符号交付，没有对应设备运行证据。
新增手表、电视的压缩 Release 已编译，运行证据为 Debug 仪器测试；真机、正式签名与
商店发布仍未验收。CI 已扩为 phone / Wear / TV 矩阵，本次没有远端 CI 结果；TV 使用
API 36 x86_64 镜像，因为较旧的 TV x86 镜像不在本模板 ABI 范围内。
