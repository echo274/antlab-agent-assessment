"""不调模型的检查：诊断（套规则失败归因）+ 变体（ID 重映射下 improve 按内容工作）。

诊断：T01/T08 模型答“证据不足”，但规则与候选段落都在本次输入中。
      用「模型实际引用的段落」判断是检索失败还是套用失败。
变体：对 improve() 做 ID 重映射，验证其排序只依赖段落内容（项目/版本/月份），不依赖 ID。
"""
import json, sys, copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '基础' / 'starter'))
import student

cases = json.loads((ROOT / '基础' / 'data' / 'cases.json').read_text(encoding='utf-8'))
byid = {c['id']: c for c in cases}

def passages_of(cid, cond):
    c = byid[cid]
    pid = {p['id']: p for p in c['passages']}
    return [copy.deepcopy(pid[i]) for i in c['conditions'][cond]]


def latest_paid_run(case, cond, variant='baseline'):
    """从 runs/ 取最近一次付费运行记录（用于读模型实际引用）。"""
    runs = sorted((ROOT / '基础' / 'runs').glob('*.json'))
    for f in reversed(runs):
        r = json.loads(f.read_text(encoding='utf-8'))
        if r.get('mode') == 'paid' and r['case_id'] == case and r['condition'] == cond and r['variant'] == variant:
            return r
    return None


print('== 诊断：T01/T08 答“证据不足”是检索失败还是套用失败 ==')
for case, rule_id, cand_id in [('T01', 'P761989', 'P555495'), ('T08', 'P223300', 'P183430')]:
    r = latest_paid_run(case, 'R0')
    if r is None:
        continue
    cites = []
    try:
        obj = json.loads(r['response']['choices'][0]['message']['content'])
        cites = obj.get('citations', [])
    except Exception:
        pass
    has_rule = rule_id in cites
    has_cand = cand_id in cites
    print(f'  {case}: 规则段 {rule_id} 被引用={has_rule}，候选段 {cand_id} 被引用={has_cand}，answer=证据不足')
    if has_rule and has_cand:
        print(f'    → 规则与候选都在引用里，却答“证据不足”：是「未套用规则」的推理失败，非检索/资料缺失。')


print('\n== 变体：improve 对段落 ID 重映射不变（只依赖内容） ==')
q = byid['D01']['question']
orig = passages_of('D01', 'R0')
ranked = student.improve(q, copy.deepcopy(orig))
base = [p['source'] for p in ranked]
# ID 重映射 Pxxxxxx -> Qxxxxxx，内容不变
remapped = [{**p, 'id': 'Q' + p['id'][1:]} for p in orig]
ranked2 = student.improve(q, copy.deepcopy(remapped))
new = [p['source'] for p in ranked2]
print('  基线排序(来源):', base)
print('  ID重映射后排序(来源):', new)
print('  结果:', 'PASS — improve 只依赖内容，不依赖 ID' if base == new else 'FAIL')
