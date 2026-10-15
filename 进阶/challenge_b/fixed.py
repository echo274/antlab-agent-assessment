"""修复版 Engine：最小修复「缓存键粒度不足」这一主故障。

与 challenge.py 的唯一差异在 _cache_key()：缓存键由 query 扩展为
「query + doc_ids(排序归一) + snapshot + k」，使「同 query 但不同文档范围 /
快照 / 返回数」的请求不再互相污染。

只改缓存键，不动其余逻辑（检索先截断后过滤、support_status 把「ID 有效」
当「语义支持」这两个症状在报告中登记为风险，不属于本次最小修复范围）。
基线记录保留在 challenge.py；本文件为兼容 Engine，可用 --engine fixed:Engine 运行。
"""
import copy
import time
import uuid


class Engine:
    def __init__(self):
        self.cache = {}

    @staticmethod
    def _cache_key(request):
        # 修复点：缓存键覆盖请求的完整「语义」，而不只是 query 文本。
        # doc_ids 排序归一，使「同一组文档、不同书写顺序」仍命中同一缓存。
        return (
            request['query'].strip().lower(),
            tuple(sorted(request['doc_ids'])),
            request['snapshot'],
            request['k'],
        )

    def evaluate(self, request, corpus, draft):
        started = time.perf_counter()
        key = self._cache_key(request)
        hit = key in self.cache
        if hit:
            result = copy.deepcopy(self.cache[key])
        else:
            terms = set(request['query'].strip().lower().split())
            ranked = sorted(corpus, key=lambda b: (-len(terms & set(b['tags'])), b['id']))
            selected = [b for b in ranked[:request['k']] if terms & set(b['tags'])]
            evidence = [b for b in selected if b['doc_id'] in request['doc_ids'] and b['snapshot'] == request['snapshot']]
            citations = draft['citations']
            valid = bool(citations) and set(citations).issubset({b['id'] for b in evidence})
            result = {'answer': draft['answer'], 'citations': citations, 'evidence': evidence,
                      'locator_status': 'valid' if valid else 'invalid',
                      'support_status': 'supported' if valid else 'not_checked',
                      'judgment_source': 'rule', 'status': 'ok'}
            self.cache[key] = copy.deepcopy(result)
        result.update(request_id=str(uuid.uuid4()), request=copy.deepcopy(request), cache_hit=hit,
                      elapsed_ms=(time.perf_counter()-started)*1000, run_kind='offline_replay')
        return result
