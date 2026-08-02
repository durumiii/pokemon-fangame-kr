# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""조사 자동 선택(josa.rb)을 한글패치 통합의 Scripts.rxdata에 굽는다.

번역표가 \\j[은,는] 문법을 전제해 조사 스크립트 없이는 한글패치가 성립하지
않는다 — 그래서 별도 모드(옛 Josa Select)가 아니라 한글패치 통합의 본문 섹션
「Josa Select」로 담는다(2026-08-03 흡수 결정). MOD: 접두사가 없으므로
inject.py 재구축·modstore 설치 어느 쪽에서도 기반의 일부로 살아남는다.

멱등: 같은 제목 섹션이 있으면 갈아 끼우고, 없으면 Main 직전에 꽂는다.
훅 대상 섹션(SpriteWindow·DrawText)의 md5가 기대와 다르면 멈춘다(판 갱신 신호).

usage: uv run bake_josa.py [대상 Scripts.rxdata ...]
  무인자면 한글패치 통합의 수술판 + 수술 전 백업(pre-intl.bak) 둘 다.
"""
import hashlib
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from rubymarshal.reader import load  # noqa: E402
from fanlib import rubywrite  # noqa: E402

BASE_MOD = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합")
DEFAULT_TARGETS = [
    BASE_MOD / "Data" / "Scripts.rxdata",
    BASE_MOD / "Data" / "Scripts.rxdata.pre-intl.bak",
]
TITLE = b"Josa Select"
# 옛 Josa Select mod.json의 expects — 훅이 잡는 원문 섹션의 md5
EXPECTS = {
    "SpriteWindow": "dd49c0623e5fc170534c44aa6c198e23",
    "DrawText": "b6e3111c62e7c43b528fa60894e9acb6",
}


def bake(target: Path, source: bytes) -> None:
    with open(target, "rb") as fh:
        sections = load(fh)
    by_title = {}
    for e in sections:
        by_title.setdefault(bytes(e[1]).decode("utf-8"),
                            hashlib.md5(zlib.decompress(bytes(e[2]))).hexdigest())
    for name, want in EXPECTS.items():
        got = by_title.get(name)
        if got != want:
            sys.exit(f"멈춤: {target} 섹션 {name} md5 {got} (기대 {want}) — 판이 바뀌었으면 훅 재확인.")

    kept = [e for e in sections if bytes(e[1]) != TITLE]
    main_at = max(i for i, e in enumerate(kept) if bytes(e[1]) == b"Main")
    sid = int(hashlib.md5(TITLE).hexdigest()[:7], 16)
    result = kept[:main_at] + [[sid, TITLE, zlib.compress(source)]] + kept[main_at:]

    payload = rubywrite.dumps(result)
    import io
    again = load(io.BytesIO(payload))
    assert len(again) == len(result), "왕복에서 섹션 수가 달라졌다"
    for a, b in zip(again, result):
        assert bytes(a[1]) == bytes(b[1]) and \
            zlib.decompress(bytes(a[2])) == zlib.decompress(bytes(b[2]))
    tmp = target.with_suffix(target.suffix + ".new")
    tmp.write_bytes(payload)
    tmp.replace(target)
    print(f"{target} ← Josa Select 섹션 ({len(source)}자, {'갈아 끼움' if len(kept) != len(sections) else '새로 꽂음'})")


def main() -> int:
    targets = [Path(a) for a in sys.argv[1:]] or DEFAULT_TARGETS
    source = (HERE / "josa.rb").read_bytes()
    for t in targets:
        bake(t, source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
