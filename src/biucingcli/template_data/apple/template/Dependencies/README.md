# 二进制依赖

`components.json` 声明精确版本；`components.lock.json` 由显式 `lock` 命令生成并提交。
首次执行 `make components-bootstrap` 发布随模版提供的源码到 `.artifacts/`，再生成锁。
普通 `make generate` 只校验、解析锁定产物，不构建组件源码。

`./scripts/components build --version 0.1.1` 构建新的不可变版本；再修改声明并执行
`./scripts/components lock`。同版本不得覆盖；团队应使用共享的不可变产物仓库。
`COMPONENT_REGISTRY=/absolute/path` 可指向已同步的团队仓库；托管传输层由团队选择。
校验和与版本锁必须进入代码评审，不能把它们当作来自不可信来源的签名认证。

`./scripts/components override set HomeFeature /absolute/path/to/HomeFeature/0.1.1`
显式使用本地二进制；`override info` 查看；`override clear HomeFeature` 清除。
本地覆盖配置被 Git 忽略，CI 与 release 解析一律拒绝任何覆盖。
