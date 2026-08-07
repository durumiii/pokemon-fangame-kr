"""모드 설치·제거를 여러 순서로 돌려 순정 복귀를 검사한다 (게임 사본 위에서).

    uv run --project ~/workspace/claude-native/sketches/essentials-modkit \
        python qa_cycles.py [사이클이름 ...]

각 사이클은 ① 사본을 순정으로 되돌리고 ② 정해진 순서로 얹고 ③ 정해진 순서로 빼고
④ 지문표와 전수 대조한다. 실패하면 어긋난 자리를 이름까지 찍는다.
"""
import json
import pathlib
import random
import subprocess
import sys
import zipfile
import zlib

sys.path.insert(0, "/home/durumii/workspace/claude-native/sketches/essentials-modkit")
from modkit import modassets, modstore  # noqa: E402

import os
SLOT = os.environ.get("QA_SLOT", "")          # 조합마다 제 사본을 쓴다
COPY = pathlib.Path("/mnt/d/GameVault/trash/V2.18-시험사본" + SLOT)
STORE = pathlib.Path("/mnt/d/GameVault/mods")
MAN = json.loads(pathlib.Path(
    "/mnt/d/GameVault/manifests/pokemon-z/V2.18-정본.json").read_text(encoding="utf-8"))["files"]
ZIP = zipfile.ZipFile("/mnt/c/Users/durumii/Downloads/POKEMON Z V2.18.zip")
ROOT = ZIP.namelist()[0].split("/")[0]
INZIP = {n.split("/", 1)[1] for n in ZIP.namelist() if "/" in n}

SKIP = {"LastSave.dat", "modkit-owners.json", "modkit-log.jsonl"}

MODS = ["DPPT Font", "한글패치 코어", "UI Text KR", "Controller UX", "Z-GUI",
        "Battle Speed", "Better Movements", "Frame Profiler", "GC Tamer", "디버그 모드"]


PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
SNAP = r"D:\GameVault\trash\V2.18-순정스냅"
COPY_WIN = r"D:\GameVault\trash\V2.18-시험사본" + SLOT


def reset():
    """순정 스냅에서 robocopy로 되돌린다 — 파일 옮기기는 윈도우 쪽에서."""
    subprocess.run([PS, "-NoProfile", "-Command",
                    f"robocopy '{SNAP}' '{COPY_WIN}' /MIR /NFL /NDL /NJH /NP /MT:16 | Out-Null"],
                   check=False, capture_output=True)


def _old_reset():
    for p in sorted(COPY.rglob("*")):
        if p.is_file() and (p.name.endswith(".orig") or ".pre-" in p.name):
            p.unlink()
    for p in sorted(COPY.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(COPY)).replace("\\", "/")
        if rel not in MAN and rel not in INZIP and p.name != "LastSave.dat":  # 장부도 지운다
            p.unlink()
    for rel, (size, crc) in MAN.items():
        f = COPY / rel
        if not f.is_file() or (zlib.crc32(f.read_bytes()) & 0xffffffff) != crc:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(ZIP.read(f"{ROOT}/{rel}"))


def touched_slots() -> set:
    """모드들이 선언한 자리의 합집합 — 모드가 바꿀 수 있는 곳은 여기뿐이다."""
    out = {"Data/Scripts.rxdata"}
    for name in MODS:
        try:
            mod = modstore.read_mod(STORE, name, game="Pokemon Z")
        except Exception:
            continue
        out |= {one.get("install_to") for one in (mod.assets or [])}
    return {r for r in out if r}


def pristine() -> list:
    """순정과 어긋난 자리 — 모드가 건드릴 수 있는 자리만 본다.

    19,064자리 전수 CRC를 사이클마다 drvfs로 훑으면 검사보다 파일 읽기에 시간을 다 쓴다.
    모드는 자기가 선언한 자리와 백업 찌꺼기 말고는 만들지 않으므로 그 둘이면 충분하다.
    """
    off = []
    for rel in sorted(touched_slots()):
        f = COPY / rel
        told = MAN.get(rel)
        if told is None:                       # 순정에 없던 자리 — 사라져야 정상
            if f.is_file():
                off.append((rel, "잔재"))
        elif not f.is_file():
            off.append((rel, "없어짐"))
        elif (zlib.crc32(f.read_bytes()) & 0xffffffff) != told[1]:
            off.append((rel, "내용 다름"))
    for p in COPY.rglob("*"):                  # 백업·층·장부 찌꺼기
        if p.is_file() and (p.name.endswith(".orig") or ".pre-" in p.name
                            or p.name in ("modkit-owners.json", "modkit-log.jsonl")):
            off.append((str(p.relative_to(COPY)).replace("\\", "/"), "찌꺼기"))
    return off


def mismatches(name):
    """그 모드의 에셋 중 지금 게임과 다른 자리 — 「반쪽」 판정의 속을 본다."""
    mod = modstore.read_mod(STORE, name, game="Pokemon Z")
    out = []
    for one in mod.assets:
        src = pathlib.Path(mod.folder) / one["file"]
        dst = COPY / one["install_to"]
        if not dst.is_file():
            out.append((one["install_to"], "게임에 없음"))
        elif dst.name == "Scripts.rxdata":
            # 코어는 병합으로 들어가 바이트가 같을 수 없다 — 뜻으로 견준다
            if not modstore.same_core(src, dst):
                out.append((one["install_to"], "코어 내용이 다름"))
        elif zlib.crc32(dst.read_bytes()) != zlib.crc32(src.read_bytes()):
            owner = [m for m in MODS if _owns(m, one["install_to"], dst)]
            out.append((one["install_to"], f"다름 · 지금 내용의 주인 {owner or '순정/미상'}"))
    return out


def _owns(name, rel, dst):
    try:
        mod = modstore.read_mod(STORE, name, game="Pokemon Z")
    except Exception:
        return False
    for one in mod.assets:
        if one["install_to"] == rel:
            src = pathlib.Path(mod.folder) / one["file"]
            return src.is_file() and zlib.crc32(src.read_bytes()) == zlib.crc32(dst.read_bytes())
    return False


def cycle(label, install, remove):
    print(f"\n═══ {label}")
    reset()
    trouble = []
    for n in install:
        try:
            modstore.apply(STORE, n, COPY)
        except Exception as e:
            trouble.append(f"설치 {n}: {type(e).__name__} {str(e)[:80]}")
    names = modstore.installed(COPY)
    ratios = {n: modassets.applied(modstore.read_mod(STORE, n, game="Pokemon Z"), COPY)
              for n in MODS if not modstore.read_mod(STORE, n, game="Pokemon Z").scripts
              or modstore.read_mod(STORE, n, game="Pokemon Z").assets}
    print(f"  설치 후 주입 {len(names)}개 · 에셋 판정 "
          + " ".join(f"{n}={v:.0%}" for n, v in ratios.items() if v < 1.0) or "  전부 100%")
    for n in remove:
        try:
            modstore.remove(n, COPY, store=STORE)
        except Exception as e:
            trouble.append(f"제거 {n}: {type(e).__name__} {str(e)[:70]}")
            for rel, why in mismatches(n)[:8]:
                trouble.append(f"    ↳ {rel} — {why}")
    off = pristine()
    print(f"  결과: 걸린 것 {len(trouble)}건 · 순정과 어긋난 자리 {len(off)}개")
    for t in trouble[:12]:
        print("   ", t)
    for rel, why in off[:8]:
        print(f"    · {rel} — {why}")
    return not trouble and not off


if __name__ == "__main__":
    rng = random.Random(20260807)
    plans = {
        "정순 설치 → 정순 제거": (MODS, list(MODS)),
        "정순 설치 → 역순 제거": (MODS, list(reversed(MODS))),
        "역순 설치 → 역순 제거": (list(reversed(MODS)), MODS),
        "겹치는 것 먼저 → 무작위 제거": (
            ["Controller UX", "Z-GUI", "DPPT Font", "한글패치 코어"] +
            [m for m in MODS if m not in ("Controller UX", "Z-GUI", "DPPT Font", "한글패치 코어")],
            rng.sample(MODS, len(MODS))),
        "무작위 설치 → 무작위 제거": (rng.sample(MODS, len(MODS)), rng.sample(MODS, len(MODS))),
    }
    want = sys.argv[1:] or list(plans)
    ok = {}
    for label in want:
        install, remove = plans[label]
        ok[label] = cycle(label, install, remove)
    print("\n═══ 종합")
    for label, good in ok.items():
        print(f"  {'통과' if good else '실패'} — {label}")
