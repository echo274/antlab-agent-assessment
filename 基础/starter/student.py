"""证据核验：prepare_messages 与 improve 的实现。

约束（见 01_考核题目.md）：
- prepare_messages / improve 只读取 question 与本次可见 passages，
  不读答案、题号或 condition，不按固定 ID 生成结果。
设计说明与三项决定见 report.md / decisions.md。
"""
import re


def prepare_messages(question, passages):
    """返回 [{"role","content"}, ...]，强制模型输出 JSON 证据链。"""
    system = (
        "你是文档核验助手，只依据下面提供的“段落资料”回答，禁止使用外部知识或记忆。\n"
        "段落来自多个项目/版本/批次，其中存在干扰项（项目名、版本、月份、批次或指标口径相近但不同）。"
        "必须严格匹配问题中的项目名、版本、月份窗口、批次和指标口径；忽略相近但不同的记录。\n"
        "允许跨两段组合计算（如：百分比=分子/分母，差值=两数相减，或按某段的规则筛选另一段的候选）。\n"
        "输出规则：\n"
        "1. 只输出一个 JSON 对象，不要代码块标记、解释、标点或任何多余文字；\n"
        "2. 字段为 \"answer\"（简短答案，只答数值或名称）和 \"citations\"（支撑答案的段落ID数组）；\n"
        "3. citations 只能填资料里实际出现的段落 ID；\n"
        "4. 资料不足以回答时，answer 填“证据不足”，citations 列出你用来判断“证据不足”所核对的段落 ID；"
        "不要把缺失信息编造成事实。\n"
        "示例：{\"answer\":\"80%\",\"citations\":[\"P312446\",\"P898100\"]}"
    )
    blocks = [f"[ID {p['id']} | 来源 {p['source']}]\n{p['text']}" for p in passages]
    user = f"问题：{question}\n\n段落资料（共 {len(passages)} 段）：\n\n" + "\n\n".join(blocks)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _entity_tokens(question):
    """从问题提取判别实体：项目名（XX项目）、版本号（R加数字）、月份（YYYY-MM）。"""
    toks = set(re.findall(r'[一-鿿]{2}项目', question))
    toks |= set(re.findall(r'R\d+', question))
    toks |= set(re.findall(r'\d{4}-\d{2}', question))
    return toks


def improve(question, passages):
    """改进：按问题实体（项目名/版本/月份）相关性重排段落，把最相关的段落前置。

    只用问题与段落文本，不读答案、题号或固定 ID，因此对段落顺序与 ID 重映射不变。
    保留全部段落（只重排、不丢弃）。批次码在本题里被干扰项共享，不作为判别信号。
    """
    toks = _entity_tokens(question)
    return sorted(passages, key=lambda p: sum(1 for t in toks if t in p['text']), reverse=True)
