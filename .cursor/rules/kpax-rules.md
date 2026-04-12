---
description: KPAX 产品开发规则
globs: ["KPAX.md", "kpax/**"]
alwaysApply: true
---

# KPAX — 开发规则

## 核心原则

1. **不重复造轮子**: 能用现成开源方案的就直接封装进来，不自己重写
   - 记忆系统：借鉴 Hermes Agent (MIT) 的三层记忆架构，直接封装其设计模式
   - Agent 编排：用 Claude / OpenAI Assistants API，不自建编排层
   - LLM 推理：继续用 LiteLLM 多模型调度
   - 辩论引擎 / 知识图谱：复用 Agent X Lab 自有引擎
   - 自己只做：记忆层管理、领域专家优化、报告生成 — 这是差异化壁垒

2. **Agent X Lab 是 KPAX 的 R&D 引擎**: 用 Agent X Lab 的交叉学科发现能力来指导 KPAX 的专家阵容设计，而不是拍脑袋

3. **知识付费，不是预测机器**: KPAX 卖的是"让你做更聪明的决策"，不承诺预测结果。报告里永远标注置信度和不确定性来源

4. **技术选型优先级**: 成熟开源 > 自建封装 > 从零开发

## 技术借鉴清单

| 来源 | 借鉴内容 | 许可证 |
|------|---------|--------|
| Hermes Agent (NousResearch) | 三层记忆系统、Skills 自进化、渐进式加载、PLUR 共享记忆 | MIT |
| Agent X Lab (自有) | 辩论引擎、反向发现、知识图谱、Token 配额 | 自有 |
| Zep Cloud | 跨会话记忆检索 | 商用 API |
| LiteLLM | 多模型统一调度 | MIT |

## 记忆系统设计（借鉴 Hermes）

四层记忆，各层职责分明：

- **Layer 1 持久记忆**: 用户画像 + 全局知识，会话开始注入，中间不改（冻结快照模式）
- **Layer 2 技能记忆**: 分析模板自动沉淀，渐进式加载（Level 0/1/2）
- **Layer 3 会话搜索**: SQLite FTS5 + Zep Cloud，历史分析结果检索
- **Layer 4 共享记忆**: 跨用户知识积累，纠正自动传播

## 产品定位

- KPAX 是分析工具，不是赌博平台
- 不碰用户资金，不做投注建议
- 合规优先：任何情况下不承诺预测准确率
