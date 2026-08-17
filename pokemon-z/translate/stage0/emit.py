# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""정본(0단계) → 번역표 24절+loc를 **써 내는** 도구. 주도권 이전의 쓰기 쪽 첫 수.

`diff.py`가 채점표(대조만)라면 이쪽은 같은 역생성을 실제로 `translate/ko/`에 앉힌다.
역생성·대조 로직은 diff.py 것을 그대로 쓴다 — 두 벌을 두면 갈린다.

기본은 dry-run(차이만 센다). `--write`가 정본 파일을 갈아 끼운다.

⚠ `--write`는 `translate/ko/`에 미커밋 수정이 있으면 멈춘다 — 스튜디오가 열려 있을 수
있고, 그 수정을 stage0이 아직 안 담았으면 덮어쓰는 순간 사라진다.

usage: uv run translate/stage0/emit.py [--write]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import KO, ROOT, read_overrides  # noqa: E402
from diff import compare, rebuild, tainted_ids  # noqa: E402


def dirty_ko():
    """git이 보는 translate/ko/의 미커밋 수정 — 스테이지 여부와 무관하게 다 센다."""
    out = subprocess.run(
        ["git", "status", "--porcelain", "--", str(KO)],
        cwd=ROOT.parent, capture_output=True, text=True, check=True,
    ).stdout
    return [ln for ln in out.splitlines() if ln.strip()]


def main(argv=None):
    """argv를 받는 것은 다른 도구가 쓰기 경로를 부르기 위해서다(apply_verdicts 등)."""
    write = "--write" in (sys.argv if argv is None else argv)
    built, owner, msgs = rebuild()
    tainted = tainted_ids(msgs, read_overrides())

    if write:
        dirty = dirty_ko()
        if dirty:
            print("멈춤 — translate/ko/에 미커밋 수정이 있다. 덮어쓰면 그 수정이 사라진다.")
            for ln in dirty[:10]:
                print(f"  {ln}")
            print("커밋하거나 harvest로 회수한 뒤 다시 돌려라.")
            return 2

    from_ovr, other = compare(built, owner, tainted, write_to=KO if write else None)
    print(f"\n{'써 냄' if write else 'dry-run'} — 차이 {from_ovr + other}건 "
          f"(overrides 유래 {from_ovr} · 그 밖 {other})")
    if not write and from_ovr + other:
        print("--write로 정본에 반영한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
