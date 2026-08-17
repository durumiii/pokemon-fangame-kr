# /// script
# requires-python = ">=3.12"
# ///
"""박제 안내 — 승격(Z-53 3단계)으로 방향이 어긋난 도구가 실행 머리에서 부른다.

파일을 지우지 않는 것은 그 안의 규칙·표가 아직 읽을거리이기 때문이다. 다만 그대로
돌리면 정본이 되돌아가므로 여기서 멈춘다.
"""
import sys

FORCE = "--i-know"


def stop_unless_forced(why):
    """사정을 적고 멈춘다. `--i-know`가 있으면 경고만 하고 지나간다."""
    if FORCE in sys.argv:
        print(f"⚠ 박제된 도구를 강행한다 — {why}\n"
              "⚠ 이 실행으로 정본이 옛 값으로 되돌아갈 수 있다. 되돌리려면 git이 유일한 길이다.")
        return
    sys.exit(f"박제된 도구다 — {why}\n"
             f"그래도 돌리려면 {FORCE}. 정본이 되돌아가는 것을 각오하는 뜻이다.")


def stop_dat_writer():
    """dat를 직접 고치던 옛 도구 넷의 공통 사정."""
    stop_unless_forced(
        "dat 직접 수정은 빌드 한 번에 지워진다. 값은 정본 도구로 고쳐라 — "
        "스튜디오 `uv run translate/fixgui.py` · 낱건 `uv run translate/fix.py`.")
