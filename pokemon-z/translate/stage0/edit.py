# /// script
# requires-python = ">=3.12"
# ///
"""stage0 값 수정 공용 한 벌 — (맵, norm(원문))으로 자리를 찾아 messages의 `val`을 간다.

값 수정 도구 열하나(Z-53 3단계)가 전부 이것을 부른다. 도구마다 제 조회를 다시 짜면
그 수만큼 갈린다.

**공유 항목(`m*.s*`)까지는 따라가고 통일 참조(`unified.*`)는 따라가지 않는다.**
옛 경로(ko 직접 쓰기)는 (맵, 원문) 한 줄을 갈았다 — 그 맵의 자리는 전부 함께 바뀌고
다른 맵은 그대로다. 통일 항목을 갈면 전 맵이 바뀌어 옛 경로와 어긋나므로, 참조를
문자열로 갈아 끼워 그 맵만 떼어 낸다.

ko까지 내리는 것은 이 모듈의 일이 아니다 — 저장 뒤 `emit.py --write`가 역생성한다.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, dump_jsonl, norm, read_jsonl  # noqa: E402

SHARED_RE = re.compile(r"^m\d+\.s\d+$")
MAP_ID_RE = re.compile(r"^m(\d+)\.")


class Messages:
    """messages.jsonl을 메모리에 열고 값을 갈아 저장한다. 자리 조회는 sites.jsonl로 한다."""

    def __init__(self, d=OUT):
        self.d = d
        self.msgs = read_jsonl(d / "messages.jsonl")
        self.idx = {m["id"]: i for i, m in enumerate(self.msgs)}
        # 맵 절의 줄 하나가 항목 하나 — ((맵, norm 원문), 값이 사는 id).
        self.groups, seen = [], set()
        for s in read_jsonl(d / "sites.jsonl"):
            if s["apply"] != "map":
                continue
            tid = self.local(s["id"])
            if tid in seen:
                continue
            seen.add(tid)
            self.groups.append(((int(MAP_ID_RE.match(s["id"]).group(1)), norm(s["src"])), tid))
        self.by_key = {}
        for key, tid in self.groups:
            self.by_key.setdefault(key, []).append(tid)

    def local(self, sid):
        """자리 → 그 맵 안에서 값이 실제로 사는 항목. 공유 항목까지만 따라간다."""
        seen = set()
        while True:
            v = self.msgs[self.idx[sid]]["val"]
            if not (isinstance(v, dict) and SHARED_RE.match(v.get("ref", ""))):
                return sid
            assert sid not in seen, f"참조 순환: {sid}"
            seen.add(sid)
            sid = v["ref"]

    def value(self, mid):
        """지금 보이는 문자열 — 참조를 끝까지 따라간다(diff.resolve와 같은 셈).

        선택자 트리는 **기본 갈래**를 돌려준다. 갈래별 값은 이 창으로 안 보인다.
        """
        v, seen = self.msgs[self.idx[mid]]["val"], set()
        while isinstance(v, dict) and ("ref" in v or "sel" in v):
            if "sel" in v:
                return v["default"]
            assert v["ref"] not in seen, f"참조 순환: {v['ref']}"
            seen.add(v["ref"])
            v = self.msgs[self.idx[v["ref"]]]["val"]
        return v

    def put(self, mid, val):
        """값 항목 하나를 간다. 참조였으면 문자열로 갈려 그 자리가 떨어져 나온다.

        선택자 트리는 거부한다 — 통째로 덮으면 갈래가 소리 없이 사라진다.
        """
        i = self.idx[mid]
        cur = self.msgs[i]["val"]
        if isinstance(cur, dict) and "sel" in cur:
            raise ValueError(
                f"{mid}는 선택자 트리(갈래 {sorted(cur['when'])})다 — 갈래 값 수정 경로는"
                " 아직 없다. overrides나 추가분 파일로 가라.")
        self.msgs[i] = {**self.msgs[i], "val": val}

    def put_default(self, mid, val):
        """선택자 트리면 **기본 갈래만** 간다. 평문이면 put과 같다.

        스튜디오가 절23 상점 줄을 고치는 것의 뜻이 이것이다 — 옛 경로가 base 줄을
        고치던 것과 같은 자리이고, 갈래(when)는 그 화면에 보이지도 않는다.
        """
        i = self.idx[mid]
        cur = self.msgs[i]["val"]
        if isinstance(cur, dict) and "sel" in cur:
            self.msgs[i] = {**self.msgs[i], "val": {**cur, "default": val}}
        else:
            self.put(mid, val)

    def set(self, mi, src, val):
        """(맵, 원문)의 값을 간다 — 바꾼 항목 수. 없는 열쇠면 0."""
        tids = self.by_key.get((mi, norm(src)), [])
        for tid in tids:
            self.put(tid, val)
        return len(tids)

    def save(self):
        dump_jsonl(self.d / "messages.jsonl", self.msgs)


def put_lines(edits, allow_default=False):
    """ko의 (파일, 줄)들을 0단계 정본에 앉히고 ko를 **한 번에** 역생성한다 — 오류면 사유.

    ko를 고치는 도구가 전부 이 창구로 온다. (파일, 줄) → 자리 색인은 역생성의 owner가
    그대로 주므로 도구마다 제 색인을 짜지 않는다. 줄마다 emit을 돌면 일괄 치환에서
    못 쓰니 앉히기는 모아서 하고 역생성은 마지막에 한 번이다.

    `allow_default`는 절23 상점 줄(선택자 트리)의 뜻을 정한다 — 사람이 그 줄을 보고
    고치는 도구(스튜디오)만 참이고, 기계·일괄 도구는 거짓이라 거부된다. 갈래를 같이
    안 가면 한 상점 안에서 격이 섞인다.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import emit
    from diff import rebuild

    edits = list(edits)
    if not edits:
        return None
    built, owner, _ = rebuild()
    if emit.dirty_ko() and not emit.leftover(built):
        return f"translate/ko/에 이 도구 밖의 수정이 있다 — {emit.advice(built)}"
    expect = emit.ko_state()          # 쓰기 직전에 이것과 견준다
    ed = Messages()
    for file, line, val in edits:
        ids = owner.get(file, [])
        sid = ids[line - 1] if 0 < line <= len(ids) else None
        if sid is None:
            return f"{file}:{line} — 0단계 자리에 안 붙는다(맵 머리 줄이거나 파일 밖)"
        try:
            (ed.put_default if allow_default else ed.put)(ed.local(sid), val)
        except ValueError as e:
            return f"{file}:{line} — {e}"
    ed.save()
    if emit.main(["--write"], expect=expect):
        return "정본은 고쳤으나 ko 역생성이 멈췄다 — 터미널을 보라"
    return None
