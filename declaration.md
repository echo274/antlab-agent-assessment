# AI、贡献与真实性声明

> 以下为草稿，请候选人复核并补全「本人核验」与署名后提交。

- **真实 API 模型名称**：DeepSeek（配置 `deepseek-chat`；API 响应 `model` 字段为 `deepseek-flash`）。
- **Token 消耗量级**：< 10 万（实测 57 次付费调用，共 89,523 tokens：88,284 prompt + 1,239 completion）。
- **AI 工具与主要用途**：Claude Code（Claude）。用于：阅读任务说明与题包、实现 `student.py`（提示词设计与 improve 重排）、编写判分脚本（`score.py`）与检查脚本（`checks.py`）、撰写 `report.md`/`decisions.md`/README、Git 操作与实验命令执行。
- **本人核验并承担的关键判断及核验方法**：
  1. 判分 ground truth（T01–T08 的规则应用与算术）由本人逐题读 `cases.json` 原文确定，依据写在 `results/scoring/ground_truth.md`；
  2. 抽查 D01 首次真实调用，确认输入 messages、原始响应与答案「80%」一致，可追溯到 `runs/` 记录；
  3. 核对了 40 次主实验无技术失败/格式错误/引用越界（`results.csv` 的 `cite_valid` 列）。
  （以上由候选人确认后填写实际核验范围。）
- **未实现、未运行或未验证的内容**：
  1. 进阶 B（系统失效诊断）未开始；
  2. 引用「语义支撑」（cite_support）尚未逐条人工核验，脚本标注为 `not_checked`；
  3. 改进（内容重排）未带来准确率提升，T07 改进版反而答错，如实报告未改善。

我确认没有把模拟输出、预测或 AI 编造数据当真实运行；没有隐瞒会改变结论的失败、调参、重试或标签使用。复用代码、第三方资料或他人帮助在报告/源码中注明；提交包已检查无 API 密钥、Endpoint 和私人账号信息（密钥仅存于本机环境变量与未提交的 `config.local.json`）。

姓名/日期：________
