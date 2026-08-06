# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal", "fonttools"]
# ///
"""루나판 한글패치 모드를 정본 재료로 다시 짓는다.

    uv run runa/build-mod.py                 # 모드 보관소에 짓는다
    uv run runa/build-mod.py --install "/mnt/d/Game/Pokemon Z/V2.18 루나판"   # 짓고 게임에 얹는다
    uv run runa/build-mod.py --dry-run       # 짓기만 하고 보관소는 안 건드린다
    uv run runa/build-mod.py --fix-base      # 「한글패치 통합」 코어에 섞인 주입 섹션 제거
    uv run runa/build-mod.py --scan-vanilla <정본 게임 폴더>   # 지문표 갱신

왜 이 도구가 있나. 루나판 모드는 이미 패치가 얹힌 게임을 복제해 손으로 만든 것이라,
그 폴더 자체가 유일본이었다. 한 번의 사고로 사라지면 되살릴 길이 없고, 모드 보관본과
게임 사이를 사람이 복사로 오가는 동안 조용히 어긋난다(실제로 하드링크 너머로 「한글패치
통합」의 코어까지 함께 바뀌어 있었다). 그래서 **재료에서 매번 다시 짓는다** — 몇 번을
돌려도 결과가 같고, 폴더가 통째로 없어져도 이 한 줄로 돌아온다.

루나판이 원판 한글패치와 다른 곳은 셋뿐이다.

  korean.dat  번역표 정본에서 다시 굽되 문자열마다 UTF-8 인코딩 딱지를 붙인다. 딱지가
              없으면 루비 1.9+ 실행기(루나·조이플레이 계열)가 문자열을 ASCII-8BIT로 읽어
              번역표 조회가 전부 빗나가고 결국 멎는다. 1.8.7은 딱지를 무시한다.
  Fonts       게임이 요청하는 패밀리명 16종을 한글 든 픽셀 폰트가 직접 들게 개명해 넣는다.
              폰트 대체 설정(fontSub)을 안 읽는 엔진에서도 잡히게 하는 유일한 길이다.
  mkxp.json   그래서 fontSub 를 두지 않는다.

나머지는 「한글패치 통합」 모드에서 그대로 가져온다. 코어(Scripts.rxdata)는 가져오면서
주입 섹션(MOD:*)을 걷어낸다 — 주입형 모드는 각자 제 모드로 설치되는 것이 맞고, 한글패치
안에 구워 두면 설치한 적 없는 모드가 딸려 들어간다.
"""
import argparse
import io
import json
import shutil
import subprocess
import sys
import zlib
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "vendor"))

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame")
BASE_MOD = "한글패치 통합"
NAME = "한글패치 통합 (루나)"
SCRATCH = Path("/mnt/d/GameVault/trash")  # 짓는 곳·직전 판을 두는 곳 (보관소 밖이라야 한다 —
#                                           보관소 안에 두면 목록에 유령 모드로 뜬다)
FAMILIES = json.loads((HERE / "fonts" / "families.json").read_text("utf-8"))["families"]
MASTER = HERE / "fonts" / "dppt-kr.ttf"
VANILLA_CRC = HERE / "vanilla-crc.json"
MOD_MARK = b"MOD:"

# 「한글패치 통합」이 아직 들고 있지만 루나판은 안 싣는 것.
# 글자가 구워진 그림 세 장은 2026-08-04에 GUI 모드 몫으로 넘겼고(순정 그림체를 지킨
# 한글화를 Z-GUI가 들고 있다), 옛 판은 docs/attic/2026-08-04-kr-3장-pre-zgui에 남겼다.
# 원판 모드에서는 파일만 남아 있어 그대로 딸려 나가던 자리다.
DROP = (
    "Graphics/Pictures/battleCommandButtons.png",
    "Graphics/Pictures/pokedexTypes.png",
    "Graphics/Pictures/types.png",
)

FONT_NOTE = [
    '// 루나판: fontSub 를 두지 않는다. 조이플레이 계열 엔진은 이 키를 안 읽고 Fonts',
    '// 폴더 폰트의 내부 패밀리명으로만 찾으므로, 요청 이름("Power Green" 등)을 한글 든',
    '// 픽셀 폰트가 직접 들고 있게 했다(pkmn*.ttf 교체 · kr-*.ttf 추가).',
]

DESCRIPTION = """포켓몬 Z 한글패치를, 최신 루비로 도는 실행기(루나·조이플레이 계열)에서도 그대로 돌아가게 손본 판이에요. 담긴 번역과 그림·소리는 「한글패치 통합」과 같은 것이고, 그 위에 세 가지가 다릅니다.

번역표에 인코딩 딱지 — 문자열마다 UTF-8 표시를 붙였어요. 이게 없으면 루비 1.9 이상에서 게임이 번역표의 글자를 바이트 뭉치로 읽어, 조회가 전부 빗나가 스페인어가 나오다가 결국 Encoding::CompatibilityError로 멎습니다. 옛 실행기(루비 1.8.7, 데스크톱 mkxp-z)는 이 표시를 무시하므로 그쪽에서도 그대로 돌아가요.

한글 든 픽셀 폰트 16벌 — 게임이 찾는 이름("Power Green", "Arial" 등)을 한글이 든 폰트가 직접 들게 개명해 넣었어요. 원판 pkmn*.ttf 여덟 벌이 그 이름을 들고 있으면서 한글이 0자라, 조이플레이처럼 폰트 대체 설정을 안 읽는 엔진에서는 글자가 네모로 떨어졌습니다. 폰트는 dppt 픽셀 폰트에 없던 글자 106자(대괄호·따옴표·낱자모)를 갈무리에서 들여 채운 것이에요.

폰트 대체 설정 없음 — 위 이유로 mkxp.json의 fontSub 를 뺐어요.

글자 그림자와 굵게가 픽셀 폰트에 비해 두껍게 보이면 「Pixel Shadow」 모드를 함께 설치하세요. 원판 폰트 크기에 맞춰진 값이라 획이 1픽셀인 폰트에서는 그림자가 글자보다 굵어 보입니다.

이 모드는 pokemon-fangame-kr 저장소의 runa/build-mod.py 가 번역표 정본과 「한글패치 통합」에서 매번 다시 짓습니다. 폴더를 손으로 고치지 마세요 — 다음 빌드에 덮입니다."""


# ── 재료 만들기 ────────────────────────────────────────────────

def clean_core(blob: bytes) -> bytes:
    """코어에서 주입 섹션(MOD:*)을 걷어낸다. 읽고-쓰고-되읽어 왕복을 확인한다."""
    from fanlib import rubywrite
    from rubymarshal.reader import load

    sections = load(io.BytesIO(blob))
    kept = [one for one in sections if not bytes(one[1]).startswith(MOD_MARK)]
    out = rubywrite.dumps(kept)
    again = load(io.BytesIO(out))
    assert len(again) == len(kept), "왕복에서 섹션 수가 달라졌다"
    for a, b in zip(again, kept):
        assert bytes(a[1]) == bytes(b[1])
        assert zlib.decompress(bytes(a[2])) == zlib.decompress(bytes(b[2]))
    return out


def font_bytes(family: str) -> bytes:
    """마스터를 그 패밀리명으로 갈아 낀 한 벌.

    저장 시각을 다시 매기지 않는다(recalcTimestamp=False) — 그러지 않으면 같은 재료로
    지어도 매번 다른 바이트가 나와, 설치 판정이 「달라졌다」로 읽는다.
    """
    from fontTools.ttLib import TTFont

    font = TTFont(MASTER, recalcTimestamp=False)
    postscript = family.replace(" ", "")
    for record in font["name"].names:
        if record.nameID in (1, 4, 16):
            record.string = family
        elif record.nameID == 6:
            record.string = postscript
    font["head"].modified = font["head"].created
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def runa_mkxp(text: str) -> str:
    """fontSub 블록을 빼고 그 자리에 이유를 적는다.

    주석으로 죽여 둔 예시 fontSub 가 파일에 하나 더 있다 — 그것까지 지우면 설정이
    통째로 어긋난다(2026-08-06 실사고). 그래서 주석이 아닌 줄만 고른다.
    """
    lines = text.splitlines()
    heads = [i for i, line in enumerate(lines)
             if line.lstrip().startswith('"fontSub"') and not line.lstrip().startswith("//")]
    assert len(heads) == 1, f"살아 있는 fontSub 줄이 {len(heads)}개다 — 손으로 확인할 것"
    start = heads[0]
    stop = next(i for i in range(start, len(lines)) if lines[i].rstrip().endswith("],"))
    out = "\n".join(lines[:start] + FONT_NOTE + lines[stop + 1:]) + "\n"

    before, after = _jsonc(text), _jsonc(out)
    assert "fontSub" in before and "fontSub" not in after, "fontSub 가 안 빠졌다"
    assert {k: v for k, v in before.items() if k != "fontSub"} == after, "딴 설정까지 바뀌었다"
    return out


def _jsonc(text: str) -> dict:
    """주석과 꼬리 쉼표를 걷어내고 읽는다 — mkxp.json은 순수 JSON이 아니다."""
    import re

    body = re.sub(r"^\s*//.*$", "", text, flags=re.M)
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", body))


def build_dat(out: Path) -> None:
    """번역표 정본에서 korean.dat를 굽는다(딱지 붙는 판 — 이 갈래의 build.py)."""
    run = subprocess.run(
        ["uv", "run", "build.py", f"--out={out}"],
        cwd=REPO / "translate", capture_output=True, text=True)
    sys.stdout.write(run.stdout)
    if run.returncode != 0:
        sys.exit(run.stderr or "korean.dat 빌드가 실패했어요")


# ── 지문 ──────────────────────────────────────────────────────

def crc_of(path: Path) -> int:
    running = 0
    with open(path, "rb") as handle:
        while chunk := handle.read(1 << 20):
            running = zlib.crc32(chunk, running)
    return running


def scan_vanilla(game_dir: Path, wanted) -> dict:
    """정본 게임에서, 이 모드가 덮을 자리의 지문을 뜬다.

    모드가 새로 놓는 자리(정본에 없는 파일)는 적지 않는다 — 대조할 원본이 없다.
    """
    found = {}
    for where in sorted(wanted):
        target = game_dir / where
        if target.is_file():
            found[where] = crc_of(target)
    return found


# ── 조립 ──────────────────────────────────────────────────────

def build(store: Path, dry: bool) -> int:
    base_dir = store / BASE_MOD
    base_meta = json.loads((base_dir / "mod.json").read_text("utf-8"))
    fingerprints = json.loads(VANILLA_CRC.read_text("utf-8"))["crc"]

    room = SCRATCH / f"{NAME}.building"
    if room.exists():
        shutil.rmtree(room)
    room.mkdir(parents=True)

    print("① 번역표 정본에서 korean.dat (인코딩 딱지 붙는 판)")
    (room / "Data").mkdir(parents=True, exist_ok=True)
    build_dat(room / "Data" / "korean.dat")

    print("② 「한글패치 통합」에서 나머지 자산")
    assets = []
    for one in base_meta["assets"]:
        where = one["install_to"]
        assert one["file"] == where, f"모드 안 자리와 게임 자리가 다르다: {one}"
        if where in DROP:
            continue
        target = room / where
        target.parent.mkdir(parents=True, exist_ok=True)
        if where == "Data/korean.dat":
            pass                                   # ①에서 이미 구웠다
        elif where == "Data/Scripts.rxdata":
            target.write_bytes(clean_core((base_dir / where).read_bytes()))
        elif where == "mkxp.json":
            target.write_text(runa_mkxp((base_dir / where).read_text("utf-8")), "utf-8")
        else:
            shutil.copy2(base_dir / where, target)
        assets.append(where)
    print(f"   {len(assets)}개 (뺀 것 {len(DROP)}: 글자 구운 그림 — GUI 모드 몫)")

    print("③ 게임이 요청하는 이름 16벌로 폰트 찍어 내기")
    (room / "Fonts").mkdir(parents=True, exist_ok=True)
    for name, family in FAMILIES.items():
        (room / "Fonts" / name).write_bytes(font_bytes(family))
        assets.append(f"Fonts/{name}")

    shutil.copy2(base_dir / "읽어주세요.txt", room / "읽어주세요.txt")

    print("④ 모드 카드")
    card = {
        "name": NAME,
        "game": base_meta["game"],
        "description": DESCRIPTION,
        "summary": "포켓몬 Z 한글패치 — 최신 루비 실행기(루나·조이플레이)용",
        "from_build": base_meta.get("from_build", "V2.18"),
        "built_at": str(date.today()),
        "built_by": "runa/build-mod.py",
        "baseline_taken": False,
        "scripts": [],
        "assets": [
            {"file": where, "install_to": where,
             **({"replaces_crc": fingerprints[where]} if where in fingerprints else {})}
            for where in sorted(set(assets))
        ],
        "touches": {"methods": [], "files": sorted(set(assets))},
    }
    (room / "mod.json").write_text(
        json.dumps(card, ensure_ascii=False, indent=1) + "\n", "utf-8")
    marked = sum(1 for one in card["assets"] if "replaces_crc" in one)
    print(f"   자산 {len(card['assets'])} · 원본 지문 {marked} · 새로 놓는 자리 "
          f"{len(card['assets']) - marked}")

    problems = verify(room, card)
    if problems:
        for line in problems:
            print(f"   ✗ {line}", file=sys.stderr)
        return 1

    if dry:
        print(f"dry-run — 보관소에 넣지 않았어요. 지은 것: {room}")
        return 0

    live = store / NAME
    prev = SCRATCH / f"{NAME}.prev"
    if prev.exists():
        shutil.rmtree(prev)
    if live.exists():
        live.rename(prev)          # 직전 판은 보관소 밖에 둔다
    room.rename(live)
    print(f"보관소에 세웠어요: {live}")
    if prev.exists():
        print(f"   직전 판: {prev} (확인 뒤 지우면 돼요)")
    return 0


def install(store: Path, game_dir: Path) -> int:
    """modkit으로 게임에 얹는다 — 손으로 복사하지 않는 이유가 여기 있다.

    modkit이 얹어야 덮은 자리마다 원본 백업(`.orig`)이 남는다. 손으로 넣은 자리는
    그 백업이 없어, 호환 검사가 「우리가 넣은 폰트」를 게임의 원본으로 읽고 판이
    달라졌다고 경고한다(루나판이 실제로 그 상태였다).
    """
    modkit = Path.home() / "workspace" / "claude-native" / "sketches" / "essentials-modkit"
    if not (modkit / "modkit" / "modstore.py").is_file():
        sys.exit(f"modkit을 못 찾았어요: {modkit}")
    sys.path.insert(0, str(modkit))
    from modkit import modstore  # noqa: E402

    result = modstore.apply(store.parent, NAME, game_dir)
    print(f"{game_dir} ← {result['did']} · 자산 {result['assets']}")
    for line in result["warnings"]:
        print(f"   경고: {line}")
    return 0


def verify(room: Path, card: dict) -> list:
    """카드가 적은 것이 실제로 다 있고, 셋이 제대로 갈렸는가."""
    problems = []
    for one in card["assets"]:
        if not (room / one["file"]).is_file():
            problems.append(f"카드에 적힌 파일이 없어요: {one['file']}")
    from rubymarshal.reader import load

    # 딱지가 붙은 문자열은 판독기가 RubyString으로, 안 붙은 것은 bytes로 돌려준다 —
    # 딱지 수를 세는 것보다 이쪽이 「루비가 뭐로 읽느냐」에 곧바로 답한다.
    table = load(io.BytesIO((room / "Data/korean.dat").read_bytes()))
    sample = load(io.BytesIO(bytes(table[23]._private_data)))[0][0]
    if isinstance(sample, (bytes, bytearray)):
        problems.append("korean.dat 문자열에 UTF-8 딱지가 없어요 — 루나에서 조회가 전부 빗나가요")

    core = load(io.BytesIO((room / "Data/Scripts.rxdata").read_bytes()))
    baked = [bytes(one[1]).decode("utf-8") for one in core if bytes(one[1]).startswith(MOD_MARK)]
    if baked:
        problems.append(f"코어에 주입 섹션이 남아 있어요: {baked}")
    from fontTools.ttLib import TTFont
    for name, family in FAMILIES.items():
        font = TTFont(room / "Fonts" / name, lazy=True)
        got = {r.toUnicode() for r in font["name"].names if r.nameID == 1}
        if got != {family}:
            problems.append(f"Fonts/{name}의 패밀리명이 {got} 예요 (기대 {family!r})")
    return problems


def fix_base(store: Path) -> int:
    """「한글패치 통합」의 코어에 섞여 들어간 주입 섹션을 걷어낸다.

    루나판 폴더가 하드링크로 이어져 있어, 루나판에 코어를 복사한 동작이 원판 모드의
    코어까지 함께 바꿔 놓았다. 옆에 쓰고 이름을 바꿔 갈아 낀다 — 제자리에서 고치면
    또 링크 너머로 번진다.
    """
    core = store / BASE_MOD / "Data" / "Scripts.rxdata"
    from rubymarshal.reader import load

    baked = [bytes(one[1]).decode("utf-8")
             for one in load(io.BytesIO(core.read_bytes()))
             if bytes(one[1]).startswith(MOD_MARK)]
    if not baked:
        print("「한글패치 통합」 코어는 깨끗해요 — 할 일 없음")
        return 0
    spare = core.with_name(core.name + ".writing")
    spare.write_bytes(clean_core(core.read_bytes()))
    spare.replace(core)
    print(f"주입 섹션 {len(baked)}개를 걷어냈어요: {', '.join(baked)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="루나판 한글패치 모드를 다시 짓는다")
    ap.add_argument("--store", type=Path, default=STORE, help="모드 보관소의 게임 폴더")
    ap.add_argument("--dry-run", action="store_true", help="짓되 보관소는 안 건드린다")
    ap.add_argument("--fix-base", action="store_true", help="원판 모드 코어의 주입 섹션 제거")
    ap.add_argument("--scan-vanilla", type=Path, help="정본 게임 폴더 — 지문표를 다시 뜬다")
    ap.add_argument("--install", type=Path, metavar="게임폴더",
                    help="짓고 나서 그 게임에 modkit으로 얹는다 (게임을 꺼 두어야 한다)")
    args = ap.parse_args()

    if args.fix_base:
        return fix_base(args.store)

    if args.scan_vanilla:
        base_meta = json.loads((args.store / BASE_MOD / "mod.json").read_text("utf-8"))
        wanted = [one["install_to"] for one in base_meta["assets"]] \
            + [f"Fonts/{name}" for name in FAMILIES]
        found = scan_vanilla(args.scan_vanilla, wanted)
        VANILLA_CRC.write_text(json.dumps({
            "_읽는이에게": "정본 게임에서 이 모드가 덮을 자리의 CRC32. 모드 카드의 "
                          "replaces_crc가 여기서 나온다 — 게임 판이 오르면 다시 뜬다.",
            "from_build": args.scan_vanilla.name,
            "scanned_at": str(date.today()),
            "crc": found,
        }, ensure_ascii=False, indent=1) + "\n", "utf-8")
        print(f"{VANILLA_CRC} — 자리 {len(wanted)} 중 정본에 있는 {len(found)}개의 지문")
        return 0

    failed = build(args.store, args.dry_run)
    if failed or args.dry_run or not args.install:
        return failed
    return install(args.store, args.install)


if __name__ == "__main__":
    sys.exit(main())
