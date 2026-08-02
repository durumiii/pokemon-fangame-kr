# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Pokemon Z korean.dat에 인명 확정 명단(names.json)을 적용한다.

절14(NPC명) 값 교체 + 절13 칭호 클래스 네 자리 + 한글 대사(절0·20·22·23) 속
라틴 이름 치환. 되쓰기는 fanlib rubywrite(CountingWriter)로만 하고, 파일에
쓰기 전에 왕복 재판독으로 편집 결과가 그대로 읽히는지 검증한다.

usage: uv run apply_names.py [--dry-run]
"""
import io
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from fanlib import rubywrite  # noqa: E402
from rubymarshal.reader import load  # noqa: E402

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
SPEC = Path(__file__).with_name("names.json")

HANGUL = re.compile(r"[가-힣]")
LATIN = "A-Za-zÀ-ÿ"
DIALOGUE_SECTIONS = (0, 20, 22, 23)


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def set_pairs(oh, keys, values):
    oh._private_data = rubywrite.dumps([keys, values])


def build_dialogue_regex(spec):
    excluded = set(spec["keep"]) | set(spec["fragments"])
    table = dict(spec["phrases"])
    table.update({k: v for k, v in spec["names"].items() if k not in excluded})
    alts = sorted(table, key=len, reverse=True)
    pat = re.compile(
        f"(?<![{LATIN}])(" + "|".join(re.escape(a) for a in alts) + f")(?![{LATIN}])"
    )
    return pat, table


def replace_dialogue(text, spec, pat, table, hits):
    for lit, rep in spec["dialogue_literals"].items():
        n = text.count(lit)
        if n:
            hits[lit] = hits.get(lit, 0) + n
            text = text.replace(lit, rep)

    def sub(m):
        hits[m.group(1)] = hits.get(m.group(1), 0) + 1
        return table[m.group(1)]

    return pat.sub(sub, text)


def main():
    dry = "--dry-run" in sys.argv
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    d = load(open(STORE, "rb"))

    # 절14: 명단과 실제 키가 정확히 일치해야 한다
    k14, v14 = inner_of(d[14])
    dat_keys = {k.decode("utf-8") for k in k14}
    map_keys = set(spec["names"]) | set(spec["keep"])
    missing = dat_keys - map_keys
    extra = map_keys - dat_keys
    if missing or extra:
        sys.exit(f"명단 불일치 — 명단에 없음: {sorted(missing)}\ndat에 없음: {sorted(extra)}")

    keep = set(spec["keep"])
    new_v14 = []
    for k in k14:
        name = k.decode("utf-8")
        new_v14.append(k if name in keep else spec["names"][name].encode("utf-8"))
    set_pairs(d[14], k14, new_v14)

    # 절13: 칭호 클래스 네 자리 (위치 목록)
    for idx, ko in spec["class_slots"].items():
        i = int(idx)
        print(f"절13[{i}]: {d[13][i].decode('utf-8')!r} → {ko!r}")
        d[13][i] = ko.encode("utf-8")

    # 대사: 한글 포함 값에서만 라틴 이름 치환
    pat, table = build_dialogue_regex(spec)
    hits = {}
    changed_values = 0
    for sec in DIALOGUE_SECTIONS:
        targets = d[sec] if sec == 0 else [d[sec]]
        for oh in targets:
            keys, values = inner_of(oh)
            dirty = False
            for i, v in enumerate(values):
                text = v.decode("utf-8")
                if not HANGUL.search(text):
                    continue
                new = replace_dialogue(text, spec, pat, table, hits)
                if new != text:
                    values[i] = new.encode("utf-8")
                    dirty = True
                    changed_values += 1
            if dirty:
                set_pairs(oh, keys, values)

    total = sum(hits.values())
    print(f"절14 교체: {len(k14) - len(keep)}건 (유지 {len(keep)}건)")
    print(f"대사 치환: 값 {changed_values}개에서 {total}회")
    top = sorted(hits.items(), key=lambda x: -x[1])[:15]
    print("상위:", ", ".join(f"{k}×{n}" for k, n in top))

    # 왕복 검증: 되쓴 바이트를 재판독해 편집 결과와 대조
    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    assert len(r) == len(d), "절 수 불일치"
    rk14, rv14 = inner_of(r[14])
    assert rk14 == k14 and rv14 == new_v14, "절14 왕복 불일치"
    for idx, ko in spec["class_slots"].items():
        assert r[13][int(idx)] == ko.encode("utf-8"), f"절13[{idx}] 왕복 불일치"
    for sec in DIALOGUE_SECTIONS:
        src = d[sec] if sec == 0 else [d[sec]]
        dst = r[sec] if sec == 0 else [r[sec]]
        assert len(src) == len(dst), f"절{sec} 길이 불일치"
        for a, b in zip(src, dst):
            assert inner_of(a) == inner_of(b), f"절{sec} 왕복 불일치"
    for sec in (1, 5, 12, 19):  # 손 안 댄 절 표본
        assert r[sec] == d[sec], f"절{sec}이 변했다"
    print(f"왕복 검증 통과 · 산출 {len(out):,} bytes")

    if dry:
        print("dry-run — 파일에 쓰지 않음")
        return
    backup = STORE.with_suffix(".dat.orig")
    if not backup.exists():
        shutil.copy2(STORE, backup)
        print(f"원본 백업: {backup}")
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
