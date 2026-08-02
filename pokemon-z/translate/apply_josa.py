# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""korean.dat의 조사 병기 「(은)는」류를 Josa Select 문법 \\j[…]로 바꾼다.

Josa Select 모드가 주입돼 있어야 화면에서 해석된다 — 모드 없이 이 변환만
하면 대사에 \\j[은,는]가 그대로 보이니 주의. 되쓰기 규율은 apply_names.py와
같다(왕복 검증 통과 후에만 기록).

usage: uv run apply_josa.py [--dry-run]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from fanlib import rubywrite  # noqa: E402
from rubymarshal.reader import load  # noqa: E402

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
SECTIONS = (0, 20, 22, 23)

# 병기 → \j[받침형,무받침형]. 괄호가 앞뒤 어느 쪽에 붙는 꼴이든 잡는다.
CONVERSIONS = {
    "(은)는": "\\j[은,는]",
    "(이)가": "\\j[이,가]",
    "(을)를": "\\j[을,를]",
    "(와)과": "\\j[과,와]",
    "(으)로": "\\j[으로,로]",
    "(이)야": "\\j[이야,야]",
    "은(는)": "\\j[은,는]",
    "이(가)": "\\j[이,가]",
    "을(를)": "\\j[을,를]",
    "와(과)": "\\j[과,와]",
    "과(와)": "\\j[과,와]",
    "로(으로)": "\\j[으로,로]",
    "(이)라는": "\\j[이라는,라는]",
    "(이)군요": "\\j[이군요,군요]",
}


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def main():
    dry = "--dry-run" in sys.argv
    d = load(open(STORE, "rb"))
    counts = {}
    changed_values = 0
    for sec in SECTIONS:
        targets = d[sec] if sec == 0 else [d[sec]]
        for oh in targets:
            keys, values = inner_of(oh)
            dirty = False
            for i, v in enumerate(values):
                text = v.decode("utf-8")
                new = text
                for pat, rep in CONVERSIONS.items():
                    n = new.count(pat)
                    if n:
                        counts[pat] = counts.get(pat, 0) + n
                        new = new.replace(pat, rep)
                if new != text:
                    values[i] = new.encode("utf-8")
                    dirty = True
                    changed_values += 1
            if dirty:
                oh._private_data = rubywrite.dumps([keys, values])

    total = sum(counts.values())
    print(f"변환: 값 {changed_values}개에서 {total}회 —", counts)

    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    for sec in SECTIONS:
        src = d[sec] if sec == 0 else [d[sec]]
        dst = r[sec] if sec == 0 else [r[sec]]
        assert len(src) == len(dst), f"절{sec} 길이 불일치"
        for a, b in zip(src, dst):
            assert inner_of(a) == inner_of(b), f"절{sec} 왕복 불일치"
    for sec in (1, 5, 13, 14, 19):
        if isinstance(d[sec], list):
            assert r[sec] == d[sec], f"절{sec}이 변했다"
        else:
            assert inner_of(r[sec]) == inner_of(d[sec]), f"절{sec}이 변했다"
    print(f"왕복 검증 통과 · 산출 {len(out):,} bytes")

    if dry:
        print("dry-run — 파일에 쓰지 않음")
        return
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
