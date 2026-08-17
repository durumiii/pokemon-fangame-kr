# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""정본(0단계) → 번역표 24절+loc를 **써 내는** 도구. 주도권 이전의 쓰기 쪽 첫 수.

`diff.py`가 채점표(대조만)라면 이쪽은 같은 역생성을 실제로 `translate/ko/`에 앉힌다.
역생성·대조 로직은 diff.py 것을 그대로 쓴다 — 두 벌을 두면 갈린다.

기본은 dry-run(차이만 센다). `--write`가 정본 파일을 갈아 끼운다.

⚠ `--write`는 `translate/ko/`에 미커밋 수정이 있으면 멈춘다 — 스튜디오가 열려 있을 수
있고, 그 수정을 stage0이 아직 안 담았으면 덮어쓰는 순간 사라진다. 다만 그 수정이
**전부 역생성 결과 그대로**면 끊긴 emit의 자국이므로 막지 않고 마저 밀어낸다.

usage: uv run translate/stage0/emit.py [--write]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import KO, OUT, ROOT, read_overrides  # noqa: E402
from diff import compare, rebuild, serialize, tainted_ids  # noqa: E402


def dirty(*paths):
    """git이 보는 미커밋 수정 — 스테이지 여부와 무관하게 다 센다."""
    out = subprocess.run(
        ["git", "status", "--porcelain", "--", *(str(p) for p in paths)],
        cwd=ROOT.parent, capture_output=True, text=True, check=True,
    ).stdout
    return [ln for ln in out.splitlines() if ln.strip()]


def dirty_ko():
    return dirty(KO)


def leftover(built):
    """미커밋 ko가 **전부 역생성 결과 그대로**인가 — 그러면 사람 수정이 아니라
    파일 순회 도중 끊긴 emit의 자국이다(쓰다 만 절만 새 값으로 남아 있다).

    사람 수정과 못 가르면 「커밋 후 재흡수」를 안내하게 되고, 그러면 아직 못 써진
    절의 판정이 옛 ko 값으로 되돌아간다.
    """
    dko = dirty_ko()
    if not dko:
        return False
    made = {name: serialize(rows) for name, rows in built.items()}
    for ln in dko:
        p = KO / Path(ln[3:].strip().strip('"')).name
        if p.name not in made or not p.exists():
            return False
        if p.read_text(encoding="utf-8") != made[p.name]:
            return False
    return True


def advice(built=None):
    """차이가 났을 때 **어느 쪽이 앞선 것인지**와 할 일 — 방향은 git 상태로 가린다.

    방향을 안 가리면 stage0가 앞선 상태(값을 앉히고 emit 전에 끊긴 자리)에서
    재흡수를 안내하게 되고, 그러면 방금 앉힌 값이 옛 ko 값으로 조용히 되돌아간다.
    """
    if dirty_ko():
        if leftover(built if built is not None else rebuild()[0]):
            return ("끊긴 emit의 자국이다(사람이 고친 ko가 아니다) — "
                    "uv run translate/stage0/emit.py --write 로 마저 밀어내라.")
        return ("ko가 앞섰다 — 그 수정을 커밋한 뒤 "
                "uv run translate/stage0/gen.py 로 재흡수하고 다시 돌려라.")
    if dirty(OUT / "sites.jsonl", OUT / "messages.jsonl"):
        return ("stage0가 앞섰다(반영이 emit 전에 끊겼을 수 있다) — "
                "uv run translate/stage0/emit.py --write 로 마저 밀어내라. "
                "⚠ 여기서 gen을 돌리면 앉힌 값이 옛 ko 값으로 되돌아간다.")
    return ("둘 다 커밋 상태인데 어긋난다 — "
            "uv run translate/stage0/gen.py 로 재흡수하고 커밋한 뒤 다시 돌려라.")


def main(argv=None, guarded=True):
    """argv를 받는 것은 다른 도구가 쓰기 경로를 부르기 위해서다(apply_verdicts 등).

    `guarded=False`는 **부르는 쪽이 값을 앉히기 전에 이미 ko 상태를 봤다**는 뜻이다
    (fixgui의 연타 저장 — 둘째 저장 시점의 ko는 첫 저장이 낸 산출이라 여기서 다시
    보면 「낡음」으로 잡힌다).
    """
    write = "--write" in (sys.argv if argv is None else argv)
    built, owner, msgs = rebuild()
    tainted = tainted_ids(msgs, read_overrides())

    if write:
        # 끊긴 emit의 자국은 막지 않는다 — 그 자리에서 막으면 마저 밀어낼 길이 없다.
        dko = dirty_ko() if guarded else []
        if dko and not leftover(built):
            print("멈춤 — translate/ko/에 미커밋 수정이 있다. 덮어쓰면 그 수정이 사라진다.")
            for ln in dko[:10]:
                print(f"  {ln}")
            print(f"  {advice(built)}")
            return 2

    from_ovr, other = compare(built, owner, tainted, write_to=KO if write else None)
    print(f"\n{'써 냄' if write else 'dry-run'} — 차이 {from_ovr + other}건 "
          f"(overrides 유래 {from_ovr} · 그 밖 {other})")
    if not write and from_ovr + other:
        print(advice(built))
    return 0


if __name__ == "__main__":
    sys.exit(main())
