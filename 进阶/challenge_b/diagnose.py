"""主故障（缓存污染）的区分性干预：证明 R02 返回旧版本是「缓存键粒度不足」而非「检索/过滤另有 bug」。

症状：R01(alpha/v1) 后紧接 R02(alpha/v2)，R02 却返回 30秒/b01（v1 结论）。
两个仍与证据相容的解释：
  解释1 缓存复用错误：缓存键只用 query，跨版本/文档复用了旧结果。
         预测：R02 cache_hit=True，且其 evidence 是 v1 段落 b01；单独(fresh)跑 R02 会返回 12秒/b02。
  解释2 检索/过滤 bug：即使无缓存，snapshot 过滤失效导致 v1 段落混入。
         预测：单独(fresh)跑 R02 仍返回 30秒/b01。
区分性干预：分别 (A) 顺序跑 R01→R02（复现），(B) 单独 fresh 跑 R02（干预）。
另检查反向因果：R02 更低的 elapsed_ms 是否来自「命中旧缓存」而非「系统变快」。
"""
import json
from pathlib import Path
from challenge import Engine

ROOT = Path(__file__).parent
data = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
corpus = data['corpus']
by_id = {c['id']: c for c in data['cases']}
r01, r02 = by_id['R01'], by_id['R02']

print('== (A) 顺序跑 R01 → R02（复现缓存污染）==')
e = Engine()
o1 = e.evaluate(r01['request'], corpus, r01['draft'])
o2 = e.evaluate(r02['request'], corpus, r02['draft'])
print(f"R01: cache_hit={o1['cache_hit']} answer={o1['answer']} cites={o1['citations']} "
      f"evidence={[b['id'] for b in o1['evidence']]} elapsed_ms={o1['elapsed_ms']:.3f}")
print(f"R02: cache_hit={o2['cache_hit']} answer={o2['answer']} cites={o2['citations']} "
      f"evidence={[b['id'] for b in o2['evidence']]} elapsed_ms={o2['elapsed_ms']:.3f}")
print("   → R02 期望 12秒/b02，实际返回 30秒/b01 且 evidence 是 v1 段落：被 R01 的缓存污染。")

print()
print('== (B) 单独 fresh 跑 R02（区分性干预：排除检索/过滤 bug）==')
e2 = Engine()
o2b = e2.evaluate(r02['request'], corpus, r02['draft'])
print(f"R02(fresh): cache_hit={o2b['cache_hit']} answer={o2b['answer']} cites={o2b['citations']} "
      f"evidence={[b['id'] for b in o2b['evidence']]}")
print()
if o2b['answer'] == '请求超时阈值为12秒。' and o2b['citations'] == ['b02']:
    print('结论：单独跑 R02 正确(12秒/b02)，检索/过滤本身无误 → 支持解释1（缓存复用错误），排除解释2。')
else:
    print('结论：单独跑 R02 仍错 → 支持解释2（过滤另有 bug）。')

print()
print('== 反向因果检查：更低耗时来自命中旧缓存 ==')
print(f"R01 elapsed={o1['elapsed_ms']:.3f}ms（未命中，做完整检索+排序+过滤）")
print(f"R02 elapsed={o2['elapsed_ms']:.3f}ms（cache_hit=True，跳过检索，仅 deepcopy+update）")
print(f"   → 二者相差约 {(o1['elapsed_ms']-o2['elapsed_ms'])/o1['elapsed_ms']*100:.0f}%，"
      f"R02 的『低耗时』来自命中旧缓存、非真实加速，属于『反向因果/评价错误』风险。")
