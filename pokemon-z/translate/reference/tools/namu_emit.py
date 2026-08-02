# /// script
# dependencies = []
# ///
"""Normalize namuwiki version labels and emit namudex.jsonl + report."""
import json, re, sys, collections, importlib.util

spec = importlib.util.spec_from_file_location("nd", "namu_dex.py")
nd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nd)

# Label vocabulary induced from the dump (see report for counts).
MAP = {
    "적/녹/FR": ["red", "green", "firered"], "적/녹": ["red", "green"],
    "청/LG": ["blue", "leafgreen"], "청": ["blue"],
    "피카츄": ["yellow"],
    "레츠고! 피카츄/이브이": ["lets-go-pikachu", "lets-go-eevee"],
    "레츠고 피카츄": ["lets-go-pikachu"], "레츠고 이브이": ["lets-go-eevee"],
    "금/HG": ["gold", "heartgold"], "은/SS": ["silver", "soulsilver"],
    "금": ["gold"], "은": ["silver"], "크리스탈": ["crystal"],
    "금/하트골드": ["gold", "heartgold"], "은/소울실버": ["silver", "soulsilver"],
    "하트골드": ["heartgold"], "소울실버": ["soulsilver"],
    "HGSS": ["heartgold", "soulsilver"],
    "하트골드/소울실버": ["heartgold", "soulsilver"],
    "하트골드·소울실버": ["heartgold", "soulsilver"],
    "2세대": ["gold", "silver", "crystal"],
    "루비/OR": ["ruby", "omega-ruby"], "사파이어/AS": ["sapphire", "alpha-sapphire"],
    "루비": ["ruby"], "사파이어": ["sapphire"], "에메랄드": ["emerald"],
    "OR": ["omega-ruby"], "AS": ["alpha-sapphire"],
    "오메가루비": ["omega-ruby"], "알파사파이어": ["alpha-sapphire"],
    "오메가루비/알파사파이어": ["omega-ruby", "alpha-sapphire"],
    "ORAS": ["omega-ruby", "alpha-sapphire"],
    "RSE": ["ruby", "sapphire", "emerald"],
    "RSE/ORAS": ["ruby", "sapphire", "emerald", "omega-ruby", "alpha-sapphire"],
    "3세대": ["ruby", "sapphire", "emerald"],
    "루비/사파이어": ["ruby", "sapphire"],
    "파이어레드": ["firered"], "리프그린": ["leafgreen"],
    "FR": ["firered"], "LG": ["leafgreen"],
    "FR/LG": ["firered", "leafgreen"], "FRLG": ["firered", "leafgreen"],
    "파이어레드/리프그린": ["firered", "leafgreen"],
    "디아루가": ["diamond"], "디이루가": ["diamond"], "다이아몬드": ["diamond"],
    "펄기아": ["pearl"], "펄": ["pearl"],
    "디아루가/펄기아": ["diamond", "pearl"],
    "기라티나": ["platinum"], "플라티나": ["platinum"],
    "DPPt": ["diamond", "pearl", "platinum"],
    "DP": ["diamond", "pearl"],
    "4세대": ["diamond", "pearl", "platinum"],
    "블랙": ["black"], "화이트": ["white"],
    "블랙 2": ["black-2"], "화이트 2": ["white-2"],
    "블랙2": ["black-2"], "화이트2": ["white-2"],
    "블랙/화이트": ["black", "white"], "BW": ["black", "white"],
    "BW2": ["black-2", "white-2"], "블랙·화이트 2": ["black-2", "white-2"],
    "블랙 2/화이트 2": ["black-2", "white-2"],
    "BW/BW2": ["black", "white", "black-2", "white-2"],
    "5세대": ["black", "white", "black-2", "white-2"],
    "X": ["x"], "Y": ["y"], "XY": ["x", "y"],
    "썬": ["sun"], "문": ["moon"], "울트라썬": ["ultra-sun"], "울트라문": ["ultra-moon"],
    "썬/문": ["sun", "moon"], "울트라썬/울트라문": ["ultra-sun", "ultra-moon"],
    "USUM": ["ultra-sun", "ultra-moon"], "7세대": ["sun", "moon", "ultra-sun", "ultra-moon"],
    "소드": ["sword"], "실드": ["shield"], "소드/실드": ["sword", "shield"],
    "적/녹/FR/썬": ["red", "green", "firered", "sun"],
    "다이아몬드/펄": ["diamond", "pearl"], "디아루가·펄기아": ["diamond", "pearl"],
    "펄/플라티나": ["pearl", "platinum"],
    "금/HG/LG": ["gold", "heartgold", "leafgreen"],
    "은/SS/FR": ["silver", "soulsilver", "firered"],
    "포켓몬 GO": ["go"], "포켓몬GO": ["go"], "GO": ["go"],
}

NOTE = re.compile(r"^(.*?)\s*[\n(]\s*\(?([^)]*)\)?\s*$", re.S)


def split_note(label):
    """'소드\\n(갑옷섬)' -> ('소드', '갑옷섬'); '소드' -> ('소드', None)."""
    lab = re.sub(r"\s*/\s*", "/", label.replace("\n", " ").strip())
    m = re.match(r"^(.*?)\s*\((.*)\)+\s*$", lab)
    if m:
        return m.group(1).strip(), m.group(2).strip(") ")
    return lab, None


def main(src, out_jsonl, out_report):
    rows, bads, labels = nd.parse_all(src)
    unknown = collections.Counter()
    used = collections.Counter()
    seen = set()
    emitted = []
    for r in rows:
        if r["species"] <= 0:
            continue
        base, note = split_note(r["raw_label"])
        if r.get("form"):
            note = f"{r['form']}/{note}" if note else r["form"]
        vers = MAP.get(base)
        if not vers:
            unknown[r["raw_label"]] += 1
            continue
        used[base] += 1
        for v in vers:
            key = (r["species"], v, note)
            if key in seen:
                continue
            seen.add(key)
            e = {"species": r["species"], "version": v, "ko": r["ko"],
                 "source_name": "fan_wiki_namuwiki_20210301", "title": r["title"]}
            if note:
                e["note"] = note
            emitted.append(e)
    emitted.sort(key=lambda e: (e["species"], e["version"], e.get("note") or ""))
    with open(out_jsonl, "w") as f:
        for e in emitted:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    per_ver = collections.Counter(e["version"] for e in emitted if "note" not in e)
    sp_per_ver = collections.defaultdict(set)
    for e in emitted:
        if "note" not in e:
            sp_per_ver[e["version"]].add(e["species"])
    with open(out_report, "w") as f:
        w = f.write
        w("# namudex — 나무위키 도감 설명 추출 보고\n\n")
        w(f"- 원본: HuggingFace `heegyu/namuwiki` / `namuwiki_20210301.parquet` (문서 867,024개)\n")
        w(f"- 종 이름 후보로 걸러낸 문서 1,147개 중 `[anchor(앵커-도감 설명)]`을 가진 문서 541개\n")
        w(f"- 파싱 성공 문서 {len({r['title'] for r in rows})}개, 원시 행 {len(rows)}개, 전개 후 {len(emitted)}행\n")
        w(f"- 종 수 {len({e['species'] for e in emitted})} (도감번호 기준)\n\n")
        w("## 판본별 커버리지 (폼 주석 없는 행만)\n\n| 판본 | 종 수 |\n|---|---|\n")
        for v, s in sorted(sp_per_ver.items(), key=lambda kv: -len(kv[1])):
            w(f"| {v} | {len(s)} |\n")
        w("\n## 판본 라벨 사전 (원문 → 전개)\n\n| 원문 라벨 | 등장 | 전개 |\n|---|---|---|\n")
        for lab, n in used.most_common():
            w(f"| `{lab}` | {n} | {', '.join(MAP[lab])} |\n")
        if unknown:
            w("\n## 미매핑 라벨 (버려진 행)\n\n| 라벨 | 행 수 |\n|---|---|\n")
            for lab, n in unknown.most_common(40):
                w(f"| `{lab.replace(chr(10), ' / ')}` | {n} |\n")
        w("\n## 파싱 실패 유형\n\n| 유형 | 건수 | 설명 |\n|---|---|---|\n")
        c = collections.Counter(b[1] for b in bads)
        desc = {"header": "폼 전용 절 머리(메가·지우개굴닌자 등) — 도감번호가 없어 종을 못 붙임",
                "no-species": "위 머리 실패로 종이 안 잡힌 상태의 데이터 행",
                "empty": "본문 칸이 비어 있는 행(예: `포켓몬 GO` 미기재)"}
        for k, n in c.most_common():
            w(f"| {k} | {n} | {desc.get(k, '')} |\n")
        miss = [i for i in range(1, 899)
                if i not in {e["species"] for e in emitted if "note" not in e}]
        w("\n## 한계\n\n")
        w("- 덤프 시점이 **2021-03-01**이다. `heegyu/namuwiki`에 올라온 원본 스냅숏이 그것 하나뿐이라\n")
        w("  요청받은 2022년판이 아니다. 그래서 `source_name`은 `fan_wiki_namuwiki_20210301`으로 적었다.\n")
        w("- 도감번호 899 이상(9세대·전설의섬 이후 추가분)은 덤프에 문서가 없다.\n")
        w(f"- 898 이하인데 빠진 종 {len(miss)}개: " + ", ".join(f"{i}" for i in miss) + "\n")
        w("  대부분 절 머리가 도감번호 없이 폼 이름(우라오스 일격의 태세 등)으로만 서 있어 종을 못 붙인 것이다.\n")
        w("  140 투구는 투구푸스 문서 안에서 머리 없이 첫 블록으로 들어 있어 오귀속을 피하려고 버렸다.\n")
        w("- `note`가 붙은 행은 폼 한정 설명이다(메가·거다이맥스·지역폼·크기폼 등).\n")
        w("  같은 (종, 판본)에 주석 없는 행이 이미 있으면 그쪽이 기본형이다.\n")
        w("- 텍스트는 공식 전사와 팬 번역이 섞여 있다. 나무위키 원문 그대로이고 검수하지 않았다.\n")
        w("\n## 재현\n\n```sh\n")
        w("uv run --with huggingface_hub python -c \"from huggingface_hub import hf_hub_download as d; print(d('heegyu/namuwiki','namuwiki_20210301.parquet',repo_type='dataset'))\"\n")
        w("uv run namu_filter.py <parquet> namu_poke.jsonl   # 제목 필터\n")
        w("uv run namu_emit.py namu_poke.jsonl namudex.jsonl namudex-report.md\n```\n")
        w("\n스크립트 사본: `mod/z/translate/reference/tools/`\n")
    print("emitted", len(emitted), "species", len({e['species'] for e in emitted}))
    for v in ("emerald", "diamond", "white"):
        print(v, len(sp_per_ver[v]))
    print("unknown labels", sum(unknown.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
