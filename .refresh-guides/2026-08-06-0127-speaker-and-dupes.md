---
type: refresh-guide
created: 2026-08-06T01:27:28+09:00
snapshot: refresh-snapshot.md
---

## 이 세션에서 만든 도구 — 실제 호출법

전부 `pokemon-z/`에서 실행. 셸 `grep`이 조용히 빈 결과를 내는 사례가 있으니 세는 일은 python으로.

```bash
# 화자 귀속
uv run translate/speaker.py scan            # 귀속표 재생성(19,310행)
uv run translate/speaker.py lines Barquero  # 한 인물 대사 전량
uv run translate/speaker.py who "어떻게 할까요"  # 특정 대사의 화자
uv run translate/speaker.py stats           # 근거별 집계
uv run translate/speaker.py selftest        # 정답 아는 7자리 채점 (7/7이어야 함)

# 고유명 표기
uv run tools/names.py check                 # 변이 잔존·표기 빠짐
uv run tools/names.py rename Áster 아스테르  # 정본+원장 동시 수정, 받침 바뀌면 경고
uv run tools/names.py selftest

# 제보
uv run tools/sheet.py tabs
uv run tools/sheet.py rows "설문지 응답 시트1"
uv run tools/sheet.py archive "설문지 응답 시트1" --yes

# 게이트 (이 둘은 게임 폴더·모드 보관소에도 쓴다 — 서브에이전트에겐 금지)
uv run translate/build.py
uv run translate/verify.py --strict          # FAIL 0 WARN 0 이어야 함
```

⚠ `tabs`가 보여주는 「N행」은 **격자 크기**지 응답 수가 아니다. 실제 응답은 `rows`로 센다.

## 다음 세션 항목 4 — 중복 원문의 번역 갈림, 조사 스크립트

맵 대사 원문 11,157개 중 305개(1,717행)가 여러 번역을 갖는다. 화자가 하나면 일괄 통일,
여럿이면 화자별 정본을 따로 잡아야 한다. 그 판정을 내는 스크립트(이번 세션에서 임시로 썼고
저장소에는 없다 — 필요하면 `tools/dupes.py`로 승격):

```python
import json, gzip, collections
rows=[json.loads(l) for l in gzip.open("docs/research/speaker-attr.jsonl.gz","rt",encoding="utf-8")]
spk=collections.defaultdict(set)
for r in rows:
    if r["how"]=="선택지": continue
    spk[r["k"].strip()].add(r["who"] or "")
byk=collections.defaultdict(list)
for l in open("translate/ko/00-maps.jsonl",encoding="utf-8"):
    if not l.strip(): continue
    r=json.loads(l)
    if "map" in r: continue
    byk[r["k"].strip()].append(r["v"])
multi={k:v for k,v in byk.items() if len(set(v))>1}
for k,v in multi.items():
    who={w for w in spk.get(k,set()) if w}
    bucket = "일괄" if len(who)<=1 else ("화자별" if who else "귀속밖")
    ...  # 일괄 212개·988행 / 화자별 58개·438행 / 귀속밖 35개
```

가장 심한 것: 「치료 완료! 필요할 때…」 21가지 · 포켓몬센터 인사말 20가지 ·
너즐록 실패 문구 32가지 · 기술 되살리기 22가지.
⚠ 전량 통일 금물 — 같은 원문을 간호사·기모노 접객원·귀부인이 각각 말하는 자리가 있다.

## 제보 트리아지 — 자리(위치) 해석법

보관본 `docs/reports/설문지 응답 시트1.jsonl`의 `자리` 칸은 절마다 뜻이 다르다.

- 분류 `0:맵 대사` → `"맵:순번"`. `00-maps.jsonl`은 `{"map":N,"n":개수}` 헤더 뒤에
  그 맵 엔트리가 이어지므로, 맵 블록을 만든 뒤 순번으로 찾는다.
- 그 밖의 절 → `":줄번호"`이고 **1-based 파일 줄**이다.
- 트레이너 직함·도구 등 일부 절은 원문이 `k`가 아니라 **`es`** 칸에 있다(`{"i":…,"v":…,"es":…}`).
  `k or es`로 통일해서 대조할 것.

## 워크트리 서브에이전트 프롬프트에 반드시 넣을 것

- `translate/ko/*.jsonl`만 고친다. `k`·`es`(원문)는 절대 수정 금지.
- `build.py`·`verify.py`·`fix.py`·`fixgui.py` **실행 금지** — 게임 폴더(`/mnt/d/Game`)와
  모드 보관소(`/mnt/d/GameVault`)에 쓴다. 검증은 부모가 머지 후.
- 대신 자체 검사 넷: 전 줄 파싱 / 행 수 불변 / `k` 변경 0건 / 어투 잔재 정규식 전수.
- 푸시·머지 금지, 다른 브랜치 건드리기 금지.
- 보고에 근거·재현 경로·확정도·한계, 「고친 것」과 「보류하고 표시만 한 것」 분리.
