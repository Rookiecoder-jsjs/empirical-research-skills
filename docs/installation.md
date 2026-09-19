# 安装与首次使用

只需选择与你使用的客户端对应的路线。这里的 Claude Code 指可操作本地项目的 Claude Code；普通网页聊天上传文件不是同一种安装方式。

## 1. 先决定安装范围

- **项目级（推荐第一次使用）**：只在当前论文中发现技能，便于核对和随项目交接。
- **用户级**：本机当前用户的多个项目都能使用技能；每篇论文仍维护自己的 `.venv` 和依赖。

不需要两种范围都装。同一客户端不要同时安装插件版和文件夹版。

## 2. Codex

在 Codex 打开论文文件夹，复制 [README 的安装提示词](../README.md#codex复制一句话)。项目级复制的目标是 `.agents/skills/`；若明确需要用户级，把提示词中的“当前论文项目”改成“用户主目录”。

如果使用 Codex 内置的 skill-installer，必须传入真实分支：本仓库当前默认分支是 `codex/initial-release`，不是 `main`。最好先查询默认分支；固定版本时可使用明确的提交或标签。全部8个源路径是：

```text
skills/empirical-workflow
skills/empirical-setup
skills/empirical-project
skills/empirical-data
skills/empirical-analysis
skills/empirical-explore
skills/empirical-writing
skills/empirical-audit
```

请让助手检查实际安装位置。不同版本的内置安装器可能采用其自己的用户技能目录；已经在那里正常使用时，不要重复复制到另一个目录。本仓库安装器按当前官方文档采用 `.agents/skills/`。

## 3. Claude Code

推荐通过 [README 的两条插件命令](../README.md#claude-code安装插件)安装。插件名是 `empirical-research`，自托管市场名是 `rookiecoder-research`；并不表示本包已上架官方市场。

更喜欢和 Codex 一样对话安装时，可以发送：

> 请从 https://github.com/Rookiecoder-jsjs/empirical-research-skills 的默认分支下载 skills/ 下的全部8个技能，完整复制到当前论文项目的 .claude/skills/。先检查是否已经安装 empirical-research 插件或同名技能，已安装时不要再复制；发现同名文件不要覆盖，说明现状。无需先安装 Python；没有 Git 时可以下载 ZIP。完成后核对目录、资源文件和客户端能否发现技能。

这条提示词安装的是文件夹版，调用方式是 `/empirical-workflow`；插件版是 `/empirical-research:empirical-workflow`。两者使用同一套技能内容。

## 4. 无需 Python 的手动安装

1. GitHub 仓库页面点击 **Code → Download ZIP**，解压。
2. 找到你的论文文件夹。如果还没有，先创建一个空文件夹，再在客户端打开。
3. 依照 [README 的目录表](../README.md#下载后复制两种工具都适用)，创建 `.agents/skills/` 或 `.claude/skills/`。点开头的文件夹可能被系统隐藏；也可让助手完成创建和复制。
4. 复制 `skills/` 中完整的8个 `empirical-*` 目录。不要只复制 `SKILL.md`，内部脚本与参考资料也要保留。
5. 核对示例路径：`论文文件夹/.claude/skills/empirical-setup/references/environment-guide.md`（Codex 将 `.claude` 换成 `.agents`）。
6. 回到论文项目的客户端会话，检查技能入口。

首次需要联网下载；下载完成后的复制无需联网。公共仓库 ZIP 下载不要求 GitHub 账号。网络受限时可由他人转交完整 ZIP，再本地复制。

## 5. 已有 Python：明确选择客户端的安装器

以下命令在**下载并解压的技能仓库根目录**中运行。把示例路径替换为实际且已存在的论文文件夹。Windows 通常使用 `py` 或 `python`，macOS/Linux 通常使用 `python3`；工具需要 Python 3.10+。

```bash
# 只给当前论文安装 Codex 技能
python scripts/install_skills.py --client codex --project "/path/to/paper"

# 只给当前论文安装 Claude Code 技能
python scripts/install_skills.py --client claude --project "/path/to/paper"

# 同一篇论文同时使用两个客户端
python scripts/install_skills.py --client both --project "/path/to/paper"

# 预览两个目标目录，不写入文件
python scripts/install_skills.py --client both --project "/path/to/paper" --dry-run

# Codex：本机当前用户的所有项目
python scripts/install_skills.py --client codex --global

# Claude Code：本机当前用户的所有项目
python scripts/install_skills.py --client claude --global
```

旧命令 `--project` 不加 `--client` 时仍默认 Codex。特殊客户端可以用 `--destination "实际技能目录"`，不能同时加 `--client`。Windows 路径示例为 `"C:\Users\your-name\Documents\my-paper"`。

安装器在复制前统一检查所有目标中的同名冲突，任何冲突都会停止；不会覆盖你的定制。它只复制技能，不安装 Python/uv，不修改论文或 Git 提交，也不会识别 Claude 的已安装插件列表，使用前请自行查看。磁盘写入中途失败可能留下部分文件，请核对错误所列位置后处理，勿误删其他技能。

## 6. 怎样确认安装成功

分两步验收：

1. **文件完整**：目录中有8个技能，各有 `SKILL.md`，脚本、参考资料和 `agents/` 随目录复制。`agents/openai.yaml` 是 Codex 的界面信息，可保留在 Claude Code 安装副本中。
2. **客户端识别**：Codex 在技能选择器中找到 `empirical-workflow`，可用 `$empirical-workflow`；Claude Code 文件夹版用 `/empirical-workflow`，插件版用 `/empirical-research:empirical-workflow`。未出现时重新打开会话；Codex 仍未发现时重启客户端。

不要仅凭助手说“我可以帮你分析”判断安装成功，应核对实际入口或已加载的技能来源。

首次使用先运行 `empirical-setup` 检查环境。Python、uv、`.venv` 激活和项目依赖说明见 [环境指南](../skills/empirical-setup/references/environment-guide.md)。只写论文文字时，不强制安装分析依赖。

## 7. 更新与卸载

**Claude Code 插件版**：在 `/plugin` 管理界面刷新 `rookiecoder-research` 市场，再更新或卸载 `empirical-research`。更新后按提示刷新或重开会话。维护者每次发布插件更新都应递增 `.claude-plugin/plugin.json` 中的版本号。

**文件夹版（含本仓库安装器）**：不会自动更新。下载新版后，让助手先比较已安装副本与新版；若有定制，把旧的8个目录备份到技能扫描目录之外，再由你选择保留或合并。确认备份后移走旧目录，再安装新版。不要把备份留在 `.agents/skills/` 或 `.claude/skills/` 中，以免被再次识别。

卸载时只移除本包的8个 `empirical-*` 目录，保留其他技能、论文、数据和研究环境。若本来就有同名定制技能，先核对归属。复制版、插件版只需保留一种即可，切换前先确认新入口正常。

## 8. 常见问题

| 现象 | 处理 |
|---|---|
| 没有 Python、uv 或 Node.js | 先使用插件安装或 ZIP 复制；安装技能本身无需这些环境 |
| 插件安装提示 Git 不存在 | 使用 ZIP 复制，或按客户端指引准备 Git；不必为了复制安装 Python |
| Codex 下载报 main 分支不存在 | 查询实际默认分支；本仓库当前为 `codex/initial-release` |
| 找不到技能 | 检查是否在论文项目中打开客户端，以及是否多套了 `skills/`；重新打开会话 |
| 出现两组同名入口 | 检查用户级、项目级和插件版是否重复安装，保留需要的一份 |
| 提示拒绝覆盖 | 保留现有版本，先比较和备份，再决定是否升级 |
| `python` 找不到 | 没有 Python 就走 ZIP；已安装时尝试对应系统的 `py` 或 `python3` |
| 用户级技能在另一台电脑不可用 | 用户级安装只属于当前电脑；新电脑另行安装 |
| 组织策略禁止插件或本地技能 | 按管理员允许的方式安装；不要绕过组织限制 |

## 官方依据与验证边界

目录和调用方式依据 [Codex Skills 文档](https://developers.openai.com/codex/skills/)、[Claude Code Skills 文档](https://code.claude.com/docs/en/skills) 与 [Claude Code 插件分发文档](https://code.claude.com/docs/en/plugin-marketplaces)。客户端版本和组织设置可能影响界面。

仓库测试覆盖安装路径、双客户端复制、资源完整性、冲突保护及预览不写入；Claude 插件配置可用 `claude plugin validate` 校验。配置通过不等于每个客户端版本均完成实际安装验收，应以上面的两步验收为准。
