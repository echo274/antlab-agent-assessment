"""判分脚本：读取 runs/ 下的付费运行，判定答案正确性、引用有效性与原文支撑。

- 评测题 T01-T08（split=evaluation）无公开答案，ground truth 由本人阅读 passages 原文人工确定，
  逐题依据见同目录 ground_truth.md，结果写入 results/results.csv（40 行主结果）。
- 开发题 D01-D04（split=dev）有公开答案，用 data/dev_answers.json 核对，仅作调试汇总。

主实验 vs 探索：
- 主实验 = 冻结配置（deepseek-chat、temperature=0、max_tokens=256）下的 40 次运行。
- 探索 = 其他配置（deepseek-reasoner / max_tokens=1024 / 无 temperature 等），另列，不计入 40 主结果。

口径：
- K 条件只给 2 段，当「规则」或「互补证据」被词法检索漏掉时，正确行为是答“证据不足”，
  故 GT 按条件区分 full（7 段）与 K（2 段）。
- 技术失败(status≠ok)、格式错误(answer 无法解析) 保留在分母，不剔除。
- 引用语义支撑(cite_support) 需人工核验，脚本先标 not_checked，人工结论见 ground_truth.md。
"""
import json, csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # 仓库根
RUNS = ROOT / '基础' / 'runs'
OUT = ROOT / 'results'

# 评测题条件感知 ground truth（依据见 ground_truth.md）
GT = {
    'T01': {'full': 'S24', 'K': '证据不足'},
    'T02': {'full': '76%', 'K': '证据不足'},
    'T03': {'full': '2.6', 'K': '证据不足'},
    'T04': {'full': '流程乙', 'K': '证据不足'},
    'T05': {'full': '证据不足', 'K': '证据不足'},
    'T06': {'full': '25%', 'K': '25%'},
    'T07': {'full': '方案丙', 'K': '证据不足'},
    'T08': {'full': 'K17', 'K': '证据不足'},
}
ALIASES = {'方案丙': {'方案丙', '丙'}, '流程乙': {'流程乙', '乙'}}
# 主实验冻结配置（deepseek-chat + temperature 0 + max_tokens 256）
FROZEN_MODEL, FROZEN_MAX_TOKENS = 'deepseek-chat', 256


def norm(s):
    return (s or '').strip().replace(' ', '').replace('％', '%').replace('。', '').replace('秒', '')


def answer_verdict(answer, gt):
    if norm(answer) == norm(gt):
        return 'correct'
    if gt in ALIASES and answer in ALIASES[gt]:
        return 'correct_alias'
    return 'wrong'


def load_runs():
    out = []
    for f in sorted(RUNS.glob('*.json')):
        r = json.loads(f.read_text(encoding='utf-8'))
        if r.get('mode') != 'paid':
            continue
        content = ''
        try:
            content = r['response']['choices'][0]['message']['content']
        except Exception:
            pass
        answer, cites = None, []
        try:
            obj = json.loads(content)
            answer = obj.get('answer')
            cites = obj.get('citations', [])
        except Exception:
            answer, cites = None, []
        inids = set(r['selected_passage_ids'])
        u = r.get('usage') or {}
        cfg = r.get('config') or {}
        out.append({
            'run_id': r['run_id'], 'split': r['split'], 'case_id': r['case_id'],
            'condition': r['condition'], 'variant': r['variant'], 'status': r['status'],
            'answer': answer if answer is not None else '',
            'citations': ';'.join(cites),
            'cite_valid': 'invalid' if any(c not in inids for c in cites) else ('valid' if cites else 'empty'),
            'elapsed_seconds': r.get('elapsed_seconds'),
            'prompt_tokens': u.get('prompt_tokens'), 'completion_tokens': u.get('completion_tokens'),
            'model': cfg.get('model', ''), 'max_tokens': (cfg.get('parameters') or {}).get('max_tokens'),
        })
    return out


def is_frozen(r):
    return r.get('model') == FROZEN_MODEL and r.get('max_tokens') == FROZEN_MAX_TOKENS


def main():
    runs = load_runs()
    dev_answers = json.loads((ROOT / '基础' / 'data' / 'dev_answers.json').read_text(encoding='utf-8'))
    DEV_GT = {d['id']: d['answer'] for d in dev_answers}

    # 开发题调试汇总
    dev = Counter()
    for r in runs:
        if r['split'] != 'dev':
            continue
        gt = DEV_GT.get(r['case_id'])
        dev[r['status'] if r['status'] != 'ok' else answer_verdict(r['answer'], gt)] += 1
    print('dev (D01-D04):', dict(dev))

    # 主实验（冻结配置）与探索分开
    rows, explore = [], []
    for r in runs:
        if r['split'] != 'evaluation':
            continue
        (explore if not is_frozen(r) else rows).append(r)

    def score_row(r):
        gt = GT.get(r['case_id'], {}).get('K' if r['condition'] == 'K' else 'full')
        if r['status'] != 'ok':
            return 'tech_fail'
        if not r['answer']:
            return 'format_err'
        if gt is None:
            return 'no_gt'
        return answer_verdict(r['answer'], gt)

    for r in rows:
        r['verdict'] = score_row(r)
        r['cite_support'] = 'not_checked'

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['run_id', 'case_id', 'condition', 'variant', 'status', 'answer', 'citations',
              'verdict', 'cite_valid', 'cite_support', 'elapsed_seconds', 'prompt_tokens', 'completion_tokens']
    with open(OUT / 'results.csv', 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)

    def ok(v):
        return v in ('correct', 'correct_alias')

    print('== 主实验 baseline (32) ==', dict(Counter(r['verdict'] for r in rows if r['variant'] == 'baseline')))
    print('   correct =', sum(ok(r['verdict']) for r in rows if r['variant'] == 'baseline'))
    print('== 主实验 improved (8) ==', dict(Counter(r['verdict'] for r in rows if r['variant'] == 'improved')))
    print('   correct =', sum(ok(r['verdict']) for r in rows if r['variant'] == 'improved'))
    print('== 主实验 per-case (baseline R0/R1/R2/K) ==')
    for c in sorted(GT):
        sub = {r['condition']: r['verdict'] for r in rows if r['case_id'] == c and r['variant'] == 'baseline'}
        print(f'  {c}: ' + ' '.join(f"{k}={sub.get(k, '?')}" for k in ['R0', 'R1', 'R2', 'K']))
    print('== 探索（非冻结配置）==')
    for r in explore:
        print(f"  {r['case_id']} {r['condition']} model={r['model']} mt={r['max_tokens']} status={r['status']} => {r['answer']}")
    print('written', len(rows), 'main eval rows -> results/results.csv')


if __name__ == '__main__':
    main()
