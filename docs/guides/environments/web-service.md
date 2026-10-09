---
title: "Web 服务团队环境标准"
status: current
owner: project-maintainers
updated: 2026-10-09
---

<a id="web-service-team-environment-standard"></a>
# Web 服务团队环境标准

[English](web-service.en.md)

> 通用架构及 Docker 开发/部署目标见[后端服务整体架构](../../engineering/backend/architecture.md)。本文件保留既有环境细节；与新目标冲突时以整体架构为准，实际支持仍以生成项目验证为准。

<a id="goal"></a>
## 目标

为中型 Go Web 团队定义环境：面向客户的 HTTP API（内部服务间开发归 microservice），入职/日常开发、依赖/运行时/配置一致性、测试/构建/容器/交付。使用 Go 原生工具链和小型仓库命令集。

<a id="design-principles"></a>
## 设计原则

保持 go、标准包、普通目录原生路径；统一初始化/自动化入口；优先标准库，有明确开发收益才加框架；仓库固定 Go；区分本地、CI、部署；默认明确文件配置；小 starter 保留团队扩展路径。

<a id="standard-stack"></a>
## 标准技术栈

<a id="core-service-toolchain"></a>
### 服务核心工具链

Go 负责模块/编译/测试/格式；Gin 提供轻量路由中间件；net/http/httptest 为默认 HTTP 测试。

<a id="environment-and-tool-installation"></a>
### 环境与工具安装

macOS Homebrew 安装工具；mise 固定/激活 Go 和辅助 CLI。

<a id="dependencies"></a>
### 依赖

Go Modules 为规范依赖管理；go.sum 校验和锁必须提交。

<a id="configuration"></a>
### 配置

YAML 保存入库本地默认值；按需环境变量覆盖部署差异。

<a id="automation"></a>
### 自动化

Makefile 提供开发/CI 稳定入口；Docker 提供可重复打包和部署一致性。可后加 golangci-lint、air/reflex；只有演进 protobuf 时才加入 buf。

<a id="tool-responsibilities"></a>
## 工具职责

<a id="go-toolchain"></a>
### Go 工具链

模块解析、格式、编译、测试、构建运行；不承担整机初始化、容器打包策略或二进制编译之外的发布编排。

<a id="gin"></a>
### Gin

HTTP 路由、中间件、传输层请求响应；不拥有业务、仓储/领域约定或配置管理。

<a id="go-modules"></a>
### Go Modules

go.mod 声明依赖，go.sum 跟踪解析校验和；没有并提交 go.sum 的生成项目视为不完整。

<a id="homebrew"></a>
### Homebrew

从 Brewfile 安装工具，不固定项目运行时。

<a id="mise"></a>
### mise

固定 go 等项目运行时。

<a id="makefile"></a>
### Makefile

公开日常小型稳定命令集。

<a id="docker"></a>
### Docker

构建可运行、接近生产的镜像，验证仓库配置启动；不替代日常 go test/go run。

<a id="standard-repository-layout"></a>
## 标准仓库布局

```text
.
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   ├── handler/
│   ├── model/
│   ├── repository/
│   ├── router/
│   └── service/
├── configs/
│   └── config.yaml
├── tests/
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   └── ci/
├── .mise.toml
├── Brewfile
├── Makefile
├── go.mod
├── go.sum
├── Dockerfile
└── README.md
```

<a id="directory-rules"></a>
## 目录规则

<a id="cmd"></a>
### `cmd/`

只放入口、启动、依赖组装，不堆业务。

<a id="internal"></a>
### `internal/`

不可导出的本服务实现：handler、业务服务、仓储/数据适配、响应/领域模型、路由、配置。专属且不应被其他模块导入的代码归这里。

<a id="configs"></a>
### `configs/`

入库本地/开发默认值，至少一个本地配置；需要时环境覆盖部署值。

<a id="tests"></a>
### `tests/`

HTTP/集成测试；先用 httptest 快速请求响应，再加重型环境。

<a id="scripts"></a>
### `scripts/`

初始化/环境/CI 包装，可调用 brew、mise、go、docker、make；不重复 Makefile 稳定逻辑。

<a id="source-of-truth"></a>
## 事实来源

Brewfile 工具、.mise.toml 运行时、go.mod 图、go.sum 锁、configs/*.yaml 默认配置、Makefile 命令、Dockerfile 打包。个人 shell、全局 Go、临时脚本不作为来源。

<a id="required-root-files"></a>
## 必需根文件

<a id="brewfile"></a>
### `Brewfile`

mise、go、docker、golangci-lint、jq；可选 air、gh。

<a id="misetoml"></a>
### `.mise.toml`

至少固定 go，其他仅实际依赖时加入。

<a id="makefile-1"></a>
### `Makefile`

提供 bootstrap、doctor、tidy、test、run、build、docker-build。

<a id="scriptsbootstrap"></a>
### `scripts/bootstrap`

按需安装 Brew，mise 激活，初次/依赖变更时 go mod tidy。

<a id="scriptsdoctor"></a>
### `scripts/doctor`

检查 Go/版本、需要容器时 Docker、go.sum 存在、本地配置加载成功。

<a id="standard-local-workflow"></a>
## 标准本地流程

<a id="first-time-onboarding"></a>
### 首次入职

安装 Brew 工具，mise 激活，bootstrap、test、run。

<a id="daily-development"></a>
### 日常开发

明确通过 go get/模块修改更新依赖，go mod tidy 更新 go.sum，test，run 迭代，打包变化时 docker-build。

<a id="current-web-service-template-assessment"></a>
## 当前 web-service 模板评估

生成工程已含 cmd/server、internal 配置/handler/service/repository/响应模型、YAML、go.sum、Brewfile、.mise.toml、bootstrap/doctor、开发/运行镜像、verify。示例用户仓储仍在内存。

布局遵循 [Go 服务模块指导](https://go.dev/doc/modules/layout)，cmd 放命令、internal 放实现。context 传到 service/repository，遵循 [Go 取消指导](https://go.dev/doc/database/cancel-operations)，方便未来数据库/远程调用。YAML 为入库本地默认，CONFIG_FILE、SERVICE_NAME、HTTP_PORT 选择/覆盖运行配置，符合[部署环境配置](https://12factor.net/config)。

仓库 macOS 平台套件测试新生成项目 Go 代码。Web 产物工作流在 Linux 构建开发镜像、verify、运行镜像；工作站复现仍需本地 Docker daemon。

<a id="recommendation"></a>
## 建议

保持默认 starter 小。下一步可选真实数据库示例，以具体存储实现迁移、事务、readiness；采集/导出路径确定时增加结构化请求日志和 tracing。这些为扩展点，不是生成基础 HTTP 服务的前提。
