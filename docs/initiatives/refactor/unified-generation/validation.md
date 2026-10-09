---
title: "统一生成内核"
status: completed
owner: project-maintainers
updated: 2026-10-09
---

<a id="unified-generation-kernel"></a>
# 统一生成内核

[English](validation.en.md)

> 专题材料：记录对应阶段的背景、方案或验收；当前使用依据见[文档地图](../../../README.md)。

<a id="scope-and-contract"></a>
## 范围与契约

保留 CLI/模块、Request→Plan→execute。payload/平台/依赖/命令/JSON 不变，无插件/升级/共享后端 payload。所有模板选 common 或 common+variant，校验有效输出，统一暂存发布；全部计划有清单/指纹，普通输出不含 variant。

普通模板有意行为变化：拒源 symlink/特殊文件/不安全路径/大小写 Unicode 冲突；创建完整检查元数据/入口/Make/占位；拒计划后源漂移；悬空目标链接为冲突；只读文本渲染/恢复权限/失败清理；执行脚本判定用工程相对路径。指纹仅一致性，不是快照/锁；仍 check-rename，不保证任意并发下原子 no-replace。

<a id="delivery-stages"></a>
## 交付阶段

契约/单多层测试；统一层/枚举/指纹/校验；计划和兼容入口同发布器、删 copytree；core/platform/distribution/golden/文档。各阶段独立提交；正常快照不变，明确边界测试而非批量重生成；仅 payload 变才需全设备/部署。

<a id="baseline"></a>
## 基线

213 core/validate，聚焦 51；普通允许 symlink/copytree，variant 才指纹/严格验证。共享测试先现有交集再扩。

<a id="stage-2-result"></a>
## 阶段 2 结果

统一层选择、严格枚举/指纹，validate 全清单有效验证，缺失仍聚合；直到阶段 3 尚双执行。42 focused/Ruff/validate 通过，payload/golden 不变。

<a id="stage-3-result"></a>
## 阶段 3 结果

全计划必有清单/指纹/同发布。render_template 保解析值签名，适配同准备/发布，不重 default/prompt/派生；删 copytree；普通省 variant，手工不完整计划失败。测试覆 drift/有效校验/symlink/只读清理/祖先无关/冲突/取消/二进制空目录/直接等价。CLI set 前 metadata preflight 保优先级，core 也校验；重复 preflight 仅 metadata。223 core/Ruff/golden 通过。

<a id="final-acceptance-2026-10-06-asiashanghai"></a>
## 最终验收（2026-10-06，Asia/Shanghai）

- core 223（29.138 秒），golden 不变。
- platform 12、零跳过（31.631 秒）。
- Ruff E4/E7/E9/F、validate、diff check 通过。
- verify-distribution --check-make：637 资源 wheel/sdist/rebuilt wheel 字节/执行位一致，七模板及 frontend SSG/SSR、parser/Make 源树外通过。
- Git 比较 template_data/shared/golden 不变，无需重跑全设备/部署。

首次沙箱平台 Swift/Go loopback operation not permitted；工具/缓存/socket 可访问时完整重跑通过，无跳过/弱化。临时诊断日志：/tmp/biucing-unified-core.log、platform.log、platform-unrestricted.log、distribution.log（均带 biucing-unified- 前缀），非持久发布证据。阶段 1–4 完成，模块/平台模板不变，以上有意契约已适用。
