# 目录与可变配置

## 默认布局

`data/`是基础输入；`processed/panels/`是最终分析数据；`processed/intermediate/`是中间产物；`processed/results/`是表、图、模型和报告。横截面也可以使用panels位置或改名为analysis-data，目录名不决定数据结构。

脚本按功能放入`scripts/clean/`、`scripts/analysis/`、`scripts/figures/`和`scripts/utils/`。纯绘图与重新估计分开。文献放`literature/`，正文放`manuscript/`，探索放`experiments/<topic>/`。

目录保持便于理解的浅层结构；已有LaTeX工程和软件包内部目录不为满足形式被拆散。原始文件保留名称，产物用稳定ID与描述性前缀。论文展示的表号与文件稳定标识分开维护。

## research-project.json

初始化工具生成以下配置：

- `schema_version`：目前为1。
- `project_title`：待研究者填写，可为空。
- `python_version`：模板默认3.11，按实际环境和依赖选定后更新。
- `paths`：输入、分析数据、中间数据、结果、脚本、文献、正文、探索的位置。
- `data_contract`：`unit`、`time`、`keys`、`required`、`missing_values`；未知时为空，不推断研究设定。
- `research_design`：`question`、`estimand`、`method`、`assumptions`，由研究设计补充。

这些字段是初始化模板和人工/助手配置契约；CSV检查器目前使用显式命令行参数，不会自动读取全部配置。执行器使用的是独立`workflow.json`，不得声称所有配置已自动联动。

## 移动或归档

先找调用关系，再按用户要求调整路径并更新读写方。不要根据修改时间认定结果权威，不清空全部处理目录来“开始复现”。历史审计可保留但标记角色与有效性。

每项输出能回答：谁提供输入、哪个脚本生成、用了什么参数、在哪里被论文引用、能否重新生成。数值写入由脚本完成，规则和数据字典可以维护为文档。
