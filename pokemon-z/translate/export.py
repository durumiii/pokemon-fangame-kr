# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""korean.dat → 구조화 번역 정본(ko/) 내보내기.

정본은 절별 JSONL이다 — 한 줄이 한 문장이고, 줄 순서가 dat의 자리 순서다.
- OrderedHash 절(0·14·15~17·19·20·22·23): {"k": 원문(대개 스페인어), "v": 한국어}.
  절0은 맵마다 {"map": n} 헤더 줄이 앞선다.
- 목록 절(1~13·18·21): {"i": 자리, "es": messages.dat 원문, "v": 한국어}.
  es는 참고용이고 빌드에는 v만 쓴다.

초기 1회 + 재동기화용. 평소 편집은 ko/ 파일에 하고 build.py로 다시 만든다.

⚠ **이 도구는 dat를 통째로 정본에 덮는다.** 회수할 dat가 마지막 빌드 시점에 멈춰 있으면
그 뒤 정본이 받은 수정이 옛 값으로 돌아간다(2026-08-08 실측 282행). dat에 손으로 넣은
수정만 건지려면 `harvest.py`를 쓴다 — 기준선·dat·정본 셋을 견주어 손댄 자리만 가져온다.

usage: uv run export.py
"""
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
MESSAGES = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/messages.dat")
KO = Path(__file__).with_name("ko")

SECTION_NAMES = {
    0: "maps", 1: "species", 2: "kinds", 3: "entries", 4: "forms", 5: "moves",
    6: "move-descs", 7: "items", 8: "item-plurals", 9: "item-descs",
    10: "abilities", 11: "ability-descs", 12: "types", 13: "trainer-classes",
    14: "trainer-names", 15: "begin-speech", 16: "end-speech-win",
    17: "end-speech-lose", 18: "regions", 19: "place-names", 20: "place-descs",
    21: "map-names", 22: "phone", 23: "script-texts",
}


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def jline(obj):
    return json.dumps(obj, ensure_ascii=False)


def main():
    d = load(open(STORE, "rb"))
    es = load(open(MESSAGES, "rb"))
    KO.mkdir(exist_ok=True)
    for sec in range(len(d)):
        name = f"{sec:02d}-{SECTION_NAMES.get(sec, 'sec')}"
        lines = []
        obj = d[sec]
        if sec == 0:
            for mi, oh in enumerate(obj):
                keys, values = inner_of(oh)
                lines.append(jline({"map": mi, "n": len(keys)}))
                for k, v in zip(keys, values):
                    lines.append(jline({"k": k.decode("utf-8", "replace"),
                                        "v": v.decode("utf-8", "replace")}))
        elif isinstance(obj, list):
            ref = es[sec] if sec < len(es) and isinstance(es[sec], list) else []
            for i, v in enumerate(obj):
                row = {"i": i, "v": v.decode("utf-8", "replace")}
                if i < len(ref):
                    e = ref[i].decode("utf-8", "replace")
                    if e and e != row["v"]:
                        row["es"] = e
                lines.append(jline(row))
        elif hasattr(obj, "_private_data"):
            keys, values = inner_of(obj)
            for k, v in zip(keys, values):
                # __kr_patch__는 build.py가 심는 판 표식이라 정본에 들어가면 안 된다
                # (들어가면 다음 빌드가 그걸 다시 넣고 verify의 미러 대조가 어긋난다)
                if bytes(k) == b"__kr_patch__":
                    continue
                lines.append(jline({"k": k.decode("utf-8", "replace"),
                                    "v": v.decode("utf-8", "replace")}))
        else:
            continue
        path = KO / f"{name}.jsonl"
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        print(f"{path.name}: {len(lines)}줄")


if __name__ == "__main__":
    main()
