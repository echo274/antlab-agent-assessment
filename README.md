# ANTLab Agent Tasks — 文档阅读与信息核验

应用层开发者招募考核作品。**所选方向：基础（必做）+ 进阶 B（系统失效诊断）**。

- **最终分支**：`main`
- **最终 commit SHA**：`aa8940206991b8957df97b52896f9cf96abc2efa`（代码与报告内容定稿；本行标注为最后一次 commit）
- **真实模型**：DeepSeek（配置 `deepseek-chat`，API 响应字段为 `deepseek-flash`）

## 目录

- `基础/` 基础题：12 题（4 开发 + 8 评测），证据核验方案实现见 `基础/starter/student.py`
- `进阶/challenge_b/` 进阶 B：样机排障（`challenge.py` 基线、`fixed.py` 修复、`diagnose.py` 区分干预、`verify_fixed.py` 回归+变体、`README.md` 排障记录）
- `results/` 逐例结果与判分（`results/results.csv`、`results/scoring/`、`results/checks/`）
- `runs/`（见 `基础/runs/`、`进阶/challenge_b/runs/`）原始运行记录
- `report.md` / `decisions.md` / `declaration.md` 整合报告、决定、AI 声明

## 启动与运行

```bash
# 1) 配置（密钥放环境变量，不提交）：复制 config.example.json -> config.local.json，填入 endpoint/model
export ASSESSMENT_API_KEY='你的key'   # 或设为 Windows 用户环境变量

# 2) 预览输入（不调用模型，不花钱）
python 基础/starter/runner.py --case D01 --condition E --dry-run --config 基础/config.local.json

# 3) 真实调用（付费，会扣模型额度）
python 基础/starter/runner.py --split evaluation --condition all --limit 32 --paid --config 基础/config.local.json
python 基础/starter/runner.py --split evaluation --condition R0 --variant improved --limit 8 --paid --config 基础/config.local.json

# 4) 前端预览（可选）
python 基础/starter/server.py --config 基础/config.local.json
```

## 判分与复算（不消费 API 额度）

```bash
python results/scoring/score.py          # 由 runs/ 离线复算，生成 results/results.csv
python results/checks/checks.py          # 诊断 + 变体检查（不调模型）
```

判分口径与人工 ground truth 见 `results/scoring/ground_truth.md`；评测题无公开答案，答案由本人读原文确定。

进阶 B（离线，不花 API）：

```bash
cd 进阶/challenge_b
python run_cases.py --output runs/baseline.json   # 原样机基线（复现故障）
python diagnose.py                                # 区分性干预：证明缓存键根因
python verify_fixed.py                            # 修复 + 回归 + 变体 + 边界（6/6）
python server.py --port 8766                      # 页面（baseline + fixed 双引擎对比）
```

## 完成 / 未完成

| 要求 | 状态 | 说明 |
|---|---|---|
| 基础题实现 `student.py` | ✅ | `prepare_messages` + `improve`（内容相关性重排） |
| 40 次主实验（32 基线 + 8 改进） | ✅ | 全部 `ok`，无技术失败/格式错误/引用越界 |
| 逐题判分 + results.csv | ✅ | 基线 23/32，改进 4/8（见报告） |
| 一次诊断 | ✅ | T01/T08 答「证据不足」归因为「未套用规则」推理失败 |
| 一次变体（ID 重映射） | ✅ | improve 只依赖内容、不依赖 ID |
| 三项决定 | ✅ | 见 decisions.md |
| 引用语义支撑（cite_support） | ✅ | 逐条读原文核验：supported 26 / contradicted 13 / insufficient 1 |
| 进阶 B：主故障修复 | ✅ | 缓存键粒度修复 + 回归/变体/边界；另两个症状(R03/R04)登记未修 |

## 来源与声明

- 题包骨架复用 ANTLab Agent Tasks 基础题 starter（`基础/starter/`），`student.py` 为本人实现。
- AI 使用声明见 `declaration.md`；密钥、Endpoint 未提交。
