# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scripts.rxdata 섹션 판독기 — 이름·md5·크기를 찍는다.

    uv run share/qa-sections.py <Scripts.rxdata> [이름조각]
    uv run share/qa-sections.py <Scripts.rxdata> <이름> --dump   # 그 절의 소스를 그대로 뱉는다

설치본·보관소·배포 zip에서 꺼낸 스크립트의 섹션 구성을 30초 안에 대조하는 용도.
두 파일의 출력을 diff하면 「어느 섹션이 다른가」가 그대로 나온다(v6 샌드박스 검증에서
모드킷 설치와 zip 덮어쓰기 산출의 동치를 이것으로 쟀다 — MOD: 접두만 걷으면 동일).

`--dump`는 원작 절의 코드를 읽어야 할 때 쓴다(모드가 감쌀 자리 찾기, `$DEBUG` 같은
전역이 어디서 무엇을 여는지 세기). 이름은 정확히 일치해야 한다.
"""
import hashlib
import sys
import zlib

import rubymarshal.reader as R


def sections(path):
    with open(path, "rb") as f:
        arr = R.load(f)
    out = []
    for e in arr:
        name = e[1]
        name = name.decode("utf-8", "replace") if isinstance(name, bytes) else str(name)
        body = e[2]
        raw = body.value if hasattr(body, "value") else body
        if isinstance(raw, str):
            raw = raw.encode("latin-1")
        src = zlib.decompress(raw)
        out.append((name, hashlib.md5(src).hexdigest(), len(src), src))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    dump = "--dump" in sys.argv
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    want = args[0] if args else None
    if dump:
        if not want:
            raise SystemExit("--dump에는 절 이름을 정확히 줘라")
        for n, _h, _l, src in sections(sys.argv[1]):
            if n == want:
                sys.stdout.write(src.decode("utf-8", "replace"))
                raise SystemExit(0)
        raise SystemExit(f"그런 절이 없다: {want}")
    for n, h, l, _ in sections(sys.argv[1]):
        if want and want not in n:
            continue
        print(f"{h}  {l:8d}  {n}")
