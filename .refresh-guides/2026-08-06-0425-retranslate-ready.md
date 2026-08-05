---
type: refresh-guide
created: 2026-08-06T04:25:46+09:00
snapshot: refresh-snapshot.md
---

## 이 세션에서 만든 도구 — 실제 호출법

전부 `pokemon-z/`에서. 세는 일은 python으로(셸 grep이 조용히 빈 결과를 내는 사례가 있다).

```bash
# 화자 귀속 (2026-08-06 조회 열쇠 버그 수정됨)
uv run translate/speaker.py lines Mirra      # 한 인물 대사 전량
uv run translate/speaker.py who "검색어"
uv run translate/speaker.py selftest         # 7/7이어야 함
# ⚠ scan은 귀속표(docs/research/speaker-attr.jsonl.gz)를 덮어쓴다 — 서브에겐 금지

# 어미 급 검사 (신설)
uv run translate/register.py scan            # 어긋난 자리 → docs/research/2026-08-06-register-mismatch.md
uv run translate/register.py who Mirra       # 인물의 존대/하대 분포
uv run translate/register.py selftest
# 코드에서 쓸 때: sys.path.insert(0,'translate'); from register import axis

# 출처 장부 (신설) — 보호 대상을 기계가 가린다
uv run translate/provenance.py build         # → docs/research/protected.jsonl (이벤트 단위)
uv run translate/provenance.py stats         # 출처×반복 여부 집계
uv run translate/provenance.py selftest

# 맵 이름 (신설)
uv run translate/mapname.py 150 214          # 번호 → 한국어·스페인어 이름
uv run translate/mapname.py --tag 문서.md     # 문서의 「맵150」에 이름 붙이기

# 고유명 원장 (sweep 신설, 원장 70개)
uv run tools/names.py sweep                  # 정본을 훑어 갈린 표기를 캐낸다
uv run tools/names.py check
uv run tools/names.py rename <es> <새표기>
uv run tools/names.py add <es> <ko> [쪽지]

# 게이트 (게임 폴더·모드 보관소에 쓴다 — 서브에겐 금지)
uv run translate/build.py
uv run translate/verify.py --strict           # FAIL 0 WARN 0 이어야 함
```

## 재번역 사정권을 다시 계산하는 법

숫자는 정본이 바뀌면 움직인다. **쓰는 시점에 다시 생성해야 한다.**

```python
import json,gzip,re,collections
fold=lambda s: re.sub(r'\s+',' ',s or '').strip()
A=[json.loads(l) for l in gzip.open('docs/research/speaker-attr.jsonl.gz','rt',encoding='utf-8')]
SYS={'PISTA DE ENTRENADOR','Notas del Team Azoth','\\PN','AVISO','Oeste','Sur','Este','Norte',
     'Movimientos de patada','Movimientos de viento','ATENCIÓN','Gran Hotel Luminalia','1ºRegente'}
pages=collections.defaultdict(list); conf=set()
for a in A:
    pages[(a['map'],a['event'],a['page'])].append(a)
    if a['kind']=='text' and a['how'] in ('태그','상속') and a['who'] not in SYS:
        conf.add((a['map'],fold(a['k'])))
rows=[];cur=None
for l in open('translate/ko/00-maps.jsonl',encoding='utf-8'):
    r=json.loads(l)
    if 'map' in r: cur=r['map']; continue
    rows.append((cur,fold(r['k'])))
scope=[r for r in rows if r in conf]                      # → 5,993 정본 행

# 제외: provenance가 낸 보호 이벤트 + 극초반 크리산토·올리비에 + 맵65 + 인물 어투
ev={(r['map'],r['event'],r['page']) for r in map(json.loads,open('docs/research/protected.jsonl',encoding='utf-8'))}
early={k for k,v in pages.items() if k[0]<=16 and any(x['who'] in ('Crisanto','Olivier') for x in v)}
intro={k for k in pages if k[0]==65}
VOICE={'Barquero','Zafra','Núbila','Camarero'}
vk={(a['map'],fold(a['k'])) for a in A if a['kind']=='text' and a['how'] in ('태그','상속') and a['who'] in VOICE}
ex={(m,fold(a['k'])) for (m,e,p) in (ev|early|intro) for a in pages[(m,e,p)] if a['kind']=='text'} | vk
print(len(scope), len(scope)-sum(1 for r in scope if r in ex))   # → 5993 4787
```

## 서브에이전트 프롬프트에 반드시 넣을 것

- `translate/ko/*.jsonl`만 고친다. `k`·`es`(원문)는 절대 수정 금지. 행 수 불변.
- `build.py`·`verify.py`·`fix.py`·`fixgui.py`·`export.py`·`apply_josa.py` **실행 금지**
  (게임 폴더 `/mnt/d/Game`와 모드 보관소 `/mnt/d/GameVault`에 쓴다). `speaker.py scan`·
  `register.py scan`도 금지(산출물을 덮어쓴다). 읽기 명령은 허용.
- 푸시·머지 금지, 다른 브랜치 건드리기 금지. 워크트리 안에서만 커밋.
- 커밋 메시지 마지막 줄에 `Edit-Source: human|batch|bulk-term`.
- 자체 검사 넷: 전 줄 파싱 / 행 수 불변 / `k` 변경 0건(`git show HEAD:…`와 행 단위 대조) /
  고친 자리마다 `register.axis()`로 의도한 급 확인. 마크업 아홉 종 개수 대조도.
- 보고에 근거·재현 경로·확정도·한계, 「고친 것」과 「보류한 것」 분리.
- **맵은 번호와 이름을 함께** 적는다(`mapname.py`).

## 워크트리 머지 때 겪은 것

서브가 갈라져 나간 뒤 main이 움직이면 충돌한다(안젤린 표기 전에 갈라진 워크트리가
「앙젤린」을 들고 돌아와 어미 수선과 충돌). **해소는 서브 쪽을 채택하고 그 위에 main의
표기 판정을 얹는 것** — 줄마다 원문 칸이 일치하는지 대조해 확인했다.
서브가 스스로 main을 워크트리로 머지해 오는 경우도 있다(도구가 없어서). 그건 정상이다.

## 이 세션에서 헛디딘 것

- **단위 혼동**: 「사정권 8,440행」은 정본 줄이 아니라 등장 횟수였다. 유지자가 짚었다.
- **제보 수 = 손댄 자리 수 오해**: 308행 중 150행이 일괄 바꾸기 둘에서 나왔다.
- **usted 과소 계수**: 정규식이 낱말 `usted`만 잡아 히비스의 존대 73행을 통째로 놓쳤다.
- **vos 오독**: vosotros 활용 738행 중 경칭은 65개뿐, 나머지는 일행을 부르는 복수였다.
- **미라 평평하게 누르기**: 말투표대로 15곳을 하대로 고쳤다가 옆줄과 부딪혀 전부 되돌렸다.
