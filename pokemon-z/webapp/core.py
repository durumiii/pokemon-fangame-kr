"""웹 스튜디오 pyodide 코어 — korean.dat ⇄ rows.

export.py·빌드.py의 로직 이식. 파일 IO 없음(bytes in/out) —
브라우저 JS가 File System Access API로 읽고 쓴다.
"""
import hashlib
import io
import json

from rubymarshal.reader import load

import rubywrite

SECTION_NAMES = {
    0: "maps", 1: "species", 2: "kinds", 3: "entries", 4: "forms", 5: "moves",
    6: "move-descs", 7: "items", 8: "item-plurals", 9: "item-descs",
    10: "abilities", 11: "ability-descs", 12: "types", 13: "trainer-classes",
    14: "trainer-names", 15: "begin-speech", 16: "end-speech-win",
    17: "end-speech-lose", 18: "regions", 19: "place-names", 20: "place-descs",
    21: "map-names", 22: "phone", 23: "script-texts",
}
META_KEY = b"__kr_patch__"
META_SEC = 23

_state = {}


def _inner(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def _raw(v):
    """마샬 문자열의 바이트.

    딱지가 없으면 판독기가 `bytes`를, 붙어 있으면 `RubyString`(문자열은 `.text`에
    들어 있고 `bytes()`로 감쌀 수 없는 객체)을 준다. 딱지판과 안 붙은 판을 같은
    코드로 다뤄야 해서 여기서 한 줄로 모은다.
    """
    if isinstance(v, str):
        return v.encode("utf-8")
    text = getattr(v, "text", None)          # rubymarshal의 RubyString
    return text.encode("utf-8") if isinstance(text, str) else bytes(v)


def _dec(b):
    return _raw(b).decode("utf-8", "replace")


def tag_utf8(o):
    """모든 문자열에 UTF-8 인코딩 딱지를 붙인다(마샬 ivar `:E`).

    딱지판을 열었으면 저장할 때도 딱지를 붙여야 한다 — 고친 줄만 딱지가 빠지면
    루비 1.9+ 실행기가 그 줄에서만 인코딩이 어긋난다. build.py의 같은 이름 함수와
    한 벌이다.
    """
    if isinstance(o, (bytes, bytearray)):
        return bytes(o).decode("utf-8", "replace")
    if isinstance(o, list):
        return [tag_utf8(x) for x in o]
    if hasattr(o, "_private_data"):
        o._private_data = rubywrite.dumps(tag_utf8(_inner(o)))
    return o


def _looks_tagged(d):
    """이 dat의 문자열에 인코딩 딱지가 붙어 있나 — 첫 낱 문자열 하나로 판별한다."""
    for obj in d:
        if isinstance(obj, list) and obj and not hasattr(obj[0], "_private_data"):
            return not isinstance(obj[0], (bytes, bytearray))
    return False


def load_dat(dat_bytes, msg_bytes=None):
    d = load(io.BytesIO(bytes(dat_bytes)))
    es = load(io.BytesIO(bytes(msg_bytes))) if msg_bytes else []
    rows, meta = [], None
    for sec in range(len(d)):
        obj = d[sec]
        if sec == 0:
            for mi, oh in enumerate(obj):
                keys, values = _inner(oh)
                for j in range(len(keys)):
                    rows.append({"sec": 0, "map": mi, "idx": j,
                                 "k": _dec(keys[j]), "v": _dec(values[j])})
        elif isinstance(obj, list):
            ref = es[sec] if sec < len(es) and isinstance(es[sec], list) else []
            for i, v in enumerate(obj):
                row = {"sec": sec, "idx": i, "v": _dec(v)}
                if i < len(ref) and _raw(ref[i]) != _raw(v):
                    row["k"] = _dec(ref[i])
                rows.append(row)
        elif hasattr(obj, "_private_data"):
            keys, values = _inner(obj)
            for j in range(len(keys)):
                if sec == META_SEC and _raw(keys[j]) == META_KEY:
                    meta = _dec(values[j])
                    continue
                rows.append({"sec": sec, "idx": j,
                             "k": _dec(keys[j]), "v": _dec(values[j])})
    _state["d"] = d
    _state["tagged"] = _looks_tagged(d)
    return json.dumps({"meta": meta,
                       "sha": hashlib.sha256(bytes(dat_bytes)).hexdigest()[:12],
                       "rows": rows}, ensure_ascii=False)


def build_dat(edits_json):
    d = _state["d"]
    edits = json.loads(edits_json)
    hash_secs, list_edits = {}, []
    for e in edits:
        if e["sec"] != 0 and isinstance(d[e["sec"]], list):
            list_edits.append(e)
        else:
            hash_secs.setdefault((e["sec"], e.get("map")), []).append(e)

    for e in list_edits:
        obj = d[e["sec"]]
        if e["idx"] >= len(obj):
            raise ValueError(f"절{e['sec']}[{e['idx']}]: 범위 밖")
        obj[e["idx"]] = e["v"].encode("utf-8")

    for (sec, mi), es_ in hash_secs.items():
        oh = d[sec][mi] if sec == 0 else d[sec]
        keys, values = _inner(oh)
        for e in es_:
            j = e["idx"]
            if j >= len(keys):
                raise ValueError(f"절{sec}[{j}]: 범위 밖")
            if "k" in e and e["k"] != _dec(keys[j]):
                raise ValueError(f"절{sec}[{j}]: 원문 불일치 — 패치 버전이 다른 고침 파일일 수 있음")
            values[j] = e["v"].encode("utf-8")
        oh._private_data = rubywrite.dumps([keys, values])

    if _state.get("tagged"):
        d = tag_utf8(d)          # 고친 줄만 딱지가 빠지지 않게, 저장 직전에 전체를 맞춘다
    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    if len(r) != len(d):
        raise ValueError("왕복 검증 실패: 절 수 불일치")
    for sec in range(len(d)):
        if isinstance(d[sec], list):
            if r[sec] != d[sec]:
                raise ValueError(f"왕복 검증 실패: 절{sec}")
        elif hasattr(d[sec], "_private_data"):
            pairs = zip(r[sec], d[sec]) if sec == 0 else [(r[sec], d[sec])]
            for a, b in pairs:
                if _inner(a) != _inner(b):
                    raise ValueError(f"왕복 검증 실패: 절{sec}")
    return out
