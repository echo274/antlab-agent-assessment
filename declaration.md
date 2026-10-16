# AI、贡献与真实性声明

- **真实 API 模型名称**：DeepSeek —— 主实验/开发调试用 `deepseek-chat`（API 响应 `model` 字段为 `deepseek-flash`）；诊断对照用 `deepseek-reasoner`（4 次）；另试 `deepseek-pro`（1 次，HTTP 400 失败，未计入结果）。
- **Token 消耗量级**：约 10.3 万（103,488 tokens：`deepseek-chat` 59 次 93,389 + `deepseek-reasoner` 4 次 10,099；另有 `deepseek-pro` 1 次因 HTTP 400 失败、无 usage）。
- **AI 工具与主要用途**：Claude Code（Claude）。用于：阅读任务说明与题包、实现 `student.py`（提示词设计与 improve 重排）、编写判分脚本（`score.py`）与检查脚本（`checks.py`）、撰写 `report.md`/`decisions.md`/README、进阶 B 源码审查与故障归因、编写修复（`fixed.py`）/区分干预（`diagnose.py`）/验证（`verify_fixed.py`）脚本、Git 操作与实验命令执行。
- **本人核验并承担的关键判断及核验方法**：
  1. 判分 ground truth（T01–T08 的规则应用与算术）由本人逐题读 `cases.json` 原文确定，依据写在 `results/scoring/ground_truth.md`；
  2. 抽查 D01 首次真实调用，确认输入 messages、原始响应与答案「80%」一致，可追溯到 `runs/` 记录；
  3. 核对了 40 次主实验无技术失败/格式错误/引用越界（`results.csv` 的 `cite_valid` 列）；
  4. 逐条读 `cases.json` 原文，核验 40 次主实验的「引用语义支撑」（cite_support：supported 26 / contradicted 13 / insufficient 1），规则与逐题依据见 `results/scoring/ground_truth.md`；
  5. 进阶 B：读 `challenge.py` 源码与 `spec.md`，确认缓存键只在 `query` 是 R02 返回旧版本的最早出错边界；单独跑 R02（`diagnose.py`）确认返回 12秒/b02，排除「过滤 bug」的竞争解释；跑 `verify_fixed.py` 确认 6/6 通过。
- **未实现、未运行或未验证的内容**：
  1. 进阶 B 只修主故障（缓存键粒度）；另两个症状 R03「先截断后过滤」、R04「support_status 把 ID 有效当语义支持」登记为风险、未修；
  2. 自构边界「资料更新后同请求仍命中旧缓存」已复现、未解决（缓存键不含资料版本 hash）；
  3. 改进（内容重排）未带来准确率提升，T07 改进版反而答错，如实报告未改善。

我确认没有把模拟输出、预测或 AI 编造数据当真实运行；没有隐瞒会改变结论的失败、调参、重试或标签使用。复用代码、第三方资料或他人帮助在报告/源码中注明；提交包已检查无 API 密钥、Endpoint 和私人账号信息（密钥仅存于本机环境变量与未提交的 `config.local.json`）。

姓名/日期：赵博然 / 2026-10-15
