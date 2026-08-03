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


def _dec(b):
    return bytes(b).decode("utf-8", "replace")


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
                if i < len(ref) and bytes(ref[i]) != bytes(v):
                    row["k"] = _dec(ref[i])
                rows.append(row)
        elif hasattr(obj, "_private_data"):
            keys, values = _inner(obj)
            for j in range(len(keys)):
                if sec == META_SEC and bytes(keys[j]) == META_KEY:
                    meta = _dec(values[j])
                    continue
                rows.append({"sec": sec, "idx": j,
                             "k": _dec(keys[j]), "v": _dec(values[j])})
    _state["d"] = d
    return json.dumps({"meta": meta,
                       "sha": hashlib.sha256(bytes(dat_bytes)).hexdigest()[:12],
                       "rows": rows}, ensure_ascii=False)
