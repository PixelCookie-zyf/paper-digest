<div align="center">
<pre>█▀█ ▄▀█ █▀█ █▀▀ █▀█   █▀▄ █ █▀▀ █▀▀ █▀ ▀█▀
█▀▀ █▀█ █▀▀ ██▄ █▀▄   █▄▀ █ █▄█ ██▄ ▄█  █ </pre>

**让 AI 替你读论文 —— 从经典到前沿，一篇一篇来。**

中文 | [English](README.md)

</div>

---

> **支持斜杠命令** — 在 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 或任何 LLM 工具中安装为 `/paper-digest`。零依赖，开箱即用。[查看安装方法 →](#安装为斜杠命令)

---

## 为什么做这个

读论文是个体力活。不管是 LLM Agent、多模态推理、RAG 还是代码生成，哪个方向都是论文堆积如山。你想系统地读一遍，但是：

- 不知道从哪篇开始
- 不知道哪些值得读、哪些是水文
- 读完记不住重点
- 中英文来回切换很累

这个工具帮你解决这些问题。

## 工作流程

1. **规划** — LLM 根据方向生成搜索词，自动判断这个领域从什么时候开始
2. **搜索** — 按时间顺序搜索 arXiv，从经典论文开始
3. **去重** — 跳过你已经读过的论文
4. **AI 筛选** — AI 判断每篇论文：值不值得你花时间？
5. **深度阅读** — 下载完整 PDF，提取全文
6. **总结** — 逐篇送给 LLM 生成详细的双语分析
7. **生成** — 每篇论文一个 MDX 文件，结构清晰，可直接发博客

明天再跑一次，自动接上次的进度，永远不重复。

## 核心特点

- **按时间线阅读** — LLM 自动判断这个方向从什么时候开始，从经典论文往后推进。先打基础，再看前沿，建立完整的知识脉络。
- **AI 帮你筛** — 搜到一批候选论文后，先让 AI 快速过一遍摘要，判断值不值得精读。水文直接跳过，省时间。
- **一篇一篇精读** — 不是把一堆论文塞给 AI 批量总结。每篇论文单独下载完整 PDF，提取全文，独立送给 LLM 认真写总结。
- **中英双语** — 每个部分都同时输出中文和英文。不是机翻，AI 分别用两种语言原生撰写。
- **跑完接着跑** — 自动记录已处理的论文。今天跑 3 篇，明天跑 3 篇，一周就能系统过完一个方向的经典论文。不会重复。
- **看得见进度** — 终端里有转圈动画和每步耗时，清楚知道工具在干嘛。

---

## 安装为斜杠命令

**这是推荐的使用方式。** 不需要 Python，不需要 pip，不需要 API key — LLM 自己搞定一切。

### 第一步：安装

```bash
# 方式 A：克隆项目，在项目内使用
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest

# 方式 B：全局安装（任何项目都能用）
mkdir -p ~/.claude/commands
curl -o ~/.claude/commands/paper-digest.md \
  https://raw.githubusercontent.com/PixelCookie-zyf/paper-digest/main/.claude/commands/paper-digest.md
```

### 第二步：使用

```
/paper-digest                                   # 默认："LLM Agent"
/paper-digest "multimodal reasoning"            # 任意研究方向
/paper-digest "RAG evaluation" --max 5          # 读 5 篇
/paper-digest --start-date 2024-01-01           # 从指定日期开始
/paper-digest --no-screen                       # 跳过筛选，全都读
```

就这样。LLM 会自己搜 arXiv、筛论文、读 PDF、写双语总结、生成 MDX 文件 — 全程自动。

### 进阶：用外部 LLM API 做总结

```
/paper-digest --summarizer api                  # 使用 .env 中的 LLM_API_KEY
/paper-digest --mode script                     # 改用 Python 脚本跑完整流程
```

| 模式 | 工作方式 | 需要什么 |
|------|---------|---------|
| `native`（默认） | LLM 自己干所有事 | 什么都不需要 |
| `script` | 调用 Python 脚本（`main.py`） | Python 依赖 + `.env` |

| 总结引擎 | 工作方式 | 需要什么 |
|---------|---------|---------|
| `claude`（默认） | LLM 自己写总结 | 什么都不需要 |
| `api` | 调用外部 LLM API | `.env` 中配置 `LLM_API_KEY` |

### 给其他 LLM / Agent 框架用

`.claude/commands/paper-digest.md` 是一个**自包含的 prompt 文件** — 包含完整工作流、arXiv 查询语法、双语总结 JSON schema 和 MDX 模板。你可以：

1. 作为 system prompt 喂给任何 LLM
2. 改造成 LangChain、CrewAI 等 Agent 框架的流程
3. 作为参考规范来构建你自己的工具

---

## 替代方式：用 Python 脚本运行

如果你更喜欢 Python 脚本（支持任何 OpenAI 兼容的 LLM API）：

### 安装

```bash
git clone https://github.com/PixelCookie-zyf/paper-digest.git
cd paper-digest
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，填入你的 LLM_API_KEY
```

### 用法

```bash
python main.py                          # 默认："LLM Agent"
python main.py "multimodal reasoning"   # 任意方向
python main.py -n 5                     # 读 5 篇
python main.py --pool-size 50           # 搜索范围扩大
python main.py --start-date 2024-01-01  # 从指定日期开始
python main.py --no-screen              # 跳过筛选
python main.py --history                # 看看已经读过哪些
```

### 配置 (.env)

```env
# 支持：MiniMax、OpenAI、DeepSeek、Qwen、Ollama 等
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.minimaxi.com/v1    # 默认：MiniMax
LLM_MODEL=MiniMax-M2.7
OUTPUT_DIR=output
```

---

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
├── .claude/commands/        # 斜杠命令（skill）文件
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
