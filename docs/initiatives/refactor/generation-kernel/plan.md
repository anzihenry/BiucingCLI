---
title: "生成内核提取历史"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="generation-kernel-extraction-history"></a>
# 生成内核提取历史

[English](plan.en.md)

原提取阶段，不是第二实现；见[当前边界](../../../engineering/kernel-modules.md)。

<a id="historical-extraction-record"></a>
## 历史提取记录

下述历史执行/计划细节已由当前边界替代，不定义第二算法。阶段 1 提取基础模块，不改生成、资源、序列化、CLI。

| 模块 | 职责 | 包内依赖 |
| --- | --- | --- |
| errors.py | 既有领域异常 | 无 |
| models.py | 元数据/变量 dataclass | 无 |
| catalog.py | 资源路径/加载 | errors/models |
| variables.py | 纯约束 | models |
| rendering.py | 占位映射/单遍 | escaping |
| validation.py | 元数据/文件/Make/占位 | catalog/models/variables/rendering/escaping |
| generation.py | 复制渲染/权限/暂存/发布清理 | errors/models/rendering |

CLI 从所有模块直接导入，templates 显式同对象重导出旧模型/异常/加载；阶段 2 也导出校验/渲染/文件函数常量，仅交互解析留待后续。新模块不导入 CLI/兼容模块。

<a id="resource-loading-and-test-fixtures"></a>
## 资源加载与测试 fixture

```python
from pathlib import Path
from biucingcli.catalog import load_template, load_templates

definition = load_template("frontend")  # package-owned template_data
fixtures = load_templates(root=Path("tests/my-fixtures"))
```

keyword-only root 选元数据 fixture，不是 CLI 选项/插件。默认包相对而非 cwd，列表排序和未知/无效错误不变。重定向 aggregate validator patch catalog.templates_root；导入兼容不等于内部全局 monkeypatch。文件注入移 generation.shutil.copytree。catalog tests 覆盖独立导入、同对象、继承、排序、cwd、root、畸形。阶段 0 快照不变，产物也验提取模块。

<a id="stage-2-boundaries"></a>
## 阶段 2 边界

占位表/模板必需文件分支直接搬，声明契约/规则后续；variables 仅约束，generation 仅执行。generation tests 覆独立/导出、二进制/执行位/空目录/单遍/源保留、既有/晚冲突，以及 copy/render/publish OSError/KeyboardInterrupt 清理；CLI 错误/EOF/SIGINT 仍验用户行为。

<a id="stage-3-pure-template-specific-derivations"></a>
## 阶段 3：纯模板派生

template_rules/apple/android/microservice 拥有平台/module/依赖派生，common 放类型名/RuleResult；旧 helper 是 alias。registry 的实现/分配表不可变；CLI 解析后统一 derive_template_values，不分支；未分配空结果，分配缺实现 InvalidTemplateError，无动态导入。阶段 4 前 Python 内置声明；未知模板先 catalog 失败。

规则接受解析字符串，返回 derived_values（覆盖并入清单）及 render_only_values（随后合并，Apple 片段不进清单）。Apple 平台/module/片段，Android module，micro 依赖/type；显式 module/OS 优先不变，source 记录不改，合并后通用校验，非法选择错误不变。规则无 input/write/command，dispatcher 复制输入，各规则不变参且新结果；无新验证、插件、schema，文件/全局占位表阶段 4 前不变。规则测试覆盖选择/default/explicit/片段转义/非法/fallback/缺实现/隔离/alias/导入；11 快照端到端。

<a id="stage-4-template-scoped-declarations"></a>
## 阶段 4：模板范围声明

保留阶段 3 字符串 helper，生成传完整 Definition/声明 rule。registry 定义精确派生/render-only 集和可覆输入；字段/实际输出均一致。declarations 检查扩展字段、名字、契约、路径、输出、上下文、绑定冲突；contracts 放文件契约；base 永远适用，删声明不能关内置最低要求；category/tags 不再隐选技术文件。

渲染始终据 Definition 的输入/上下文/输出绑定，未知占位失败，额外值不能造绑定；提示/预览/暂存前检查；插入只一遍；新自由文本按 validator 语义识别。legacy_rendering 仅冻结旧无范围调用，不是扩展；to_dict 故意省内部字段，保持 schema 1/golden。见[编写](../../../guides/template-authoring.md)。声明测试展示新 Python 后端/set 文本无需新 flag/rule，负边界/迁移前文件对比；快照不变。

<a id="stage-5-typed-requestsplans-and-injected-interaction"></a>
## 阶段 5：类型请求/计划与交互注入

CreateRequest 包含模板、位置项目、输出、set/显式映射，复制只读；显式优先 set，位置名权威；CLI 用一份 CLI_VARIABLE_ARGUMENTS。

build_generation_plan(request, definition=None, prompt=None) 加载/接受定义、检查声明、解析、派生、校验、收集，读资源但无目录/暂存/输出。定义注入支持 fixture；prompt 接 Variable 返回 string，无 prompt 聚合缺失。

Plan 有类型元数据/路径、只读值、source/预览，是进程内解析结果而非序列化 job、快照、锁；计划执行间源/字段不可改，目标存在不冻结；execute 用既有暂存，再查目标/声明。

```python
from pathlib import Path
from biucingcli.models import CreateRequest
from biucingcli.generation import build_generation_plan, execute_generation_plan

request = CreateRequest("frontend", "demo", Path("/existing/output"),
                        set_values={"display_name": "My Demo"})
plan = build_generation_plan(request)
# Inspect plan.values / plan.target_dir before choosing to execute.
execute_generation_plan(plan)
```

variables 解析/约束无终端；interaction 提示 stderr/EOF/中断；CLI 按 JSON/non-interactive/TTY 选择。core 不加载这些/compat。历史 interactive signatures wrapper；build_create_context/to_context 保旧字典；CLI 预览/create 用 build_create_plan，仅 create 执行；格式化接计划观测目标，阶段 6 再移。

plan tests 覆非 CLI、回调 source、缺失、空、取消、无写、执行冲突/父缺失、分离映射、alias/core 导入；EOF/PTY/JSON/输出基线仍 gate。

<a id="stage-6-presentation-boundary-and-test-organization"></a>
## 阶段 6：展示边界与测试组织

presentation 格式化定义/诊断/计划，不导 catalog/generation/CLI/validation/终端，不加载/写流/选退出；仍观测目标存在。CLI 加载后委托，将 format_error 写 stderr/控制退出；create JSON/schema/output_metadata 统一在 presentation；version 用运行包。

<a id="compatibility-retained-in-this-refactor"></a>
### 此重构保留兼容

templates 显式 alias 与 interactive wrapper；CLI alias 版本、校验/create formatter、派生、计数，list/info wrapper 保旧签名/加载 seam；context 保字典，core 用类型；无范围渲染冻结，生成 scoped，阶段 6 不删旧入口。

这是明确迁移适配，不保证全部全局/mock 为 SDK；新代码导 owning modules。无第三方插件/新运行依赖/模板内容/公开 schema 变。原 test_cli 按行为、原生/服务输出、平台、渲染、规则、校验分类，cli_support fixture；断言/marker 不改，前后 122 方法各一次。五 presentation 测试覆 golden/版本错误/旧适配/流无写/导入；完整映射见[测试](../../../guides/testing.md)。
