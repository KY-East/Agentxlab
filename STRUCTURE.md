# Agent X Lab 仓库结构与规范

本文档是仓库的使用手册，定义目录结构、命名规则和操作流程。AI 协作时应首先阅读本文件。

---

## 目录结构

```
Agent X Lab/
├── README.md                Lab 总览
├── CHANGELOG.md             变更记录
├── STRUCTURE.md             本文件：仓库规范
│
├── research/                研究方向
│   ├── language-and-meaning/
│   ├── thinking-and-creativity/
│   ├── subjectivity-and-intentionality/
│   ├── sociality-and-context/
│   ├── systems-and-architecture/
│   ├── formal-foundations/
│   ├── (未来新方向)/
│   └── synthesis/           跨方向综合
│
├── notes/                   研究笔记
│   ├── agenda/              课题管理（按期）
│   ├── journal/             研究日志
│   └── ideas/               灵感与种子
│
└── projects/                工程项目
    └── (项目名)/
```

---

## 研究方向（research/）

### 命名规则

- 文件夹使用语义化的 kebab-case slug，例如 `language-and-meaning`
- 不使用数字编号前缀，阅读顺序由根 README 的表格控制
- 新增方向直接创建新文件夹，无需修改现有方向

### 每个方向的标准文件

| 文件 | 职责 |
|------|------|
| `README.md` | 方向概述、文件导航、开放问题清单 |
| `papers.md` | 论文索引表格（经典文献 + 前沿研究） |
| `classics.md` | 经典文献笔记 |
| `frontier.md` | 前沿论文笔记 |
| `pdfs/` | 已下载的论文全文 |

### 笔记格式规范

每条笔记包含以下固定章节：

```
## [作者] —《[标题]》([年份])       ← 经典
## [标题] ([年份])                   ← 前沿

### 核心论点
### 原文金句                         ← 英文原文 + 中文翻译
### 关键概念
### 与本方向的关联
### 通俗理解                         ← 非专业读者可理解的解释
```

### 新增方向流程

1. 在 `research/` 下创建 kebab-case 文件夹
2. 按标准文件列表创建 `README.md`、`papers.md`、`classics.md`、`frontier.md`、`pdfs/`
3. 在根 `README.md` 的研究方向表格中添加一行
4. 在 `CHANGELOG.md` 中记录

### 拆分方向流程

1. 原文件夹保留，新文件夹并列创建
2. 将相关论文和笔记迁移至新方向
3. 在两个方向的 `README.md` 中互相交叉引用
4. 更新 `synthesis/` 中的相关文档

---

## 跨方向综合（research/synthesis/）

| 文件 | 内容 |
|------|------|
| `README.md` | 总体图景 + 经典与前沿的对话 + 子文档导航 |
| `crossroads.md` | 核心交叉节点 |
| `debates.md` | 关键论争地图 |
| `roadmap.md` | 研究路线图（基础层→中间层→应用层） |
| `concept-map.md` | 概念关系图 + 理论线索 + 方法论附注 |

新增交叉分析时，在此目录下创建新文件，并在 `README.md` 的导航表中添加链接。

---

## 研究笔记（notes/）

| 子目录 | 用途 |
|--------|------|
| `agenda/` | 按期管理研究课题。每期一个 `phase-NN.md`，`README.md` 维护索引 |
| `journal/` | 自由格式的研究日志，按日期或主题命名 |
| `ideas/` | 未成熟的想法和灵感。发展为正式课题后迁入 `agenda/` |

### 新增课题流程

1. 在 `notes/agenda/` 下创建 `phase-NN.md`
2. 在 `notes/agenda/README.md` 的索引表中添加一行
3. 在 `CHANGELOG.md` 中记录

---

## 工程项目（projects/）

每个项目是独立文件夹，内部结构由项目本身决定。

### 新建项目流程

1. 在 `projects/` 下创建以项目名命名的文件夹
2. 项目根目录必须包含 `README.md`，声明项目目标、技术栈、关联的研究方向
3. 在 `projects/README.md` 的索引表中添加一行
4. 在 `CHANGELOG.md` 中记录

---

## 全局规范

### 语言

- 正文使用中文
- 论文标题、作者名、直接引用保留英文原文
- 引用同时提供英文和中文翻译

### 文风

- 学术、正式的陈述风格
- 禁止"不是X，而是Y"句式
- 避免过多破折号
- 每条笔记必须包含"通俗理解"章节

### 变更记录

所有以下操作必须在 `CHANGELOG.md` 中记录：
- 新增研究方向
- 新增工程项目
- 新增研究课题（phase）
- 大批量论文添加
- 结构性变更（目录重组、文件迁移等）

### 文件命名

- 目录：kebab-case（`language-and-meaning`）
- Markdown 文件：kebab-case（`phase-01.md`、`concept-map.md`）
- PDF 文件：描述性名称（`Anthropic_Reward_Hacking_Misalignment.pdf`）
