# /// script
# requires-python = ">=3.12"
# ///
"""mkxp-z 시험대에 방금 지은 합본을 얹고, 시험대 전용 손질을 다시 붙인다.

    uv run share/bench_sync.py [--variant-dir "<dist 폴더 이름>"]

시험대는 `D:\\Game\\_probe\\z-mkxpz`다. 합본을 덮으면 `mkxp.json`이 배포판 것으로
돌아가 `preloadScript` 줄이 지워지므로(실측) 덮은 뒤 늘 다시 붙여야 한다.
전용 손질 둘은 배포물에 안 들어간다 — 까닭은 티켓 Z-34 「mkxp-z 시험대」 절.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
BENCH = Path("/mnt/d/Game/_probe/z-mkxpz")
BENCH_WIN = r"D:\Game\_probe\z-mkxpz"
PRELOAD = "z-bench-preload.rb"
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
WSL_PREFIX = r"\\wsl.localhost\Ubuntu"

STUB = """\
# 시험대 전용 — 모바일(Runa) 런타임 흉내. 배포물에는 안 들어간다.
#
# Win32API 무력화: 64비트 mkxp-z에서 32비트 gif.dll 적재와 RtlMoveMemory 포인터
# 장난이 세그폴트로 죽는다(SpriteWindow:421). iOS Runa에는 이 API 자체가 없으므로
# 늘 0을 돌려주는 껍데기로 갈아 끼워 그쪽과 비슷한 자리에 세운다.
Object.send(:remove_const, :Win32API) if Object.const_defined?(:Win32API)
class Win32API
  def initialize(*args); end
  def call(*args); 0; end
end
"""


def main():
    name = "포켓몬Z 한글패치 v5.3 (DPPt)"
    if "--variant-dir" in sys.argv:
        name = sys.argv[sys.argv.index("--variant-dir") + 1]
    src = HERE / "dist" / name
    if not src.is_dir():
        sys.exit(f"합본 폴더가 없어요: {src}")

    win_src = WSL_PREFIX + str(src).replace("/", "\\")
    r = subprocess.run([PS, "-NoProfile", "-Command",
                        f"robocopy '{win_src}' '{BENCH_WIN}' /E /NFL /NDL /NJH /NP /R:1 /W:1 "
                        "| Select-Object -Last 3; exit 0"],
                       capture_output=True, text=True)
    print(r.stdout.strip()[-200:] or r.stderr[-200:])

    (BENCH / PRELOAD).write_text(STUB, encoding="utf-8")
    cfg = BENCH / "mkxp.json"
    s = cfg.read_text(encoding="utf-8")
    if PRELOAD not in s:
        cfg.write_text(s.replace("{\n", '{\n    "preloadScript": ["%s"],\n' % PRELOAD, 1),
                       encoding="utf-8")
    print(f"시험대 손질 재부착: {PRELOAD} · mkxp.json preloadScript")

    stray = [p for p in (BENCH / "_rgss-only-dlls").glob("*.dll")
             if (BENCH / p.name).exists()]
    for p in stray:                       # 합본이 다시 들여놓은 32비트 dll을 도로 치운다
        (BENCH / p.name).unlink()
    if stray:
        print(f"32비트 dll {len(stray)}개 다시 치움: {', '.join(p.name for p in stray)}")


if __name__ == "__main__":
    main()
