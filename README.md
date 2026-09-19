# Empirical Research Skills

**面向不同主题实证论文、兼顾零编程基础使用者的 AI 工作流技能包。**

从环境搭建、项目目录、数据处理，到实证分析、隔离探索、证据写作和一致性检查。适用于经济学、管理学、公共政策、教育及其他定量社会科学研究；不会预设某个政策、因变量、样本、估计器或目标期刊。

This is a Chinese-first, topic-independent skill pack for reproducible empirical research. Skills are Markdown instructions, with optional Python helpers. No paid API, external skill collection, or particular AI client is required to read the material.

## 你可以怎样使用

向支持技能的助手描述目标，例如：

- “我不会编程，帮我检查并搭建这个项目的 Python 和 uv 环境。”
- “整理这份企业面板，检查重复键、缺失和合并时丢失的样本。”
- “我研究教育政策与学生成绩，帮我规划数据流程和识别设计。”
- “试一下另一种指标，保留正式结果。”
- “把这一组结果写成论文段落，并核查结论有没有超过证据。”

助手应先读当前项目约定，复用现有目录和运行链；只有缺少这些约定时才采用本包模板。只改文字不要求安装完整分析环境，只改图的样式不要求重新估计模型。

## 8个技能

| 技能 | 负责什么 |
|---|---|
| `empirical-workflow` | 识别任务范围，衔接需要的步骤 |
| `empirical-setup` | 检查、安装和激活项目环境，指导新手处理报错 |
| `empirical-project` | 目录、文件归属、项目配置与交接 |
| `empirical-data` | 数据字典、清洗、匹配、变量构造和质量检查 |
| `empirical-analysis` | 模型执行、真实依赖、缓存核验和复现记录 |
| `empirical-explore` | 隔离探索、完整记录设定、按明确范围采纳 |
| `empirical-writing` | 文献核验、论断与证据对应、正文与交付衔接 |
| `empirical-audit` | 数据、结果、引用、正文与交付的一致性检查 |

技能可以独立使用；总入口也不要求每次调用全部技能。计量方法以研究问题和设计为准，不把DID、六项控制变量、显著性或期刊审稿意见设成通用要求。

## 安装：先选你使用的工具

**安装 Skill 不需要先安装 Python、uv 或 Node.js。** 先安装技能，再让 `empirical-setup` 帮你搭建研究环境。以下假设你已经能打开并使用 Codex 或 Claude Code。

### Codex：复制一句话

先在 Codex 中打开你的论文项目，再把下面这段话发送给它：

> 请从 https://github.com/Rookiecoder-jsjs/empirical-research-skills 安装 skills/ 下的全部8个技能到当前论文项目的 .agents/skills/。读取仓库默认分支及安装说明，不要假定分支叫 main。复制完整技能目录；安装前统一检查同名冲突，遇到冲突先保留已有文件并报告。没有 Python 或 Git 时可下载 ZIP 后复制，不要为了安装 Skill 先安装分析环境。完成后报告安装位置和8个技能名称，并告诉我如何检查它们是否已被 Codex 识别。

项目位置不明确时，助手会先让你选论文文件夹。安装完成后，在技能选择器中检查 `empirical-workflow`；没有出现时重新打开会话或重启 Codex。

### Claude Code：安装插件

在 **Claude Code 的对话输入框** 中依次发送，每次一行：

```text
/plugin marketplace add Rookiecoder-jsjs/empirical-research-skills
/plugin install empirical-research@rookiecoder-research
```

安装界面中：只用于这篇论文，选择项目范围；希望本机所有论文都能使用，选择用户范围。按客户端提示刷新插件或重新打开会话，然后输入：

```text
/empirical-research:empirical-workflow
```

一个插件包含全部8个技能，后续可以通过插件管理界面更新或卸载。不要再同时复制一份到 `.claude/skills/`，以免出现重复入口。插件安装无需 Python；如果客户端提示缺少 Git，可使用下面的 ZIP 方式。

### 下载后复制：两种工具都适用

GitHub 页面点击 **Code → Download ZIP** 并解压，把 `skills/` 内8个 `empirical-*` 文件夹完整复制到：

| 使用工具 | 只在当前论文中使用 | 在本机所有项目中使用 |
|---|---|---|
| Codex | 论文文件夹下的 `.agents/skills/` | 用户主目录下的 `.agents/skills/` |
| Claude Code | 论文文件夹下的 `.claude/skills/` | 用户主目录下的 `.claude/skills/` |

不存在的目录可以创建。复制完成的层级应为 `.agents/skills/empirical-setup/SKILL.md` 或 `.claude/skills/empirical-setup/SKILL.md`，不要多套一层 `skills/`。已有同名文件夹时停止，不直接覆盖。

[完整安装指南](docs/installation.md)包含两种工具的安装提示词、已有 Python 时的安装器、验证、更新、卸载及常见故障。

## 安装后的第一句话

> 我没有编程基础。请使用 empirical-setup 检查这篇论文的运行环境，按我的系统指导安装或复用 Python 和 uv，创建或复用当前项目的虚拟环境，并教我激活它。每一步说明在哪里操作、怎样判断成功；先不要跑研究模型。

安装 Skill 只说明助手获得了流程说明，**不代表研究环境已经搭好**。技能文件在多个项目中复用，分析依赖仍按每篇论文的环境单独维护。

## 首次准备研究项目

建议由助手运行 `empirical-project`，它会先识别既有项目。全新项目可用其自带工具预览，再显式创建：

```bash
python skills/empirical-project/scripts/init_project.py "/path/to/new-paper"
python skills/empirical-project/scripts/init_project.py "/path/to/new-paper" --create
```

默认目录：

```text
paper/
├── research-project.json       路径、Python版本与数据检查配置
├── workflow.json               有输入输出声明的运行步骤
├── requirements.txt            按本研究需要维护的分析依赖
├── data/                       用户提供的基础输入，分析阶段只读
├── processed/
│   ├── panels/                 主分析数据（不要求一定是面板）
│   ├── intermediate/           清洗和匹配中间产物
│   └── results/                表、图、模型、报告和运行记录
├── scripts/                    clean / analysis / figures / utils
├── literature/                 文献、笔记和核验台账
├── manuscript/                 正文及生成交付稿
└── experiments/                独立的探索主题工作区
```

**这些目录是缺省模板，不是必须迁移到的标准。** 支持横截面、面板、重复截面、实验及调查数据；按实际设计配置主键、时间、样本和处理定义。已有 `data/p_data/script/正文` 等结构可以原样保留。

## 环境路线

先检查现有安装 → 安装或复用uv → 安装指定Python → 创建或复用`.venv` → 激活 → 安装项目依赖 → 验证。Windows和macOS命令、每天重新打开项目的方法及失败恢复见[环境指南](skills/empirical-setup/references/environment-guide.md)。

Python版本由项目指定；新建模板以3.11作为示例起点，不自动追随最新版本。工具本身仅依赖Python 3.10+标准库。模型需要的包另按该项目配置，不能把本包工具通过检查理解为所有估计器已安装。

## 可执行工具

| 工具 | 行为 |
|---|---|
| `install_skills.py` | 安装技能，拒绝覆盖已有技能 |
| `init_project.py` | 默认预览，显式创建新项目，不覆盖既有目录 |
| `check_environment.py` | 检查环境归属、Python与指定包，只读输出JSON |
| `check_csv.py` | 检查CSV主键、必需字段、缺失和数值范围，只读输出JSON |
| `run_workflow.py` | 默认显示计划；显式执行，记录输入/代码/环境/输出摘要，按有效状态恢复 |

这些工具不内置“自动选出显著模型”。流水线执行的是项目维护者提供的命令，**不是沙箱**。使用前阅读清单中的命令及脚本；安全性不能仅靠输出声明保证。工具范围与命令见[运行协议](skills/empirical-analysis/references/execution.md)。

## 无研究数据的演示

`examples/synthetic-demo/`含明确标注的人工样例，仅验证运行工具，不支持任何学术结论。为保留仓库中的样例，可将该文件夹复制到临时位置，再在仓库根运行：

```bash
python skills/empirical-analysis/scripts/run_workflow.py --project examples/synthetic-demo --target summary
python skills/empirical-analysis/scripts/run_workflow.py --project examples/synthetic-demo --target summary --execute
python skills/empirical-analysis/scripts/run_workflow.py --project examples/synthetic-demo --target summary --execute --resume
```

演示生成文件位于样例的 `processed/results/`，默认忽略，不包含真实论文数据。

## 如何定义“完成”

- 每项结果可追溯到输入、脚本、规格和推断方法。
- 运行失败或缓存失效时，不把旧文件当成新结果。
- 正式证据、辅助诊断和探索结果分别解释。
- 文献确实支持相邻论断；引用规则来自目标论文，不固定重复次数。
- 数据、正文、Word/PDF生成与实际页面检查分别报告完成状态。
- 新手每一步知道要做什么、成功长什么样、错误时下一步是什么。

## 验证与边界

```bash
python scripts/validate_bundle.py
python -m unittest discover -s tests -v
```

CI配置在Windows、macOS、Linux上检查技能结构和工具行为；是否通过以仓库对应提交的运行结果为准。测试覆盖小型合成数据、缓存失效、失败恢复和文件边界，不代表真实模型识别正确或所有科学计算包跨平台兼容。

[场景验收清单](docs/acceptance.md)用于评估助手是否正确使用技能。技能不会替代研究者对识别假设、数据合法可用性、发表要求的判断。

## 贡献与许可

欢迎通过Issue描述具体失败场景，通过Pull Request提交范围明确的改进。不要提交真实研究数据、访问凭据、未公开稿件或个人路径。新增工具请补充行为测试，新增技能请保持资源随文件夹可搬移。

原创技能说明和工具采用[MIT许可证](LICENSE)。本仓库没有复制第三方技能正文或包含任何特定论文的数据、估计结果和手稿。
