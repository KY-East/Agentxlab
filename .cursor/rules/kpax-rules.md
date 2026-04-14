---
description: KPAX 产品开发规则
globs: ["KPAX.md", "kpax/**"]
alwaysApply: true
---

# KPAX — 开发规则

## 核心原则

0. **写代码前先问：这个能力该在 Agent X Lab 还是 KPAX？** 现在是两个项目。判断标准：凡是"让专家分析"的能力（辩论、评估、概率估计、利弊权衡），都在 Agent X Lab；凡是"对接用户"的能力（问题解析、约束匹配、路径规划、报告渲染），都在 KPAX。概率估计、利弊权衡、多维评估不是 KPAX 的独立组件，而是 AXL 辩论引擎在不同问题类型下的不同运行模式——KPAX 只需要传不同的辩论目标指令。

1. **KPAX 不做辩论**: Agent X Lab 是学术底座，KPAX 是上层产品。辩论引擎、专家生成、反向学科发现全部调用 Agent X Lab 的函数（`reverse_discovery`、`generate_agents`、`run_round_stream`），一行都不重写。KPAX 只做三件事：问题解析、数据注入、报告生成。

2. **不重复造轮子**: 能用现成开源方案的就直接封装进来，不自己重写
   - 记忆系统：借鉴 Hermes Agent (MIT) 的四层记忆架构，直接封装其设计模式
   - Agent 编排：用 Claude / OpenAI Assistants API，不自建编排层
   - LLM 推理：继续用 LiteLLM 多模型调度
   - 辩论 / 专家生成 / 知识图谱：直接调用 Agent X Lab，不做封装层

3. **Agent X Lab 是 KPAX 的学术底座**: 辩论流程全走 Agent X Lab。KPAX 在辩论前注入数据（论文 + 实操经验），辩论后生成报告。

4. **知识付费，不是预测机器**: KPAX 卖的是"让你做更聪明的决策"，不承诺预测结果。

5. **技术选型优先级**: 成熟开源 > 自建封装 > 从零开发

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
