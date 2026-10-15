# 进阶 B：系统失效诊断（样机排障）

接手一个文档查证样机（`challenge.py`，约 30 行，含预埋故障），按 `spec.md` 的公开行为契约找出「换资料版本却显示旧结论」这个主故障的最早出错位置，做最小修复，并验证原本正常的行为仍成立。

## 1 症状与复现（原始失败）

运行 `python run_cases.py --output runs/baseline.json`，R01→R02 顺序下复现：

| 案例 | 请求 | 期望 | 实际（基线） | 症状 |
|---|---|---|---|---|
| R01 | alpha / v1 / k2 | 30秒 / b01 | 30秒 / b01 | 正常 |
| **R02** | alpha / **v2** / k2 | **12秒 / b02** | **30秒 / b01**（cache_hit=True） | **换版本显示旧结论** |

R02 请求 v2 快照，却返回 v1 的「30秒」并引用 v1 段落 b01。这是「换了资料版本却显示旧结论」的干净复现。

## 2 两种容易被混淆的「正确」

1. **引用可定位（locator）vs 引用语义支撑（support）**（来自 ALCE 把正确性与引文支持分开评价）：引用 ID 在本次证据里（`locator=valid`）不等于这段原文支撑这个答案。样机把 `valid` 直接写成 `support_status=supported`（见 R04 症状），导致与原文矛盾的说法被标「已验证」。
2. **缓存命中（cache_hit）vs 缓存不污染**：`cache_hit=True` 只说明「这次复用了缓存」，不说明「复用的是不是这个请求该有的结果」。R02 的 `cache_hit=True` 反而正是污染发生的标志。
3. **资料快照一致 vs 页面显示对应**：返回体里 `request` 字段被更新成当前请求（v2），但 `evidence` 仍是旧快照（v1）——「请求字段对」与「数据对」是两回事。

这些混淆为什么伤害用户任务：用户查 v2 版本的超时阈值做配置决策，却拿到 v1 的 30秒，会据此误配置；R04 把与原文矛盾的「保证 GPU 释放」标成 supported，会让用户误以为该说法已被原文核实。这不止是「违反最佳实践」，而是直接给出错误结论（spec 第 1/3/5 条）。

## 3 两个原因：先预测，再干预

对「R02 请求 v2 却返回 30秒/b01」这个症状，两个仍与证据相容的解释：

| 解释 | 内容 | 可观察预测 |
|---|---|---|
| **解释 1（缓存复用错误）** | 缓存键只用 `query`，未含 doc_ids/snapshot/k，跨版本命中旧缓存 | R02 `cache_hit=True` 且 evidence 是 v1 段落 b01；**单独 fresh 跑 R02 会返回 12秒/b02** |
| **解释 2（检索/过滤错误）** | snapshot 过滤失效，v1 段落被错误纳入本次检索 | **单独 fresh 跑 R02 仍返回 30秒/b01** |

区分性干预（`diagnose.py`）：单独 fresh 跑 R02 → 返回 **12秒/b02**。支持解释 1、排除解释 2。两个解释的作用范围不重叠：解释 1 只解释 R02 错答；R03 的漏证据是另一处（先截断后过滤）的独立根因，不属于解释 2 在此症状上的作用。

## 4 最早出错边界

源码定位在 `challenge.py:12`：

```python
key = request['query'].strip().lower()   # 缓存键只由 query 决定
hit = key in self.cache
```

R01 用 key=`"timeout request threshold"` 缓存了 v1 结果；R02 同 query、不同 snapshot v2，`hit=True` 直接复用旧结果。最早出错边界就是**缓存键的构造**，之后的检索/排序/过滤根本没被执行。

**反向因果/评价错误检查**：R02 的 `elapsed_ms` 比 R01 低约 66%（0.016ms vs 0.048ms），乍看像「系统变快」；实为 `cache_hit=True` 跳过了检索计算，只做了 `deepcopy+update`。更低耗时来自「错误命中旧缓存」，不是真实加速（spec 第 6 条：耗时只表示样机运行）。

## 5 最小修复与舍弃的替代

**修复**（`fixed.py`）：缓存键由 query 扩展为「query + doc_ids(排序归一) + snapshot + k」：

```python
return (
    request['query'].strip().lower(),
    tuple(sorted(request['doc_ids'])),
    request['snapshot'],
    request['k'],
)
```

doc_ids 排序归一，使「同一组文档、不同书写顺序」仍命中同一缓存（不破坏 spec 第 2 条「允许查询多个文档」的语义等价）。**只改这一处**，不动检索与 support_status。

**舍弃的替代**：给每个结果加「版本时间戳」判过期——被否，因为静态 fixture 没有时间语义，且会引入「何时算过期」的不确定性；把缓存键粒度定为「请求语义」更直接、可验证。另一个被舍弃的替代是「干脆关闭缓存」——被否，因为 spec 第 5 条允许保留缓存，关闭会丢弃「等价输入复用」这一本应正常的能力，属于回避而非修复。

## 6 回归、变体与边界（`verify_fixed.py`，6/6 通过）

| 项 | 内容 | 预期依据 | 结果 |
|---|---|---|---|
| 原始失败修复 | R01→R02 下 R02 返回 12秒/b02 | spec 1/3/5 | PASS |
| 回归 1 | R05 metadata beta 仍 b05/valid | spec 2/3 | PASS |
| 回归 2 | R06 worker single process 仍 b06/valid | spec 2/3 | PASS |
| 变体 1（标识重映射） | id/doc_id/snapshot 统一加前缀 X，语义不变 | 修复不依赖具体字符串 | PASS |
| 变体 2（顺序） | corpus 逆序，结果不变 | 排序按 tags+id，与输入顺序无关 | PASS |
| 自构边界 | 资料文本修订后同请求仍命中旧缓存 | spec 5 | 复现（未解决） |

变体 1 同时覆盖「标识」与「资料版本」两项（doc_id 与 snapshot 都重映射），变体 2 覆盖「顺序」；满足「至少涉及顺序/标识/资料版本中的一项」。

## 7 另外两个症状的风险登记（不在本次修复范围）

- **先截断后过滤（R03 漏证据）**：`ranked[:k]` 先按全局排序截断、再按 doc_id/snapshot 过滤，导致 scope 外条目抢占名额，R03 应返回 b03 却 evidence=[]（spec 第 2 条「scope 内有匹配时不能因 scope 外条目丢名额」）。风险：多文档查询时漏掉应返回的证据。
- **support_status 把「ID 有效」当「语义支持」（R04 造假）**：`support_status='supported' if valid`，R04 答案「保证 GPU 释放」与 b04 原文「未测量是否释放」矛盾，却被标 supported（spec 第 4 条「只有 ID 有效不足以 supported」）。风险：页面把未核验语义标成已验证。

## 8 一段话总结

我**证明**了「换版本显示旧结论」的最早出错边界是 `challenge.py:12` 的缓存键只用 `query`——用区分性干预（单独 fresh 跑 R02 正确返回 12秒/b02）排除了「检索/过滤另有 bug」的竞争解释，并确认 R02 的「低耗时」是命中旧缓存的反向因果假象。我**只是观察到** R03 漏证据与 R04 support 造假是另外两个独立 bug，尚未修，已登记风险。我**还不知道**缓存键不含资料内容/版本 hash 时，资料更新后同请求仍会命中旧缓存（自构边界已复现未解决）；单进程演示下缓存一致性、多用户/多worker并发、逻辑取消与真正释放推理资源都未测。

## 9 未来验证方案（不要求这周做分布式）

- **需加的日志/状态字段**：`corpus_version`（资料 hash）、`cache_key`、`request_id`、`cache_hit`、`source_snapshot`，并区分「缓存命中」「排队」「逻辑取消」「真正释放推理资源」。
- **会失效的假设**：当前假设「cache 是单进程内 dict、无并发」。多用户/多worker 下：进程内 cache 不跨进程共享，各 worker 缓存不一致；并发同时 miss 同一 key 会重复计算；「逻辑取消」不必然停止计算/释放资源。
- **可执行验证方案与停止条件**：在缓存键加入资料版本 hash 后，构造「同请求 + 资料修订」回归（预期返回新资料、不再命中旧缓存），停止条件 = 该回归 0 次错版返回；并发下统计同 key 的重复 miss 次数，停止条件 = 并发 miss 数收敛到 1。

## 10 启动与复算命令（全部离线，不花 API）

```bash
cd 进阶/challenge_b
python run_cases.py --output runs/baseline.json      # 原样机基线（复现故障）
python diagnose.py                                    # 区分性干预：证明根因
python verify_fixed.py                                # 修复 + 回归 + 变体 + 边界（6/6）
python run_cases.py --engine fixed:Engine --output runs/fixed.json   # 修复版复跑全部案例
python server.py --port 8766                          # 页面（baseline + fixed 双引擎对比）
```
