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

## 安装技能

先下载本仓库的 ZIP 并解压，或使用 Git：

```bash
git clone https://github.com/Rookiecoder-jsjs/empirical-research-skills.git
```

**还没有Python时：** 不需要先运行安装脚本。打开 `skills/empirical-setup/SKILL.md` 给助手阅读，或先看[环境指南](skills/empirical-setup/references/environment-guide.md)。也可把 `skills/` 内8个文件夹手动复制到你的论文项目的 `.agents/skills/`。复制整个文件夹，保留其内部资源。

**已有Python时：** 在下载的仓库根目录运行，替换成实际论文项目路径：

```bash
python scripts/install_skills.py --project "/path/to/your/paper"
```

默认安装到目标项目的 `.agents/skills/`。若使用其他支持本格式的工具，可以指定其技能目录：

```bash
python scripts/install_skills.py --destination "/path/to/your/paper/.claude/skills"
```

安装器先检查冲突，拒绝覆盖任何已有同名技能；不会修改其他技能、项目数据或全局配置。不同客户端的技能发现机制不同，复制后重新打开项目或按该客户端说明刷新；本包不保证所有客户端自动加载。

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
