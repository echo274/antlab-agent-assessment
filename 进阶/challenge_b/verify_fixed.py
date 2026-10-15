"""修复后验证：R02 修复、两个正常回归、两个等价变体、一个自构未解决边界。

每个检查先写预期依据（引用 spec.md 规则），再跑 fixed.Engine 验证。
"""
import json
from pathlib import Path
from fixed import Engine

ROOT = Path(__file__).parent
data = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
corpus = data['corpus']
by_id = {c['id']: c for c in data['cases']}


def run_cases(cases, corp):
    inst = Engine()
    out = {}
    for c in cases:
        if c['reset_before']:
            inst = Engine()
        out[c['id']] = inst.evaluate(c['request'], corp, c['draft'])
    return out


passed = []


def check(name, cond, why):
    status = 'PASS' if cond else 'FAIL'
    passed.append(cond)
    print(f"[{status}] {name}")
    if not cond:
        print(f"       预期依据: {why}")


# 1) 原始失败复现 + 修复：R01→R02 顺序下 R02 不再被污染
print('== 1) 修复后复跑 R01→R02（原始失败复现的修复）==')
res = run_cases(data['cases'], corpus)
r02 = res['R02']
print(f"  R02: cache_hit={r02['cache_hit']} answer={r02['answer']} cites={r02['citations']} "
      f"evidence={[b['id'] for b in r02['evidence']]}")
check('R02 返回 12秒/b02（v2 快照，不再被 v1 污染）',
      r02['answer'] == '请求超时阈值为12秒。' and r02['citations'] == ['b02'],
      'spec 1/3/5：查询范围由 doc_ids+snapshot 确定，不能回退另一快照；换版本不得显示旧结论。')

# 2) 两个原本正常回归：修复后仍正常
print('\n== 2) 两个原本正常回归 ==')
r05 = res['R05']
check('R05 metadata beta 仍返回 b05、locator=valid',
      r05['citations'] == ['b05'] and r05['locator_status'] == 'valid',
      'spec 2/3：scope 内正分证据应被选中，引用有效。')
r06 = res['R06']
check('R06 worker single process 仍返回 b06、locator=valid',
      r06['citations'] == ['b06'] and r06['locator_status'] == 'valid',
      'spec 2/3：同上。')

# 3) 等价变体 1：标识重映射（id/doc_id/snapshot 统一加前缀，语义不变）
print('\n== 3) 等价变体 1：标识重映射 ==')


def remap(corp, req, draft, prefix='X'):
    new_corp = [{**b, 'id': prefix + b['id'], 'doc_id': prefix + b['doc_id'], 'snapshot': prefix + b['snapshot']}
                for b in corp]
    new_req = {**req, 'doc_ids': [prefix + d for d in req['doc_ids']], 'snapshot': prefix + req['snapshot']}
    new_draft = {**draft, 'citations': [prefix + c for c in draft['citations']]}
    return new_corp, new_req, new_draft


corp2, req1, draft1 = remap(corpus, by_id['R01']['request'], by_id['R01']['draft'])
corp2, req2, draft2 = remap(corpus, by_id['R02']['request'], by_id['R02']['draft'])
inst = Engine()
o1 = inst.evaluate(req1, corp2, draft1)
o2 = inst.evaluate(req2, corp2, draft2)
print(f"  R01(重映射): answer={o1['answer']} cites={o1['citations']}")
print(f"  R02(重映射): cache_hit={o2['cache_hit']} answer={o2['answer']} cites={o2['citations']}")
check('重映射后 R01=30秒/Xb01、R02=12秒/Xb02（按字段语义工作，不依赖具体字符串）',
      o1['citations'] == ['Xb01'] and o2['citations'] == ['Xb02'] and o2['answer'] == '请求超时阈值为12秒。',
      'spec 4/变体要求：标识重映射是语义等价的输入，修复应不依赖具体 id/doc_id/snapshot 字符串。')

# 4) 等价变体 2：corpus 顺序打乱（修复后的正确行为与顺序无关）
print('\n== 4) 等价变体 2：corpus 顺序打乱 ==')
corp3 = list(reversed(corpus))
inst = Engine()
inst.evaluate(by_id['R01']['request'], corp3, by_id['R01']['draft'])  # 先跑 R01 填充缓存
o3 = inst.evaluate(by_id['R02']['request'], corp3, by_id['R02']['draft'])  # 逆序下跑 R02
print(f"  R02(乱序): cache_hit={o3['cache_hit']} answer={o3['answer']} cites={o3['citations']}")
check('R02 乱序后仍返回 12秒/b02（修复按内容排序，与 corpus 输入顺序无关）',
      o3['answer'] == '请求超时阈值为12秒。' and o3['citations'] == ['b02'],
      'spec 2：排序按 tags 得分+id 字典序，与 corpus 输入顺序无关；变体验证顺序不改变修复后的结论。')

# 5) 自构未解决边界：缓存键不含资料内容，资料更新后仍命中旧缓存
print('\n== 5) 自构未解决边界：资料更新后缓存未失效 ==')
inst = Engine()
o_before = inst.evaluate(by_id['R01']['request'], corpus, by_id['R01']['draft'])
corp_updated = [{**b, 'text': b['text'].replace('30秒', '999秒')} for b in corpus]  # 资料文本修订
o_after = inst.evaluate(by_id['R01']['request'], corp_updated, by_id['R01']['draft'])
print(f"  更新前 R01: answer={o_before['answer']} evidence_text 含 '30秒'={any('30秒' in b['text'] for b in o_before['evidence'])}")
print(f"  更新后 R01: cache_hit={o_after['cache_hit']} evidence_text 含 '999秒'={any('999秒' in b['text'] for b in o_after['evidence'])}")
check('已知边界未解决：同请求在资料更新后仍命中旧缓存（返回旧 evidence 文本）',
      o_after['cache_hit'] is True,
      'spec 5：缓存可复用等价输入，但不能污染「改变资料后的请求」。本修复的键不含资料内容/版本 hash，'
      '静态 fixture 不触发；真实系统资料可更新时需在缓存键中加入资料版本 hash 或显式失效。')

print(f'\n结果：{sum(passed)}/{len(passed)} 通过')
