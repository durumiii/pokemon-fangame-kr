#!/usr/bin/env python3
"""종결어미 분류기. anored/canon 공용.
전제: 태그 제거 -> 마지막 문장 -> 마지막 어절의 종결형으로 분류.
"""
import re, sys, json, gzip, collections

TAG = re.compile(r'\\[a-zA-Z]+(\[[^\]]*\])?')   # \c[3] \v[3] \xn[..] \pn \b \n

def clean(t):
    t = TAG.sub('', t)
    t = t.lstrip(']').strip()   # \xn[\c[1]\pn] 제거 후 남는 닫는 괄호
    return t

def is_narration(t):
    """플레이어 독백·시스템 지문: 화자가 \\pn 이거나 전문이 괄호로 감싸짐."""
    c = clean(t)
    if c.startswith('(') or c.startswith('（'):
        return True
    m = re.match(r'\\xn\[(.*?)\]', t) or re.match(r'\\xn\[(.*)$', t)
    return bool(m and '\\pn' in m.group(1) and '(' in c)

# --- 공식 덤프(canon) 전용 마크업 ---
VARTAG = re.compile(r'\[VAR\s+[^\]]*\]')      # [VAR 0114(0004)] [VAR TRNAME(0000)]
WAITTAG = re.compile(r'\[WAIT\s+[^\]]*\]|\[~\s*\d+\]')
ESC = re.compile(r'\\[nrcf]')                  # 리터럴 \n \r \c \f

def clean_canon(t):
    t = VARTAG.sub(' ', t)
    t = WAITTAG.sub(' ', t)
    t = ESC.sub(' ', t)
    t = t.replace('▶', ' ').replace('　', ' ')
    return re.sub(r'\s+', ' ', t).strip()

# --- 블랙2(gen5 NARC) 전용 ---
B2VAR = re.compile(r'VAR\([^)]*\)')

def clean_b2(t):
    t = B2VAR.sub(' ', t)
    return re.sub(r'\s+', ' ', t.replace('\f', ' ').replace('\r', ' ').replace('\n', ' ')).strip()

def sentences(t):
    """한 턴을 문장 단위로. 종결부호 기준, 부호를 남긴다."""
    return [s.strip() for s in re.split(r'(?<=[.!?…])\s+|(?<=[.!?…])(?=[가-힣])', t) if s.strip()]

def jong(ch):
    """한글 음절의 종성 인덱스. 비한글이면 -1."""
    o = ord(ch) - 0xAC00
    return o % 28 if 0 <= o < 11172 else -1

J_B, J_S = 17, 19   # ㅂ, ㅅ

SENT_END = '.!?…"\'」』)~'
def final_chunk(t):
    t = t.strip().rstrip(SENT_END + ' ')
    parts = [p.strip() for p in re.split(r'[.!?…]+\s*', t) if p.strip()]
    return parts[-1] if parts else ''

MENU = {'네', '예', '응', '아니', '아뇨', '아니오', '으응', '아냐', '취소', '그만두기'}

# 강한 하게체 표지 (어미 자체로 확정)
HAGE_STRONG = re.compile(r'(걸세|ㄹ세|일세|게나|구먼|구만|시게|보게|주게|하게|나그려)$')
# 약한 표지: 자네/그대 호칭이 같은 줄에 있을 때만 하게체
HAGE_WEAK = re.compile(r'(는가|은가|인가|런가)$')
HAGE_ADDR = re.compile(r'(자네|그대|자당|여보게)')

RULES = [
    ('해요',   re.compile(r'(요|죠|쇼)$')),
    ('해라친근', re.compile(r'(단다|란다|잖니|려무나|느니라|니라)$')),
    ('명령라', re.compile(r'(어라|아라|여라|거라|너라|봐라|하라|시라|렴)$')),
    ('해체',   re.compile(r'(다고|라고|냐고|자고|다니|다며)$')),   # 인용 반말 (연결어미보다 우선)
    ('평서다', re.compile(r'다$')),
    ('연결미완', re.compile(r'(면|서|며|고|지만|다가|거나|든지|니까|는데도|러|려고)$')),
    ('해체',   re.compile(r'(구나|군|거든|는걸|을걸|는데|은데|잖아|니|냐|자|래|마|까|지|어|아|야|여|네|게|걸|데|든|겠'
                          r'|줘|해|돼|봐|와|워|려|겨|셔|져|쳐|커|배|매|대|째|뭐|께'
                          r'|다고|라고|냐고|자고|드아)$')),
]

def classify(text):
    c = clean(text)
    c = re.sub(r'^\[[^\]]*\]', '', c).strip()
    if not c:
        return 'empty', ''
    fc = final_chunk(c)
    if not fc:
        return 'empty', ''
    if fc in MENU:
        return '체언기타', fc
    last = fc.split()[-1] if fc.split() else fc
    last = last.rstrip('~-,'"'\"")
    if not re.search(r'[가-힣]', last):
        return '비한글', last
    # 합쇼체: 니다/니까 + 앞 음절 종성이 ㅂ/ㅅ (합니다/있습니까). '아니다'는 제외됨.
    if len(last) >= 3 and last[-2:] in ('니다', '니까') and jong(last[-3]) in (J_B, J_S):
        return '합쇼', last
    if last.endswith(('십시오', 'ㅂ시다', '소서')):
        return '합쇼', last
    if HAGE_STRONG.search(last):
        return '하게', last
    if HAGE_WEAK.search(last):
        # 자네/그대 호칭이 있으면 하게체, 없으면 혼잣말성 해체
        return ('하게' if HAGE_ADDR.search(c) else '해체'), last
    for name, rx in RULES:
        if rx.search(last):
            return name, last
    return '체언기타', last

def load(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt', encoding='utf-8') as f:
        for i, l in enumerate(f, 1):
            l = l.strip()
            if l:
                yield i, json.loads(l)
