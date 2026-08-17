# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""걸음 5의 두 소배치 — ① 절23 가시 미번역 새 번역, ② 설명문 절 다듬기.

① 미번역(한글 없는 행) 중 게임 스크립트가 실제로 부르는 것만 새로 번역한다.
   가시 판별은 말뭉치 조사(2026-08-02-z-corpus-survey.md)와 같은 방법 —
   Scripts.rxdata(본편)·EditorScripts.rxdata(에디터)를 풀어 통째 검색, 자리표는
   끊어서 가장 긴 8자 이상 조각으로. 본편·양쪽·판정 불가(4자 미만)만 태운다.
② 설명문 절(3 도감·6 기술·9 도구·11 특성·20 지명)의 한글 행을 도감체 프롬프트로
   다듬는다. 초벌 배치에서 「대사용 프롬프트와 결이 다르다」고 뺀 자리다.

모델·게이트·진행 기록 규약은 batch.py와 같다(gemini-3.6-flash minimal, validate 7종,
fill/out/<cid>.jsonl 원자 저장·재개).

usage:
  uv run fill.py plan
  uv run fill.py run [--workers 4]
  uv run fill.py status
  uv run fill.py apply
"""
import io
import json
import re
import sys
import threading
import time
import zlib
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
LEDGER = HERE.parent / "docs" / "ledger"   # 판정 대장 (glossary·voices)
FILL = HERE / "fill"
OUT = FILL / "out"
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
CHUNK = 40
DESC_SECS = {3: "03-entries", 6: "06-move-descs", 9: "09-item-descs",
             11: "11-ability-descs", 20: "20-place-descs"}

sys.path.insert(0, str(HERE))
from batch import HAN, key_of, or_extras, read_jsonl, worth_rewriting  # noqa: E402
from validate import check  # noqa: E402

URL = "https://api.llmgateway.io/v1/chat/completions"
MODEL = "gemini-3.6-flash"

PROMPT_NEW = """스페인어 포켓몬 팬게임의 시스템 문구를 한국어로 새로 번역한다.
원문은 스페인어이고 일부는 영어다. 규칙:

- 시스템 문구는 합쇼체(~합니다/~하십시오)가 기본이다. 짧은 라벨(단어 하나)은 명사형 그대로.
- 포켓몬 시리즈 용어는 한국어 정식 발매판 명칭을 쓴다(배지·기술머신·포켓몬센터 등).
- 마크업과 자리표를 한 글자도 빠뜨리지 마라: \\c[n]·\\PN·\\v[n]·{1}·{1:02d}·<ac> 류는
  원문 그대로 보존한다.
- 고유명사(인명 Bill 등 로마자 이름)는 음차한다(Bill→빌).
- 번역이 불가능하거나 식별자로 보이면(예: 변수명) 원문을 그대로 돌려줘라.

[용어 규칙]
{GLOSSARY}

출력은 JSON 배열만: [{"id": "<id>", "ko": "<번역>"}] — 모든 행에 하나씩. 코드펜스 금지."""

PROMPT_DESC = """포켓몬 팬게임의 설명문(도감 항목·기술 설명·도구 설명·특성 설명·지명 설명)
한국어 번역을 다듬는다. 이미 번역돼 있고, 직역투와 어색한 문장만 고친다. 규칙:

- 문체는 간결한 평서형(~다)이다. 도감체 — 본가 게임의 설명문 문체를 따른다.
- 뜻을 더하거나 빼지 마라. 원문(es)에 없는 수식을 넣지 마라.
- 길이를 늘리지 마라 — 설명문은 UI 칸에 들어가므로 현행보다 짧거나 같은 것이 좋다.
- 마크업·자리표({1} 류)는 그대로 보존한다.
- 이미 자연스러우면 현행 그대로 돌려줘라.

[용어 규칙]
{GLOSSARY}

출력은 JSON 배열만: [{"id": "<id>", "ko": "<다듬은 번역>"}] — 모든 행에 하나씩. 코드펜스 금지."""

PLACEHOLDER = re.compile(r"\{\d+[^}]*\}|\\[A-Za-z]+\[[^\]]*\]|\\PN|<[^>]+>")


def scripts_text() -> tuple[str, str]:
    from datread import load
    texts = []
    for fname in ("Scripts.rxdata", "EditorScripts.rxdata"):
        arr = load(io.BytesIO((GAME / fname).read_bytes()))
        buf = []
        for entry in arr:
            blob = entry[2]
            data = bytes(blob._private_data if hasattr(blob, "_private_data") else blob)
            buf.append(zlib.decompress(data).decode("utf-8", "replace"))
        texts.append("\n".join(buf))
    return texts[0], texts[1]


def visible_in(text_main: str, text_editor: str, s: str) -> str:
    probe = s
    if PLACEHOLDER.search(s):
        frags = [f for f in PLACEHOLDER.split(s) if len(f) >= 8]
        if not frags:
            return "short"
        probe = max(frags, key=len)
    elif len(s) < 4:
        return "short"
    m, e = probe in text_main, probe in text_editor
    if m:
        return "main"
    if e:
        return "editor"
    return "dead"


def plan():
    FILL.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    chunks = []

    print("게임 스크립트 판독 중 (가시 판별)...")
    main_t, editor_t = scripts_text()
    rows23 = read_jsonl(HERE / "ko" / "23-script-texts.jsonl")
    new_rows, vis_count = [], Counter()
    for j, d in enumerate(rows23):
        v = d.get("v", "")
        if not v or HAN.search(v):
            continue
        w = visible_in(main_t, editor_t, d["k"])
        vis_count[w] += 1
        if w in ("main", "short"):
            new_rows.append({"id": f"s23:{j}", "es": d["k"]})
    print(f"절23 미번역 분류: {dict(vis_count)} → 새 번역 대상 {len(new_rows)}행")
    for i in range(0, len(new_rows), CHUNK):
        chunks.append({"cid": f"u{i // CHUNK:03d}", "kind": "new", "sec": 23,
                       "rows": new_rows[i:i + CHUNK]})

    for sec, stem in DESC_SECS.items():
        # 설명문 절은 인덱스 조인({"i", "v", "es"}) — 절0·23의 {"k", "v"}와 모양이 다르다
        rows = [{"id": f"s{sec}:{d['i']}", "es": d.get("es", ""), "ko": d["v"]}
                for d in read_jsonl(HERE / "ko" / f"{stem}.jsonl")
                if HAN.search(d.get("v", "")) and worth_rewriting(d["v"])]
        for i in range(0, len(rows), CHUNK):
            chunks.append({"cid": f"d{sec:02d}-{i // CHUNK:03d}", "kind": "desc",
                           "sec": sec, "rows": rows[i:i + CHUNK]})

    with open(FILL / "chunks.jsonl", "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    n_new = sum(len(c["rows"]) for c in chunks if c["kind"] == "new")
    n_desc = sum(len(c["rows"]) for c in chunks if c["kind"] == "desc")
    print(f"청크 {len(chunks)}개 — 새 번역 {n_new:,}행 · 설명문 {n_desc:,}행")


def build_prompt(kind):
    gloss = (LEDGER / "glossary.md").read_text(encoding="utf-8")
    tpl = PROMPT_NEW if kind == "new" else PROMPT_DESC
    return tpl.replace("{GLOSSARY}", gloss)


def ask(key, prompt, rows, attempt=0):
    import urllib.request
    payload = {"model": MODEL, "temperature": 0.3, "reasoning_effort": "minimal",
               "messages": [{"role": "system", "content": prompt},
                            {"role": "user", "content": json.dumps(rows, ensure_ascii=False)}],
               **or_extras()}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.load(r)
        text = body["choices"][0]["message"]["content"]
        cost = float(body.get("usage", {}).get("cost") or 0)
        m = re.search(r"\[.*\]", text, re.S)
        arr = json.loads(m.group(0))
        return {str(a["id"]): a["ko"] for a in arr
                if isinstance(a, dict) and isinstance(a.get("ko"), str)}, cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, prompt, rows, attempt + 1)
        return {"__error__": type(e).__name__}, 0.0


def run(workers=4):
    key = key_of()
    chunks = read_jsonl(FILL / "chunks.jsonl")
    pending = [c for c in chunks if not (OUT / (c["cid"] + ".jsonl")).exists()]
    total = sum(len(c["rows"]) for c in pending)
    print(f"대기 {len(pending)}청크 · {total:,}행")
    if not pending:
        return
    lock = threading.Lock()
    state = {"rows": 0, "n": 0, "cost": 0.0, "rej": 0, "t0": time.time()}

    def work(c):
        prompt = build_prompt(c["kind"])
        got, cost = ask(key, prompt, c["rows"])
        err = got.pop("__error__", None)
        missing = [r for r in c["rows"] if r["id"] not in got]
        if missing and not err:
            got2, c2 = ask(key, prompt, missing)
            got2.pop("__error__", None)
            got.update(got2)
            cost += c2
        out = []
        rej = 0
        for r in c["rows"]:
            ko = got.get(r["id"])
            base = r.get("ko") or r["es"]  # 새 번역은 원문 기준으로 게이트
            if ko is None:
                out.append({"id": r["id"], "ko": base, "ok": False, "why": err or "누락"})
                rej += 1
                continue
            bad = check(base, ko, c["sec"])
            if bad:
                out.append({"id": r["id"], "ko": ko, "ok": False, "why": " | ".join(bad)})
                rej += 1
            else:
                out.append({"id": r["id"], "ko": ko, "ok": True,
                            "same": ko == r.get("ko")})
        tmp = OUT / (c["cid"] + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps({"cid": c["cid"], "cost": cost}, ensure_ascii=False) + "\n")
            for row in out:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        tmp.rename(OUT / (c["cid"] + ".jsonl"))
        with lock:
            state["rows"] += len(c["rows"])
            state["n"] += 1
            state["cost"] += cost
            state["rej"] += rej
            el = time.time() - state["t0"]
            rate = state["rows"] / el if el else 0
            eta = (total - state["rows"]) / rate if rate else 0
            print(f"[{state['n']}/{len(pending)} {state['rows']:,}/{total:,}행"
                  f" | ETA {int(eta // 60)}m | ${state['cost']:.2f}"
                  f" | 반려 {state['rej']}] {c['cid']}", flush=True)

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, pending))
    print(f"끝. 반려 {state['rej']}행, 실비용 ${state['cost']:.2f}")


def status():
    chunks = read_jsonl(FILL / "chunks.jsonl")
    ok = rej = same = 0
    cost = 0.0
    done = 0
    for c in chunks:
        p = OUT / (c["cid"] + ".jsonl")
        if not p.exists():
            continue
        done += 1
        rows = read_jsonl(p)
        cost += rows[0].get("cost", 0)
        for r in rows[1:]:
            if r["ok"]:
                ok += 1
                same += bool(r.get("same"))
            else:
                rej += 1
    print(f"청크 {done}/{len(chunks)} · 통과 {ok:,}(무변경 {same:,}) · 반려 {rej:,} · ${cost:.2f}")


def apply():
    accepted = {}
    for p in sorted(OUT.glob("*.jsonl")):
        for r in read_jsonl(p)[1:]:
            if r["ok"] and not r.get("same"):
                accepted[r["id"]] = r["ko"]
    changed = 0
    files = {23: "23-script-texts.jsonl", **{s: f"{stem}.jsonl" for s, stem in DESC_SECS.items()}}
    for sec, fname in files.items():
        path = HERE / "ko" / fname
        rows = read_jsonl(path)
        for j, d in enumerate(rows):
            rid = f"s{sec}:{d['i']}" if "i" in d else f"s{sec}:{j}"
            ko = accepted.get(rid)
            if ko is not None and d.get("v") != ko:
                d["v"] = ko
                changed += 1
        path.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in rows) + "\n",
                        encoding="utf-8")
    print(f"정본 반영 {changed:,}행. 다음: uv run build.py")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    a = sys.argv[2:]
    if cmd == "plan":
        plan()
    elif cmd == "run":
        run(workers=int(a[a.index("--workers") + 1]) if "--workers" in a else 4)
    elif cmd == "status":
        status()
    elif cmd == "apply":
        apply()
    else:
        print(__doc__)
