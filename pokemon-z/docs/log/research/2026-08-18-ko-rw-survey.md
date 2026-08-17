# translate/ko/ 읽기·쓰기 전수 조사 (2026-08-18)

3단계 승격 설계의 재료. 서브 넷이 translate/·share/·webapp/·tools/를 전수로 훑었고,
아래 표의 근거 줄은 전부 파일을 직접 열어 확인한 실측이다.

## ko를 고치는 도구 — 열둘

| 도구 | 고치는 것 | 쓰기 꼴 | 근거 |
|---|---|---|---|
| `fixgui.py` | 임의 절 한 파일 | 행 단위 값 교체(줄 수 불변) + fixlog append | fixgui.py:403-422 |
| `apply_verdicts.py` | 00-maps | 값 교체(줄 수 보존) | apply_verdicts.py:300-316 |
| `batch.py apply` | 00-maps·22·23 | 값 교체 | batch.py:371-395 |
| `fill.py apply` | 23 + 설명 절(03·06·09·11·20) | 값 교체 | fill.py:264-283 |
| `judge.py apply` | 00-maps·22·23 | 값 교체 | judge.py:183-207 |
| `unified.py restore` | 00-maps | 값 교체 | unified.py:128-147 |
| `canon_sweep.py --write` | 지정 절 하나 | 값 교체(승인 목록 필수) | canon_sweep.py:72-75 |
| `harvest.py` | dat에 손댄 절 | 행 단위 값 교체 | harvest.py:150-154 |
| `fix.py` | 검색에 걸린 절 | 치환 | fix.py:113-121 |
| `apply_josa.py` | 전 절 | 치환 | apply_josa.py:78-100 |
| `tools/names.py rename` | 전 절 | 치환 | tools/names.py:38,128-144 |
| `export.py` | 전 절 | **통째 재생성**(줄 수 변동 가능) | export.py:86-88 |
| `stage0/emit.py --write` | 전 절 + loc | 역생성 전체 재작성(왕복 차이 0) | emit.py:49 → diff.py:170-171 |

emit --write까지 세면 열셋이고, export와 emit 둘만 줄 수를 바꿀 수 있다. 나머지 열하나는
전부 「기존 줄을 읽어 같은 개수로 재기록」하는 꼴이라 fixlog의 줄 번호가 안 밀린다.
(provenance는 애초에 줄 번호를 앵커로 안 쓴다 — provenance.py:194-196, 원문 앵커 946건
전부 유일 실측.)

`apply_terms`·`apply_names`·`apply_dialogue_terms`·`apply_battle_expr` 넷은 ko가 아니라
korean.dat를 직접 다시 쓰는 옛 도구다(각 파일 끝의 `STORE/GAME.write_bytes`).
`mend_newlines`·`screen_llm`·`register`·`make_speakers`·`dexswap`·`provenance`는 ko에
쓰지 않는다(각 파일 grep 0건 확인).

## ko를 읽기만 하는 도구 — 열여섯

build(전 절→dat) · verify(검증) · probe(진단 조회) · batch_pages(프롬프트 재료) ·
batch_trainers(간접) · battle_materials · mapname · mapscan · mine · speaker(표시용) ·
survey · termcheck · xfer_text · tools/status_icon(절23 caduco 신선도) ·
tools/names.py(check/sweep) · share/make_package(배포 킷 복사, stage0 groups.yaml도 복사).
줄 단위 근거는 서브 보고 원문(세션 기록)에 있고, 전부 「ko 파일이 그 자리에 있으면 된다」는
성질이라 승격과 무관하다.

webapp/은 ko·stage0를 코드로 읽지 않는다(grep 0건). stage0 정본 여섯 중 밖에서 읽는 것은
make_package의 groups.yaml 복사 하나뿐이다.

## gen·emit의 실측 성질 (승격 설계가 딛는 것)

- gen 입력: ko 스물넷(빈 절 셋 제외) + data/ 열한 종 + names.json + overrides. 산출은
  sites·messages·axes 셋뿐이고 voices·terms·groups는 만들지도 다시 쓰지도 않는다
  (gen.py:11-12, 282-291).
- emit --write는 diff.rebuild의 역생성을 파일 통째로 앉힌다. 미커밋 ko 수정이 있으면
  멈춘다(emit.py:26-47). 쓰기는 대조 뒤다(diff.py:168-171).
- 전체 emit dry-run **2.3초**(2026-08-18, 이 기계).
- 같은 dry-run에서 차이 12건(overrides 유래 0) — 전날 상점 존대 통일 커밋의 자국.
  ko가 출처인 현행 구조에서 gen 재흡수가 안 돈 상태의 정상 신호이고, 전환기 임시 규약
  (설계 「이행 3단계」)의 실증이다.
