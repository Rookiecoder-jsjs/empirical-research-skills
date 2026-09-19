# 按依赖运行和记录

## workflow.json格式

清单位于项目根目录，schema版本为1。示例：

```json
{
  "schema_version": 1,
  "raw_paths": ["data"],
  "state_dir": "processed/results",
  "steps": [
    {
      "id": "summary",
      "command": ["{python}", "scripts/summarize.py"],
      "inputs": ["data/synthetic.csv"],
      "code": ["scripts/summarize.py"],
      "outputs": ["processed/results/summary.json"],
      "depends_on": [],
      "role": "descriptive"
    }
  ]
}
```

每步使用显式文件列表，不支持glob或目录输入。`{python}`作为独立命令参数时替换为启动执行器的解释器；应使用项目环境启动。其他参数原样传递，命令工作目录固定为项目根目录。无shell展开，命令中不要放`&&`、重定向或依赖shell的变量。

`code`必须声明脚本及相关共享代码；执行器不自动分析动态导入。某步读取另一任务的输出，必须把生产者列为其直接或间接依赖。新模型参数写在命令参数或声明为input/code的配置文件中。

## 使用

```text
python <skill-folder>/scripts/run_workflow.py --project <project> --target summary
python <skill-folder>/scripts/run_workflow.py --project <project> --target summary --execute
python <skill-folder>/scripts/run_workflow.py --project <project> --target summary --execute --resume
```

不提供target时规划全部步骤。`--manifest`可指定项目内另一份清单。默认规划不写文件、不安装依赖、不执行命令；允许新项目空步骤清单。

`--execute`按依赖串行执行。`--resume`仅跳过状态记录有效且输入/代码/环境/输出摘要都匹配的步骤。记录使用Python版本、平台、已装发行包版本，以及该步骤与依赖指纹。随机参数、使用外部程序的版本、环境变量和外部数据版本需由项目另行显式记录；工具无法自动捕捉这些隐含依赖。

## 安全与局限

执行器拒绝逃出项目根的声明路径、声明到raw_paths下的输出、相互覆盖的输出、未知依赖和循环。输入和代码文件本身可来自只读原始目录。

**这不是文件系统沙箱。** Python脚本、外部命令或未声明缓存仍可能写其他位置；助手必须在执行前阅读实际命令与脚本。原始数据只读与探索隔离需要调用方遵守，不由清单声明自动保证。

把已有脚本接入前检查硬编码输出、导入副作用和缓存。没有声明的变化可能漏检；只在版本来源可靠时使用恢复功能。它不锁进程，不支持并发运行同一项目，不捕捉远端数据库快照，也不提供整条流水线回滚。

## 失败和过期

开始每步前先写running状态以使旧成功记录失效；非零退出或缺失输出记为failed，立即停止。失败步骤留下的部分CSV不能作为本次有效结果。再次运行可重跑失败步，其他步骤仅在有效验证后跳过。

状态记录、每次运行报告和日志写入state_dir，保留最近每步状态与逐次run文件。不要把终端日志当成权威数值来源。输出内容改变、输入改变、代码改变均会使恢复失效。

显式执行时每个声明的输出必须重新写出。执行器比较文件摘要与修改元数据，发现旧输出未刷新时记为失败；粗粒度或异常文件系统上可能保守地拒绝一次有效重写，应调查后再继续，不能关闭检查混用旧产物。脚本自带缓存若直接跳过写出，应先验证并在适配层处理，或使用执行器自身的有效恢复模式。

脚本成功不代表科学结论成立。执行后仍需核验样本、模型、单位、推断、图表以及正文角色。
