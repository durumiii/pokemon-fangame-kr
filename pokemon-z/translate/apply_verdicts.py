# /// script
# requires-python = ">=3.12"
# ///
"""검수 판정을 번역 정본에 반영한다 — 선별분은 판정대로, 나머지는 새 번역으로.

    uv run translate/apply_verdicts.py <out-dir>          # 미리보기(쓰지 않는다)
    uv run translate/apply_verdicts.py <out-dir> --write  # 정본에 반영

판정 원장은 `<out-dir>`의 짝인 `verdicts-<out이름>.jsonl`. 자리마다 최종 한 줄이다.

반영 규칙 — **판정이 없으면 새 번역을 채택한다**(유지자 판정 2026-08-06: 선별 화면에서
고르지 않은 행은 새 번역으로 간다). 그 위에 안전판 셋:

- 기계 검증 반려(`ok:false`) 행은 현행을 지킨다. 판정으로 명시하면 그것이 이긴다.
- 승인 줄은 현행을 지킨다 — 이미 판정이 끝난 자리라 자동 채택 대상이 아니다.
- 「보류」와 「현행」은 손대지 않는다.

같은 (맵, 접힌 원문)이 여러 자리에 서면 정본은 한 줄뿐이다 — 그 열쇠에 판정이 둘 이상
엇갈리면 반영하지 않고 목록으로 보여 준다.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch_pages import BATCH, MAPS, fold  # noqa: E402

CHUNKS = BATCH / "page-chunks.jsonl"


def approved_ids():
    """이미 판정이 끝난 줄 — 자동 채택에서 뺀다."""
    out = set()
    if CHUNKS.exists():
        for line in CHUNKS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for r in json.loads(line)["rows"]:
                    if r.get("approved"):
                        out.add(r["id"])
    return out


def verdicts(path):
    """행 판정만 추린다 — 이벤트 승인 줄(`event` 열쇠)은 환류 몫이라 여기서 안 쓴다."""
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("id"):
                    out[r["id"]] = r
    return out


def decide(row, v, approved):
    """(새 번역문 또는 None, 사유) — None이면 현행 유지."""
    if v:
        j = (v.get("판정") or "").strip()
        if j == "B새번역":
            return row.get("new"), "판정:새번역"
        if j == "직접":
            t = (v.get("텍스트") or "").strip()
            return (t, "판정:직접") if t else (None, "판정:직접(빈칸)")
        if j == "현행":
            return None, "판정:현행"
        if j == "보류":
            return None, "판정:보류"
        # 고르지 않은 자리 — 메모를 남겼으면 물음이 걸려 있는 것이니 현행을 지킨다.
        # 메모도 없으면 고른 것을 도로 끈 자리라 무판정과 같게 본다.
        if (v.get("메모") or "").strip():
            return None, "메모만(물음 걸림)"
    if row["id"] in approved:
        return None, "승인 줄"
    if not row.get("ok"):
        return None, "기계 반려"
    if not row.get("new"):
        return None, "새 번역 없음"
    return row["new"], "무판정→새번역"


def run(out_dir, write=False):
    d = Path(out_dir)
    ledger = d.parent / f"verdicts-{d.name}.jsonl"
    vs, appr = verdicts(ledger), approved_ids()

    plan, why = {}, {}
    clash, stat = [], {}
    for fp in sorted(d.glob("p*.jsonl")):
        for line in fp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            new, tag = decide(r, vs.get(r["id"]), appr)
            stat[tag] = stat.get(tag, 0) + 1
            if new is None:
                continue
            key = (int(r["id"].split(":")[0]), fold(r["es"]))
            if key in plan and plan[key] != new:
                clash.append((key, why[key], plan[key], tag, new))
                continue
            plan[key], why[key] = new, tag

    for tag, n in sorted(stat.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {n}행")
    print(f"판정 원장 {len(vs)}건 · 반영 대상 {len(plan)}자리 · 열쇠 충돌 {len(clash)}")
    for key, t1, v1, t2, v2 in clash[:10]:
        print(f"  충돌 맵{key[0]} 「{key[1][:30]}」: {t1}={v1[:25]} / {t2}={v2[:25]}")

    if not write:
        print("미리보기만 — 반영하려면 --write")
        return

    out, hit, cur = [], 0, None
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            out.append(line)
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
        else:
            new = plan.get((cur, fold(r["k"])))
            if new and new != r["v"]:
                r["v"], hit = new, hit + 1
        out.append(json.dumps(r, ensure_ascii=False))
    MAPS.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"정본 {MAPS.name}: {hit}행 고침")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
        sys.exit()
    run(a[0], write="--write" in sys.argv)
