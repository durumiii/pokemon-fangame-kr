# /// script
# requires-python = ">=3.12"
# ///
"""도감 분류·설명을 한국어 정식판 텍스트로 갈아 끼우는 제안 파일 생성기.

Z 팬게임 한글패치의 02-kinds / 03-entries에는 본가에서 복사된 행과 창작 행이
섞여 있다. 원문(es 칸, 실제로는 영어·스페인어 혼합)을 PokéAPI 원천 CSV의
en(9)/es(7) 텍스트와 대조해 본가 복사본을 식별하고, 같은 자리의 ko(3)를 제안한다.

**정본 ko/는 절대 건드리지 않는다.** 산출은 reference/dexswap-proposed-*.jsonl뿐.

주의: 이 게임의 종 인덱스는 전국도감 번호가 아니다(1,019행 중 102행이 어긋나고
24행은 창작종). 그래서 01-species.jsonl의 영문·스페인어 이름으로 species_id를
조인한다.

usage:
  uv run dexswap.py plan
  uv run dexswap.py stats
"""
import csv
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
KO = HERE / "ko"
OUT = HERE / "reference"
CACHE = Path(
    "/tmp/claude-1000/-home-durumii-workspace-claude-native-sketches-poke-essentials"
    "/41d564b2-c839-444b-a189-aa5e76642cc9/scratchpad/pokeapi"
)
BASE = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"
FILES = [
    "pokemon_species_names.csv",
    "pokemon_species_flavor_text.csv",
    "version_names.csv",
]
EN, ES, KOR = "9", "7", "3"


def csv_rows(name):
    p = CACHE / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(BASE + name, p)
    with p.open(encoding="utf-8") as f:
        yield from csv.DictReader(f)


def jsonl(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def fold(s):
    """이름 대조용: 악센트·기호·대소문자를 지운다 (Flabébé == Flabebe)."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def norm_text(s):
    """본문 대조용: 개행·특수공백을 공백 하나로 접고 따옴표를 통일한다."""
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("­", "").replace("\x0c", " ")
    s = s.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"}))
    return re.sub(r"\s+", " ", s).strip()


def match_key(s):
    """대조 전용 열쇠: 악센트와 공백을 아예 지운다.

    원문은 게임 화면 폭에 맞춰 줄바꿈돼 있어 낱말 가운데(small-\nbodied)에도
    개행이 들어간다. 공백을 하나로 접는 것만으론 그 자리가 안 맞는다.
    """
    s = unicodedata.normalize("NFKD", norm_text(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", "", s).casefold()


def strip_suffix(genus, words):
    """분류에서 꼬리를 뗀다. 한국어는 붙여 쓰고(씨앗포켓몬) 영어는 띄어 쓴다(Seed Pokémon)."""
    g = norm_text(genus)
    for w in words:
        if g.lower().endswith(w.lower()):
            return g[: -len(w)].strip()
    return g


def load_sources():
    names, genus, ko_name = {}, {}, {}
    for r in csv_rows("pokemon_species_names.csv"):
        sid, lang = int(r["pokemon_species_id"]), r["local_language_id"]
        if lang in (EN, ES):
            names.setdefault(fold(r["name"]), set()).add(sid)
        if lang in (EN, ES, KOR):
            genus[(sid, lang)] = r["genus"]
        if lang == KOR:
            ko_name[sid] = r["name"]

    flavor = {}  # (sid, lang) -> [(version_id, text)]
    for r in csv_rows("pokemon_species_flavor_text.csv"):
        if r["language_id"] in (EN, ES, KOR):
            flavor.setdefault((int(r["species_id"]), r["language_id"]), []).append(
                (int(r["version_id"]), r["flavor_text"])
            )

    vname = {}
    for r in csv_rows("version_names.csv"):
        if r["local_language_id"] == EN:
            vname[int(r["version_id"])] = r["name"]
    return names, genus, ko_name, flavor, vname


def species_map(names):
    """게임 인덱스 i -> PokéAPI species_id. 이름이 없거나 창작종이면 빠진다."""
    out, unmatched = {}, []
    for row in jsonl(KO / "01-species.jsonl"):
        i, key = row["i"], fold(row.get("es", ""))
        cands = names.get(key)
        if not cands:
            if key:
                unmatched.append((i, row.get("es")))
            continue
        out[i] = i if i in cands else sorted(cands)[0]  # 동명이인은 인덱스 일치를 우선
    return out, unmatched


def plan():
    names, genus, ko_name, flavor, vname = load_sources()
    sid_of, unmatched = species_map(names)
    OUT.mkdir(exist_ok=True)

    # --- 분류 ---
    kinds = []
    for row in jsonl(KO / "02-kinds.jsonl"):
        sid, cur = sid_of.get(row["i"]), row.get("v", "")
        src = norm_text(row.get("es", ""))
        if not sid or not src or not cur:
            continue
        ko_raw = norm_text(genus.get((sid, KOR), ""))
        # 꼬리가 '포켓몬'이 아니면 원천 자료가 깨진 것이다(실측 1건: '침붕포켓몬몬').
        # 잘못 뗀 값을 내놓느니 건너뛴다.
        ko_g = strip_suffix(ko_raw, ["포켓몬"]) if ko_raw.endswith("포켓몬") else ""
        if not ko_g:
            continue
        refs = {
            lang: strip_suffix(genus.get((sid, lang), ""), ["Pokémon", "Pokemon"])
            for lang in (EN, ES)
        }
        have = [v for v in refs.values() if v]
        if match_key(src) in {match_key(v) for v in have}:
            match = "exact"
        elif not have or not refs[ES]:
            # PokéAPI에 그 언어의 분류가 아예 없다(9세대 스페인어가 통째로 빈다).
            # 원문이 본가 것인지 확인할 길이 없으므로 제안하되 등급을 내린다.
            match = "fallback"
        else:
            continue  # 원본이 있는데 다르다 = 창작이거나 손본 것
        if ko_g != cur:
            kinds.append({"i": row["i"], "old": cur, "new": ko_g, "ko_name": ko_name.get(sid, ""),
                          "match": match})
    write_jsonl(OUT / "dexswap-proposed-kinds.jsonl", kinds)

    # --- 설명 ---
    entries = []
    for row in jsonl(KO / "03-entries.jsonl"):
        sid, cur = sid_of.get(row["i"]), row.get("v", "")
        src = norm_text(row.get("es", ""))
        if not sid or not src or not cur:
            continue
        # 같은 원문이 여러 판본에 그대로 실린다. 한국어가 있는 판본을 골라야
        # 헛되이 fallback으로 떨어지지 않는다.
        hits = {
            v
            for lang in (EN, ES)
            for v, t in flavor.get((sid, lang), [])
            if match_key(t) == match_key(src)
        }
        if not hits:
            continue
        ko_flavors = dict(flavor.get((sid, KOR), []))
        shared = hits & ko_flavors.keys()
        if shared:
            ver, match = max(shared), "exact"
        elif ko_flavors:
            ver, match = max(ko_flavors), "fallback"
        else:
            continue
        new = norm_text(ko_flavors[ver])
        if new != cur:
            entries.append({"i": row["i"], "old": cur, "new": new, "ko_name": ko_name.get(sid, ""),
                            "version": vname.get(ver, str(ver)), "match": match})
    write_jsonl(OUT / "dexswap-proposed-entries.jsonl", entries)

    print(f"종 조인: {len(sid_of)}/1019, 미매칭 {len(unmatched)}건 {unmatched[:5]}")
    print(f"분류 제안 {len(kinds)}행 -> {OUT / 'dexswap-proposed-kinds.jsonl'}")
    print(f"설명 제안 {len(entries)}행 -> {OUT / 'dexswap-proposed-entries.jsonl'}")


def stats():
    import collections

    for label, path in (("분류", "dexswap-proposed-kinds.jsonl"),
                        ("설명", "dexswap-proposed-entries.jsonl")):
        rows = jsonl(OUT / path)
        total = sum(1 for r in jsonl(KO / ("02-kinds.jsonl" if label == "분류" else "03-entries.jsonl"))
                    if r.get("v"))
        c = collections.Counter(r["match"] for r in rows)
        print(f"\n== {label}: 원본 {total}행 중 제안 {len(rows)}행 "
              f"({len(rows) / total:.1%}) — exact {c['exact']}, fallback {c['fallback']}")
        if label == "설명":
            vc = collections.Counter(r["version"] for r in rows)
            print("  버전별 상위 5:", vc.most_common(5))
        for r in rows[:5]:
            print(f"  #{r['i']} {r['ko_name']}: {r['old'][:40]!r} -> {r['new'][:40]!r}")


def demo():
    assert fold("Flabébé") == fold("Flabebe") == "flabebe"
    assert fold("Farfetch'd") == "farfetchd"
    assert norm_text("A strange\nseed  was\x0cplanted.") == "A strange seed was planted."
    assert strip_suffix("Seed Pokémon", ["Pokémon"]) == "Seed"
    assert match_key("these Pokemon were") == match_key("these Pokémon  were")
    assert match_key("small-\nbodied POKéMON") == match_key("small-bodied Pokémon")
    assert strip_suffix("씨앗포켓몬", ["포켓몬"]) == "씨앗"
    print("ok")


if __name__ == "__main__":
    {"plan": plan, "stats": stats, "demo": demo}[sys.argv[1] if len(sys.argv) > 1 else "plan"]()
