# /// script
# requires-python = ">=3.12"
# ///
"""번역 정본(translate/ko/*.jsonl)의 조사 병기 「(은)는」류를 조사 자동 선택 문법 \\j[…]로 바꾼다.

조사 스크립트(share/josa.rb — 지금은 한글패치 코어의 본문 섹션)가 있어야 화면에서
해석된다. 없이 이 변환만 하면 대사에 \\j[은,는]가 그대로 보인다.

**정본을 고친다 — 예전 판은 korean.dat를 직접 고쳤는데(2026-08-05 이전),
dat는 build.py가 정본에서 매번 새로 만드는 산출물이라 빌드 한 번에 되살아났다.**
고친 뒤 `uv run translate/build.py`로 dat를 다시 만들 것.

앞말이 변수여도 안전하다 — `\\PN`은 Messages:1313, `\\v[N]`은 Messages:1341에서
창에 넘기기 전에 실제 값으로 바뀌고, josa.rb는 그 뒤 그리기 훅(setText)에서 돈다.

usage: uv run translate/apply_josa.py [--dry-run]
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
KO = HERE / "ko"

# 병기 → \j[받침형,무받침형]. 괄호가 앞뒤 어느 쪽에 붙는 꼴이든 잡는다.
CONVERSIONS = {
    "(은)는": "\\j[은,는]",
    "(이)가": "\\j[이,가]",
    "(을)를": "\\j[을,를]",
    "(와)과": "\\j[과,와]",
    "(으)로": "\\j[으로,로]",
    "(이)야": "\\j[이야,야]",
    "(이)랑": "\\j[이랑,랑]",
    "은(는)": "\\j[은,는]",
    "이(가)": "\\j[이,가]",
    "을(를)": "\\j[을,를]",
    "와(과)": "\\j[과,와]",
    "과(와)": "\\j[과,와]",
    "로(으로)": "\\j[으로,로]",
    "(이)라는": "\\j[이라는,라는]",
    "(이)군요": "\\j[이군요,군요]",
}
# 변수와 조사 사이에 낀 공백·군더더기 역슬래시 — 그대로 두면 josa가 앞 글자로
# 공백이나 역슬래시를 보고 무받침으로 골라 버린다(예: `\v[1] 은(는)`, `\PN\은(는)`)
VAR = r"(?:\\PN|\\[vV]\[\d+\]|\{\d+\})"
GAP = re.compile(rf"({VAR})[\s\\]+(?=\\j\[)")
# 병기조차 없이 조사가 하나로 굳은 자리 — 앞이 변수면 그 값은 실행 때 정해지므로
# 받침을 미리 알 수 없다(「\PN가」는 받침 있는 이름에서 그대로 틀린다).
# 변수 바로 뒤에 붙은 홑조사만 잡는다 — 사이에 공백이나 다른 글자가 끼면 건드리지 않는다.
BARE = {"은": "\\j[은,는]", "는": "\\j[은,는]", "이": "\\j[이,가]", "가": "\\j[이,가]",
        "을": "\\j[을,를]", "를": "\\j[을,를]", "와": "\\j[과,와]", "과": "\\j[과,와]",
        "로": "\\j[으로,로]"}
BARE_RE = re.compile(rf"({VAR})({'|'.join(BARE)})(?![가-힣])")


def convert(text):
    out = text
    hits = {}
    for pat, rep in CONVERSIONS.items():
        n = out.count(pat)
        if n:
            hits[pat] = hits.get(pat, 0) + n
            out = out.replace(pat, rep)
    if hits:
        out = GAP.sub(r"\1", out)

    def bare(m):
        hits[m.group(2) + "(홑)"] = hits.get(m.group(2) + "(홑)", 0) + 1
        return m.group(1) + BARE[m.group(2)]

    out = BARE_RE.sub(bare, out)
    return out, hits


def put_lines(edits):
    """0단계 정본에 앉히고 ko를 역생성한다 — 창구는 stage0/edit.py 하나다."""
    sys.path.insert(0, str(HERE / "stage0"))
    from edit import put_lines as _put
    return _put(edits)

def main():
    dry = "--dry-run" in sys.argv
    counts, rows, samples = {}, 0, []
    edits = []
    for path in sorted(KO.glob("*.jsonl")):
        lines = path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            d = json.loads(line)
            v = d.get("v")
            if not v:
                continue
            new, hits = convert(v)
            if new == v:
                continue
            for k, n in hits.items():
                counts[k] = counts.get(k, 0) + n
            rows += 1
            if len(samples) < 8:
                samples.append(f"{path.name}:{i + 1}\n   전 {v[:90]}\n   후 {new[:90]}")
            edits.append((path.name, i + 1, new))
    if not dry:
        err = put_lines(edits)
        if err:
            print("멈춤 —", err)
            return

    print(f"변환: {rows}행에서 {sum(counts.values())}회 —", counts)
    for s in samples:
        print(s)
    print("dry-run — 파일에 쓰지 않음" if dry else "정본 기록 완료 — build.py로 dat를 다시 만들 것")


if __name__ == "__main__":
    main()
