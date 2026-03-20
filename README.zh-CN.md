<div align="center">
<pre>█▀█ ▄▀█ █▀█ █▀▀ █▀█   █▀▄ █ █▀▀ █▀▀ █▀ ▀█▀
█▀▀ █▀█ █▀▀ ██▄ █▀▄   █▄▀ █ █▄█ ██▄ ▄█  █ </pre>

**让 AI 替你读论文 —— 从经典到前沿，一篇一篇来。**

中文 | [English](README.md)

</div>

---

## 为什么做这个

读论文是个体力活。不管是 LLM Agent、多模态推理、RAG 还是代码生成，哪个方向都是论文堆积如山。你想系统地读一遍，但是：

- 不知道从哪篇开始
- 不知道哪些值得读、哪些是水文
- 读完记不住重点
- 中英文来回切换很累

这个工具帮你解决这些问题。

## 工作流程

```
python main.py
```

就这一行。工具会自动：

1. **规划** — LLM 根据方向生成搜索词，自动判断这个领域从什么时候开始
2. **搜索** — 按时间顺序搜索 arXiv，从经典论文开始
2. **去重** — 跳过你已经读过的论文
3. **AI 筛选** — AI 判断每篇论文：值不值得你花时间？
4. **深度阅读** — 下载完整 PDF，提取全文
5. **总结** — 逐篇送给 LLM 生成详细的双语分析
6. **生成** — 每篇论文一个 MDX 文件，结构清晰，可直接发博客

明天再跑一次，自动接上次的进度，永远不重复。

## 核心特点

- **按时间线阅读** — LLM 自动判断这个方向从什么时候开始，从经典论文往后推进。先打基础，再看前沿，建立完整的知识脉络。
- **AI 帮你筛** — 搜到一批候选论文后，先让 AI 快速过一遍摘要，判断值不值得精读。水文直接跳过，省时间。
- **一篇一篇精读** — 不是把一堆论文塞给 AI 批量总结。每篇论文单独下载完整 PDF，提取全文，独立送给 LLM 认真写总结。
- **中英双语** — 每个部分都同时输出中文和英文。不是机翻，AI 分别用两种语言原生撰写。
- **跑完接着跑** — 自动记录已处理的论文。今天跑 3 篇，明天跑 3 篇，一周就能系统过完一个方向的经典论文。不会重复。
- **看得见进度** — 终端里有转圈动画和每步耗时，清楚知道工具在干嘛。

## 快速开始

```bash
# 安装
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 配置
cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY

# 运行
python main.py
```

## 用法

```bash
python main.py                          # 默认："LLM Agent"
python main.py "multimodal reasoning"   # 换个方向
python main.py -n 5                     # 这次多读 5 篇
python main.py --pool-size 50           # 搜索范围扩大
python main.py --start-date 2024-01-01  # 从 2024 年开始
python main.py --no-screen              # 跳过筛选，全都读
python main.py --history                # 看看已经读过哪些
```

## 作为斜杠命令使用（适配 LLM 编程工具）

Paper Digest 可以作为**斜杠命令**在 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或任何支持 `.claude/commands/` 的 LLM 工具中运行。

### 安装

命令文件已经在项目的 `.claude/commands/paper-digest.md` 中。用 LLM 工具打开这个项目即可使用。

如果想全局可用（任何项目都能调用），复制一下：

```bash
mkdir -p ~/.claude/commands
cp .claude/commands/paper-digest.md ~/.claude/commands/
```

### 命令用法

```
/paper-digest                                   # 默认："LLM Agent"，Claude 自己总结
/paper-digest "multimodal reasoning"            # 换个方向
/paper-digest --max 5                           # 处理 5 篇
/paper-digest --summarizer api              # 用外部 LLM API 而不是 Claude
/paper-digest --mode script                     # 用 Python 脚本跑
/paper-digest --start-date 2024-01-01           # 从 2024 年开始
/paper-digest --no-screen                       # 跳过质量筛选
```

### 运行模式

| 模式 | 工作方式 | 需要什么 |
|------|---------|---------|
| `native`（默认） | LLM 自己干所有事 — 搜索、筛选、读 PDF、写总结、生成 MDX | 什么都不需要 |
| `script` | 调用 Python 脚本（`main.py`） | Python 依赖 + `LLM_API_KEY` |

### 总结引擎

| 选项 | 工作方式 | 需要什么 |
|------|---------|---------|
| `claude`（默认） | LLM 自己写总结 | 什么都不需要 |
| `api` | 调用外部 LLM API 生成总结 | `.env` 中配置 `LLM_API_KEY` |

### 给其他 LLM / Agent 框架用

`.claude/commands/paper-digest.md` 是一个自包含的 prompt 文件，包含了完整的工作流、arXiv 查询构建方式、总结 JSON schema 和 MDX 模板。你可以：

1. 作为 system prompt 喂给任何 LLM
2. 改造成其他 Agent 框架的流程（LangChain、CrewAI 等）
3. 作为参考规范来构建你自己的论文阅读工具

文件里包含了 LLM 需要知道的一切 — 不需要额外文档。

---

## 配置 (.env)

```env
LLM_API_KEY=your_key_here           # 必填
LLM_BASE_URL=https://api.minimaxi.com/v1    # 默认：MiniMax
LLM_MODEL=MiniMax-M2.7
OUTPUT_DIR=output
```

## 生成的 MDX 长什么样

每篇论文一个 `.mdx` 文件，包含：

| 内容         | 说明                           |
|-------------|--------------------------------|
| 论文标题     | 中英双语                        |
| 一句话概述   | 做了什么、为什么重要              |
| 研究问题     | 要解决什么问题                   |
| 摘要总结     | 动机、方法、结果                  |
| 核心方法     | 具体的技术方案                   |
| 模型/框架    | 架构和组件                       |
| 数据集       | 用了什么数据、规模多大            |
| 实验设置     | 基线、指标、关键参数              |
| 主要结果     | 关键数据和发现                   |
| 创新点       | 有什么新东西                     |
| 局限性       | 不足之处                        |
| 适用场景     | 适合用在哪里                     |
| 重点关注     | 作为读者应该关注什么              |
| 关键词       | 中英双语                        |

带 frontmatter，可以直接用在博客里。

## 项目结构

```
├── main.py                  # 命令行入口，带 rich 进度 UI
├── config/                  # 从 .env 读取配置
├── paper_search/            # arXiv 搜索（可扩展其他源）
├── paper_fetch/             # PDF 下载 + 全文提取
├── llm_summary/             # LLM 筛选 + 深度总结
├── mdx_writer/              # 逐篇生成双语 MDX
├── history.py               # 跨次运行的去重追踪
├── processed_papers.json    # 自动生成的阅读记录
└── output/                  # 你的论文摘要在这里
```

## 终端效果

```
╭──────── Paper Digest ────────╮
│ Query: RAG evaluation        │
│ Model: deepseek-chat         │
│ Pool:  20 candidates         │
│ Goal:  3 papers              │
╰──────────────────────────────╯

  LLM 正在规划搜索策略... (2.1s)
  覆盖检索增强生成、忠实性评估、RAGAS 基准测试...
  搜索词: 4 条 | 从: 2020-05-01

  搜索 arXiv...
  找到 18 篇候选论文
  全部 18 篇都是新的

──────────── Paper 1/18 ────────────
  Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
  2020-05-22 · Patrick Lewis, Ethan Perez...

  PASS (2.8s) RAG 奠基论文
  PDF extracted (6.2s) 41,208 chars
  deepseek-chat 正在精读并撰写总结...
  Summary done (38.5s)
  Saved: output/2026-03-20-retrieval-augmented-generation-for-knowledge.mdx

┌──── Done — 处理了 3 篇论文 ────┐
│ #  File                         │
│ 1  output/2026-03-20-retrieval… │
│ 2  output/2026-03-20-self-rag…  │
│ 3  output/2026-03-20-ragas-au…  │
└─────────────────────────────────┘
```

---

<div align="center">

*Built with arXiv API, any LLM you like, and a lot of coffee.*

</div>
