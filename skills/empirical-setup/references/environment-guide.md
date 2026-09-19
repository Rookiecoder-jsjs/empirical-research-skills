# 新手环境指南

本指南使用Python与uv，分别介绍首次配置和日常启动。命令参考官方文档；每个研究项目的包版本与平台兼容性仍需实际验证。能由助手执行的检查不要求新手重复操作。

## 1. 先打开项目

Windows：开始菜单搜索PowerShell，打开后输入以下示例，把双引号内路径换成你的项目：

```powershell
Set-Location "D:\研究项目\my-paper"
Get-Location
```

macOS：按Command＋空格搜索“终端”，输入：

```bash
cd "/Users/你的用户名/研究项目/my-paper"
pwd
```

应显示论文项目的路径。一次复制一段并等待完成，不混用不同终端语法。助手能检测路径时提供已填好的真实命令。

## 2. 检查与安装uv

先运行`uv --version`，显示版本号就跳过安装。uv是安装Python及分析工具包的管理器；无需先安装Python才能安装uv。[官方安装文档](https://docs.astral.sh/uv/getting-started/installation/)

Windows PowerShell：

```powershell
winget install --id=astral-sh.uv -e
```

没有winget时，官方独立安装方式为：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS终端：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

独立安装命令会下载并执行官方程序。完成后重开终端、重新进入项目，再检查`uv --version`。不要在版本检查失败时继续后续命令。

## 3. 选择Python并创建环境

先查项目文档、`research-project.json`、`.python-version`、依赖配置等已有约定。**下方3.11仅是示例，助手要替换为本研究已确认的版本。** 已有兼容的Python和项目环境则复用。

```text
uv python install 3.11
uv python find 3.11
```

第二行应返回解释器位置。uv支持安装指定版本和使用现有Python。[Python管理说明](https://docs.astral.sh/uv/guides/install-python/)

先检查`.venv`是否存在：Windows用`Test-Path .\.venv`，macOS用`ls -d .venv`。若存在，先检查其解释器，不覆盖。**仅在不存在时创建：**

```text
uv venv --python 3.11 .venv
```

`.venv`保存本项目独立的Python入口和工具包。它不应被当作跨电脑、跨操作系统的可移植副本；迁移时带上代码和依赖记录，在新机器重建。[Python环境说明](https://docs.python.org/3/library/venv.html)

## 4. 激活当前终端

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS终端：

```bash
source .venv/bin/activate
```

然后运行：

```text
python --version
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

版本应符合项目要求，输出路径应在当前项目的`.venv`内。不要只根据提示符的括号判断。[uv环境使用说明](https://docs.astral.sh/uv/pip/environments/)

如果PowerShell禁止激活脚本，可以在“命令提示符”（CMD）中进入项目并使用对应脚本，无需默认全局放宽安全策略：

```bat
cd /d "D:\研究项目\my-paper"
.venv\Scripts\activate.bat
python -c "import sys; print(sys.executable)"
```

后续留在该CMD窗口。路径仍需换成实际位置。[Python激活脚本说明](https://docs.python.org/3/library/venv.html)

## 5. 安装研究所需依赖

采用已有的依赖管理方式。若项目使用`requirements.txt`，先确认其内容确实适用于该Python版本；空的模板清单不表示任何分析包已安装。

Windows：

```text
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
uv pip check --python .venv\Scripts\python.exe
```

macOS：

```bash
uv pip install --python .venv/bin/python -r requirements.txt
uv pip check --python .venv/bin/python
```

分别完成安装与兼容性检查。项目没有依赖清单时，助手根据任务只加入所需包，并在实际验证后记录版本，不为“通用”安装全部统计生态。[依赖文件安装](https://docs.astral.sh/uv/pip/packages/)、[环境检查](https://docs.astral.sh/uv/pip/inspection/)

已有`pyproject.toml`与锁文件的项目继续用其既定同步方式；不额外混入另一套手工安装流程。R、Stata、TeX和文档转换工具只在相应任务需要时准备。

## 6. 验收与日常启动

助手用本技能的`check_environment.py`检查环境归属和所需包，并运行实际任务需要的最小合成数据计算。报告解释器、版本、包检查与还缺哪些能力。只读环境工具不安装软件、不读取研究数据。

以后每次打开新终端通常只需要：进入项目 → 激活 → 核对解释器。无需每天重装软件。激活只对当前终端有效；代理独立进程应直接用项目解释器路径。[激活范围说明](https://docs.python.org/3/library/venv.html)

## 7. 遇到问题

| 症状 | 优先处理 |
|---|---|
| 找不到uv | 重开终端，再核对安装位置与PATH |
| 找不到Python | 查安装是否成功，再创建与激活项目环境 |
| 找不到依赖文件 | 确认当前是项目根目录 |
| 激活了环境仍缺包 | 核对`sys.executable`与安装目标是否一致 |
| 复制来的环境不能运行 | 保留旧环境，在当前机器重建 |
| 包版本不存在或冲突 | 保留清单和报错，核对Python、平台和来源；不要静默取消版本约束 |
| 网络或证书错误 | 检查网络或管理要求，不关闭证书校验 |
| 分析能跑但Word/PDF失败 | 单独检查文档工具、字体和模板，不能宣称全环境已就绪 |

每次报错先解释当前原因和一个可执行下一步，避免让新手在多种包管理工具之间反复尝试。
