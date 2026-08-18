# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal", "pyyaml"]
# ///
"""즉석 개별 수정 도구 — LLM 없이 찾고 바꾸고 바로 다시 만든다.

    uv run translate/fix.py "찾을 문구"              # 검색(한국어 v·원문 es 모두)
    uv run translate/fix.py "옛" --to "새"           # 전 매칭 행에서 부분 치환 + 자동 빌드
    uv run translate/fix.py "옛" --to "새" --file 00-maps   # 파일 한정
    uv run translate/fix.py "옛" --to "새" --nth 2   # 검색 결과 중 n번째 행만
    옵션 --no-build : 치환만 하고 dat 재빌드 생략

메모(나중에 배치 수정할 거리 적어 두기):
    uv run translate/fix.py "문구" --note "왜 어색한지"   # fixnotes.jsonl에 기록
    uv run translate/fix.py --notes                       # 미결 메모 목록
    uv run translate/fix.py --done 3                      # 3번 메모 완료 처리

검색 결과에는 파일·행번호·맵·원문이 함께 나온다. 치환 후에는 build.py가
돌아 보관소·게임 양쪽 korean.dat까지 갱신된다(실기 확인은 게임 재시작).
"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
KO = HERE / "ko"


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "stage0"))
    from edit import put_lines as _put
    return _put(edits)


def sweep_skip(name):
    sys.path.insert(0, str(HERE / "stage0"))
    from common import sweep_skip as _s
    return _s(name)

ASSETS = HERE / "data/asset-texts.jsonl"


def rows():
    # 그림 자산 문안(Z-74) — 검색·전수 치환이 이미지 문구에도 미친다(유지자 지시).
    for i, line in enumerate(ASSETS.read_text(encoding="utf-8").splitlines(), 1):
        d = json.loads(line)
        if d.get("ko"):
            yield ASSETS, i, None, d["es"], d["ko"], d
    for p in sorted(KO.glob("*.jsonl")):
        cur_map = None
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            d = json.loads(line)
            if "map" in d and "n" in d:
                cur_map = d["map"]
                continue
            v = d.get("v")
            es = d.get("k") or d.get("es") or ""
            if v is None:
                continue
            yield p, i, cur_map, es, v, d


NOTES = HERE / "fixnotes.jsonl"


def load_notes():
    if not NOTES.exists():
        return []
    return [json.loads(l) for l in NOTES.read_text(encoding="utf-8").splitlines() if l]


def save_notes(notes):
    NOTES.write_text("\n".join(json.dumps(n, ensure_ascii=False) for n in notes) + "\n",
                     encoding="utf-8")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--notes":
        notes = load_notes()
        pend = [n for n in notes if not n.get("done")]
        print(f"미결 메모 {len(pend)} / 전체 {len(notes)}")
        for i, n in enumerate(notes, 1):
            mark = "완료" if n.get("done") else "미결"
            print(f"[{i}] ({mark}) 「{n['query'][:40]}」 — {n['note']}"
                  + (f"  ({n.get('hits', '?')}행 매칭)" if not n.get("done") else ""))
        return
    if args[0] == "--done":
        notes = load_notes()
        notes[int(args[1]) - 1]["done"] = True
        save_notes(notes)
        print(f"메모 {args[1]} 완료 처리")
        return
    query = args[0]
    to = args[args.index("--to") + 1] if "--to" in args else None
    only = args[args.index("--file") + 1] if "--file" in args else None
    nth = int(args[args.index("--nth") + 1]) if "--nth" in args else None

    hits = []
    for p, i, m, es, v, d in rows():
        if only and only not in p.name:
            continue
        if query in v or query in es:
            hits.append((p, i, m, es, v))
    print(f"매칭 {len(hits)}행")
    for n, (p, i, m, es, v) in enumerate(hits[:40], 1):
        loc = f"{p.name}:{i}" + (f" 맵{m}" if m is not None else "")
        print(f"[{n}] {loc}")
        print(f"    es: {es[:90]}")
        print(f"    ko: {v[:90]}".replace("\n", "\\n"))
    if len(hits) > 40:
        print(f"... 외 {len(hits) - 40}행")
    if "--note" in args:
        note = args[args.index("--note") + 1]
        notes = load_notes()
        notes.append({"query": query, "note": note, "hits": len(hits)})
        save_notes(notes)
        print(f"메모 기록 ({len(notes)}번): 「{query[:40]}」 — {note}")
        return
    if to is None:
        return

    targets = [hits[nth - 1]] if nth else hits
    touched = {}
    for p, i, m, es, v in targets:
        touched.setdefault(p, set()).add(i)
    changed, edits, left = 0, [], []
    regen = []
    for p, linenos in touched.items():
        if p == ASSETS:                    # 자산 문안 — 원료 파일에 직접 쓰고 그림은 재생성 몫
            lines = p.read_text(encoding="utf-8").splitlines()
            for i in linenos:
                d = json.loads(lines[i - 1])
                if query in d.get("ko", ""):
                    d["ko"] = d["ko"].replace(query, to)
                    lines[i - 1] = json.dumps(d, ensure_ascii=False)
                    regen.append(d["file"]); changed += 1
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            d = json.loads(line)
            if i not in linenos or query not in d.get("v", ""):
                continue
            if sweep_skip(p.name):        # 합성 열쇠 파일 — 사람이 직접 고칠 자리
                left.append(f"{p.name}:{i} {d.get('v', '')[:60]}")
                continue
            edits.append((p.name, i, d["v"].replace(query, to)))
            changed += 1
    for ln in left:
        print(f"  건너뜀(추가분·좌표는 직접 고친다) {ln}")
    err = put_lines(edits)
    if err:
        print("멈춤 —", err)
        return
    print(f"치환 {changed}행 (「{query[:30]}」→「{to[:30]}」)")
    if regen:
        print(f"⚠ 그림 재생성 필요 {len(regen)}장: {', '.join(regen[:8])}"
              + (" …" if len(regen) > 8 else "")
              + " — translate/assets/ 생성기 재실행 후 install_assets.py --write")
    if changed and "--no-build" not in args:
        r = subprocess.run(["uv", "run", str(HERE / "build.py")],
                           capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])


if __name__ == "__main__":
    main()
