# /// script
# requires-python = ">=3.12"
# ///
"""고유명 표기 원장 — 흩어진 표기를 한 곳에서 관리한다.

같은 인물·조직·용어가 번역 정본 곳곳에서 다르게 적히는 사고가 반복됐다
(아스터/아스테르 · 샤핀/사핀 · 프리물라/프리뮬라 · 팀 아조스/아조스단).
사람 눈으로 잡으면 늘 늦으니, 정본 표기를 원장에 적어 두고 기계가 훑는다.

원장: translate/canon/names.jsonl — 한 줄이 이름 하나다.
    {"es": 원문, "ko": 정본 표기, "변이": [틀린 표기…], "쪽지": 판정 근거,
     "생략허용": true}   # 원문에 있어도 번역에서 이름을 안 쓸 수 있는 자리

usage:
  uv run tools/names.py check              변이 잔존과 표기 빠짐을 훑는다
  uv run tools/names.py rename <es> <새표기>  정본을 훑어 바꾸고 원장을 고친다
                                            (옛 표기는 변이 목록으로 내려간다)
  uv run tools/names.py add <es> <ko> [쪽지]  원장에 새 이름을 올린다

`check`는 verify.py에도 같은 검사가 들어 있다(재배포 게이트). 이 도구는 작업
중에 바로 돌려 보는 쪽이다.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent.parent
LEDGER = HERE / "translate" / "canon" / "names.jsonl"
KO_DIR = HERE / "translate" / "ko"

FINAL_CONSONANT = set()  # 받침 있는 한글 음절은 코드로 판별한다


def has_batchim(word):
    """마지막 한글 음절에 받침이 있는가 — 조사 선택이 이걸로 갈린다."""
    for ch in reversed(word):
        if "가" <= ch <= "힣":
            return (ord(ch) - 0xAC00) % 28 != 0
    return None  # 한글이 아니면 판단하지 않는다


def load_ledger():
    if not LEDGER.exists():
        return []
    return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def save_ledger(rows):
    LEDGER.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def ko_files():
    return sorted(KO_DIR.glob("*.jsonl"))


def each_row():
    """(파일, 줄번호, 엔트리) — 원문은 절마다 `k` 또는 `es`에 들어 있다."""
    for f in ko_files():
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                yield f, n, json.loads(line)


def src_of(entry):
    return entry.get("k") or entry.get("es") or ""


def cmd_check():
    ledger = load_ledger()
    bad = missing = 0
    for f, n, e in each_row():
        v = e.get("v", "")
        if not v:
            continue
        src = src_of(entry=e)
        for r in ledger:
            for wrong in r.get("변이", []):
                if wrong in v:
                    bad += 1
                    print(f"[변이] {f.name}:{n} {wrong!r} → {r['ko']!r}  | {v[:70]}")
            if r["es"] in src and r["ko"] not in v and not r.get("생략허용"):
                missing += 1
                print(f"[빠짐] {f.name}:{n} 원문에 {r['es']!r} 있는데 {r['ko']!r} 없음 | {v[:70]}")
    print(f"\n이름 {len(ledger)}개 · 변이 잔존 {bad} · 표기 빠짐 {missing}")
    return 1 if bad else 0


def cmd_rename(es, new):
    ledger = load_ledger()
    row = next((r for r in ledger if r["es"] == es), None)
    if row is None:
        sys.exit(f"원장에 없는 이름이에요: {es} — 먼저 add로 올려주세요")
    old = row["ko"]
    if old == new:
        sys.exit(f"이미 {new!r}예요")
    if old in new or new in old:
        print(f"⚠ 옛 표기와 새 표기가 서로를 품어요({old!r} / {new!r}) — "
              f"부분 치환이 겹칠 수 있으니 결과를 꼭 확인하세요")
    ob, nb = has_batchim(old), has_batchim(new)
    if ob is not None and nb is not None and ob != nb:
        print(f"⚠ 받침이 달라져요({old!r} {'있음' if ob else '없음'} → "
              f"{new!r} {'있음' if nb else '없음'}) — 뒤따르는 조사를 확인하세요")

    changed = 0
    for f in ko_files():
        lines = f.read_text(encoding="utf-8").split("\n")
        hit = 0
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            e = json.loads(line)
            if old in e.get("v", ""):
                e["v"] = e["v"].replace(old, new)
                lines[i] = json.dumps(e, ensure_ascii=False)
                hit += 1
        if hit:
            f.write_text("\n".join(lines), encoding="utf-8")
            print(f"  {f.name} {hit}행")
            changed += hit

    row["ko"] = new
    row["변이"] = sorted(set(row.get("변이", [])) | {old})
    save_ledger(ledger)
    print(f"{changed}행을 {old!r} → {new!r}로 고치고 원장을 갱신했어요 "
          f"(옛 표기는 변이 목록으로 내려갔어요)")
    print("빌드해서 게임에 반영하세요: uv run translate/build.py")


def cmd_add(es, ko, note=""):
    ledger = load_ledger()
    if any(r["es"] == es for r in ledger):
        sys.exit(f"이미 원장에 있어요: {es}")
    ledger.append({"es": es, "ko": ko, "변이": [], "쪽지": note})
    save_ledger(ledger)
    print(f"원장에 올렸어요: {es} → {ko}")


def selftest():
    assert has_batchim("아조스단") is True          # ㄴ 받침
    assert has_batchim("아스테르") is False          # 르 — 받침 없음
    assert has_batchim("사프라") is False
    assert has_batchim("선생") is True
    assert has_batchim("AZ") is None                # 한글이 아니면 판단 보류
    assert has_batchim("로시욘 저택") is True        # 마지막 한글 음절만 본다
    assert has_batchim("아스터 왕") is True
    print("selftest 통과")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "selftest":
        selftest()
    elif cmd == "check":
        sys.exit(cmd_check())
    elif cmd == "rename" and len(sys.argv) == 4:
        cmd_rename(sys.argv[2], sys.argv[3])
    elif cmd == "add" and len(sys.argv) >= 4:
        cmd_add(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
