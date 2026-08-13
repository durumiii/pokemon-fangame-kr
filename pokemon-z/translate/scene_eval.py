# /// script
# requires-python = ">=3.12"
# ///
"""메인스토리 판별 신호를 블라인드 라벨로 채점한다 — 표본 뽑기와 채점 한 벌.

라벨은 `data/scene/labels.jsonl`에 라운드째로 쌓인다. 표본을 새로 뽑을 때
이미 라벨된 자리를 빼므로, 라운드를 거듭해도 같은 페이지를 두 번 안 준다.

    uv run translate/scene_eval.py sample 200 --round 4   # 블라인드 시트 만들기
    uv run translate/scene_eval.py score                  # 쌓인 라벨로 신호 채점
    uv run translate/scene_eval.py score --pool 버림      # 버리는 층만

⚠ 표본 시트에는 좌표와 원문만 싣는다 — 층·플래그·화자를 실으면 라벨이 오염되고
그 라운드는 통째로 못 쓴다. 라벨러에게 이 파일도 열지 말라고 일러라.
"""
import argparse
import gzip
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
ATTR = HERE / "data" / "speaker-attr.jsonl.gz"
SCENE = HERE / "data" / "scene"
LABELS = SCENE / "labels.jsonl"


def load_pages():
    """(맵, 이벤트, 페이지) → 행 목록. 귀속표가 대사 있는 페이지만 담는다."""
    pages = defaultdict(list)
    with gzip.open(ATTR, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            pages[(r["map"], r["event"], r["page"])].append(r)
    return pages


def load_register(name, verdict_key="판정"):
    path = SCENE / name
    return {r["id"]: r[verdict_key] for r in map(json.loads, path.open(encoding="utf-8"))}


def counter_pages():
    """창구 노릇이 그 페이지의 일인 자리 — 이벤트 명령의 기능 호출로 판정된다.

    이름표가 붙어도 상점·회복·보관·교환은 메인스토리가 아니다. 라벨 91건 대조에서
    이 목록 안에 메인스토리가 0건이라, 빼도 잃는 것이 없다(2026-08-14).
    """
    return {(r["map"], r["event"], r["page"])
            for r in map(json.loads, (SCENE / "counter-pages.jsonl").open(encoding="utf-8"))}


def story_var_pages():
    """본편 장면 카운터가 걸린 페이지 좌표."""
    out = set()
    for r in map(json.loads, (SCENE / "var-register.jsonl").open(encoding="utf-8")):
        if r["판정"] != "본편 장면":
            continue
        for key in ("조작자리", "소비자리"):
            for p in r.get(key) or []:
                if isinstance(p, dict) and p.get("맵") is not None:
                    out.add((p["맵"], p.get("이벤트"), p.get("페이지")))
    return out


# --- 신호 셋 ---------------------------------------------------------------
# 값을 고칠 때는 여기만 고친다. 신호를 고쳤으면 그 라운드의 라벨로 다시 재지 마라 —
# 고친 근거가 그 라벨에서 나왔으면 새 라운드를 뽑아야 한다.

def signals(rows, key, flags_reg, story):
    """플롯 신호는 **자리로 정해진다** — 값 하나가 아니라 그 페이지의 등재 값 전부를 본다.

    - `임시 플래그`는 장면 안에서만 도는 보조라 세지 않는다. 다만 **그 페이지의 등재
      플래그가 그것뿐이면** 그 플래그가 페이지 전체의 대표이므로 본편으로 본다
      (`Escena*` 컷신이 보조 하나만 켜는 자리가 그렇다).
    - `서브퀘스트`·`모드`는 메인스토리가 아니라 플롯 신호에서 뺀다. 값은 데이터에
      남으니 나중에 번역 프롬프트 재료로 쓴다.

    ⚠ 「단독인가」를 등재에 박지 마라 — 다른 플래그의 값이 바뀌면 동반이던 것이 단독이
    된다. 여기서 매번 다시 센다.
    """
    person = any(r["cls"] == "PS" for r in rows)
    fl = {f for r in rows for f in r["flags"]}
    vals = {v for f in fl if (v := flags_reg.get(f))}
    plot = "메인스토리" in vals or vals == {"임시 플래그"}
    return {"정본인물이 말한다": person,
            "본편플래그를 켠다": plot,
            "장면카운터가 걸렸다": key in story}


def stratum(key, rows):
    """맵 번호 구간 × 대사 줄 수 — 신호가 아니라 크기·위치 기준이라 오염이 없다."""
    m, n = key[0], len(rows)
    mb = 0 if m <= 100 else 1 if m <= 250 else 2 if m <= 380 else 3
    nb = 0 if n <= 2 else 1 if n <= 8 else 2
    return (mb, nb)


def read_labels():
    if not LABELS.exists():
        return {}
    out = {}
    for r in map(json.loads, LABELS.open(encoding="utf-8")):
        out[(r["map"], r["event"], r["page"])] = r["라벨"]
    return out


def cmd_sample(args):
    pages = load_pages()
    done = set(read_labels())
    pool = {k: v for k, v in pages.items() if k not in done}
    if args.pool == "버림":
        fr, st = load_register("flag-register.jsonl"), story_var_pages()
        pool = {k: v for k, v in pool.items() if not any(signals(v, k, fr, st).values())}

    by = defaultdict(list)
    for k, v in pool.items():
        by[stratum(k, v)].append(k)
    rng = random.Random(args.seed)
    picked = []
    floor = min(args.floor, args.n // max(len(by), 1))
    for s in sorted(by):
        rng.shuffle(by[s])
        picked += by[s][:floor]
    rest = [k for s in sorted(by) for k in by[s][floor:]]
    rng.shuffle(rest)
    picked += rest[: max(0, args.n - len(picked))]

    for k in picked:
        rows = sorted(pages[k], key=lambda r: r["cmd"])
        print(json.dumps({
            "map": k[0], "map_name": rows[0]["map_name"], "event": k[1], "page": k[2],
            "라운드": args.round,
            "대사": [r["k"] for r in rows],
        }, ensure_ascii=False))
    print(f"# 표본 {len(picked)}페이지 · 후보 {len(pool)} · seed {args.seed} · 라운드 {args.round}",
          file=sys.stderr)


def cmd_score(args):
    pages, labels = load_pages(), read_labels()
    if not labels:
        sys.exit("라벨이 없다 — 먼저 sample로 시트를 만들어 라벨을 붙여라.")
    fr, st, func = load_register("flag-register.jsonl"), story_var_pages(), counter_pages()

    pop = Counter(stratum(k, v) for k, v in pages.items())
    samp = Counter(stratum(k, pages[k]) for k in labels if k in pages)
    w = {s: pop[s] / samp[s] for s in samp}

    cells, raw = defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(int))
    for k, lb in labels.items():
        if k not in pages:
            continue
        s = signals(pages[k], k, fr, st)
        name = " × ".join(n for n, v in s.items() if v) or "(신호 없음)"
        cells[name][lb] += w[stratum(k, pages[k])]
        raw[name][lb] += 1

    print(f"{'칸':34s} {'M':>7s} {'X':>7s} {'?':>5s}   표본(M/전체)")
    for name in sorted(cells, key=lambda n: -sum(cells[n].values())):
        c, r = cells[name], raw[name]
        print(f"{name:34s} {c['M']:7.0f} {c['X']:7.0f} {c['?']:5.0f}"
              f"   {r['M']}/{sum(r.values())}")

    P, F, V = "정본인물이 말한다", "본편플래그를 켠다", "장면카운터가 걸렸다"
    combos = {
        "정본인물만 본다": lambda s, k: s[P],
        "본편플래그만 본다": lambda s, k: s[F],
        "장면카운터만 본다": lambda s, k: s[V],
        "셋 중 하나라도 서면": lambda s, k: any(s.values()),
        "★ 셋 중 하나 + 창구는 뺀다": lambda s, k: any(s.values()) and k not in func,
        "인물이 있고 플래그나 카운터도": lambda s, k: s[P] and (s[F] or s[V]),
    }
    print(f"\n{'게이트 규칙':34s} {'정밀도':>6s} {'재현율':>6s} {'놓친M':>7s} {'표본놓침':>8s}")
    for name, fn in combos.items():
        tp = fp = fn_ = 0.0
        missed = 0
        for k, lb in labels.items():
            if k not in pages or lb == "?":
                continue
            ww, hit = w[stratum(k, pages[k])], fn(signals(pages[k], k, fr, st), k)
            if lb == "M" and hit:
                tp += ww
            elif hit:
                fp += ww
            elif lb == "M":
                fn_ += ww
                missed += 1
        pr = tp / (tp + fp) if tp + fp else 0
        rc = tp / (tp + fn_) if tp + fn_ else 0
        print(f"{name:34s} {pr:6.2f} {rc:6.2f} {fn_:7.0f} {missed:8d}")
    print("\n★ 이것이 현행 게이트다 — 신호 셋 중 하나라도 서되, 상점·회복·보관 같은 창구"
          "\n  (`counter-pages.jsonl`)는 뺀다. 바로 위 줄이 빼기 전 값이니 견주면 실효가 보인다.")
    print("\n⚠ 「놓친M」은 모집단 추정치다. 옆의 「표본놓침」이 그 추정을 떠받치는 실제 관측 수이고,"
          "\n  그 수가 한 자리면 재현율은 사실상 안 재인 것이다.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample", help="블라인드 시트를 뽑는다 (좌표+원문만)")
    s.add_argument("n", type=int)
    s.add_argument("--seed", type=int, default=20260814)
    s.add_argument("--round", type=int, default=4)
    s.add_argument("--floor", type=int, default=20, help="층마다 최소 몇 개")
    s.add_argument("--pool", choices=["전체", "버림"], default="전체")
    s.set_defaults(fn=cmd_sample)
    c = sub.add_parser("score", help="쌓인 라벨로 신호를 채점한다")
    c.set_defaults(fn=cmd_score)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
