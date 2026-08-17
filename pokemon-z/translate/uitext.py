#!/usr/bin/env python3
"""mods/UI Text KR/001_UiText.rb의 TABLE 블록을 translate/data/uitext.jsonl에서 생성한다.

인명 행({"name": ...})의 한국어 표기는 names.json이 정본이라 손으로 베낀 복제가 남지 않는다.
미리보기: uv run translate/uitext.py   /   반영: uv run translate/uitext.py --write
"""
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RB = ROOT / "mods/UI Text KR/001_UiText.rb"
DATA = ROOT / "translate/data/uitext.jsonl"
NAMES = ROOT / "translate/names.json"
BANNER = "    # (generated from translate/data/uitext.jsonl — 직접 고치지 말고 uv run translate/uitext.py --write)"


def rb_str(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def build(banner=True):
    names = json.loads(NAMES.read_text(encoding="utf-8"))["names"]
    rows, out = [], ["  TABLE = ["]
    if banner:
        out.append(BANNER)
    for line in DATA.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if "note" in e:
            rows.append(("note", "    # " + e["note"]))
        elif "name" in e:
            ko = names.get(e["name"])
            if ko is None:
                sys.exit("names.json에 없는 이름: %s" % e["name"])
            rows.append(("row", "    [/\\b%s\\b/, %s]," % (e["name"], rb_str(ko))))
        elif "re" in e:
            rows.append(("row", "    [/\\b%s\\b/, %s]," % (e["re"], rb_str(e["ko"]))))
        else:
            rows.append(("row", "    [%s, %s]," % (rb_str(e["es"]), rb_str(e["ko"]))))
    last = max(i for i, (k, _) in enumerate(rows) if k == "row")
    rows[last] = ("row", rows[last][1][:-1])
    out += [t for _, t in rows]
    out.append("  ]")
    return out


def main():
    src = RB.read_text(encoding="utf-8").split("\n")
    start = src.index("  TABLE = [")
    end = src.index("  ]", start)
    new = src[:start] + build(banner="--no-banner" not in sys.argv) + src[end + 1:]
    if new == src:
        print("변경 없음")
        return
    if "--write" in sys.argv:
        RB.write_text("\n".join(new), encoding="utf-8")
        print("반영: %s" % RB)
    else:
        sys.stdout.writelines(difflib.unified_diff(
            [l + "\n" for l in src], [l + "\n" for l in new], "현행", "생성"))


if __name__ == "__main__":
    main()
