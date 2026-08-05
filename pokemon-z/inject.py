# /// script
# dependencies = ["rubymarshal"]
# ///
"""Pokemon Z(구형 Essentials)용 스크립트 모드 주입기.

    uv run inject.py "UI Text KR" [모드 ...]

이 게임에는 PluginScripts.rxdata가 없어서 코드 모드는 Scripts.rxdata 배열에
섹션으로 덧붙이는 수밖에 없다(RGSS는 배열 순서대로 실행해 나중 정의가 이긴다).
이 도구가 그 덧붙이기를 맡아, 모드 여럿을 파일 하나로 합쳐 관리하지 않아도 되게 한다.

- 기반은 게임 폴더가 아니라 **모드 보관소의 한글패치판** Scripts.rxdata다. 몇 번을
  다시 돌려도 결과가 같고, 게임 폴더에 쌓인 이전 주입 결과를 다시 읽을 일이 없다.
- 모드는 Wishing Star와 같은 보관소 규약을 쓴다: `<보관소>/<이름>/mod.json` +
  번호 붙은 .rb. mod.json의 `expects`(섹션 제목 → 원문 md5)가 있으면 기반이
  기대와 다를 때 멈춘다 — 게임 판이 올라 원문이 바뀌면 훅이 조용히 어긋나기 때문.
- 주입 섹션 제목은 `MOD:<모드명>/<파일명>`. 이 접두사로 기존 주입분을 걷어 낸다.
- 기록은 fangame-library의 CountingWriter를 쓴다(루비식 객체 번호 매기기 —
  rubymarshal 기본 기록기는 문자열 번호가 어긋나 조용히 깨진다).

모드 .rb는 루비 1.8.7 문법으로 써야 한다(해시 로켓, 신형 문법 금지).

설치의 정본은 fangame-library `fanlib/modstore.py`다(같은 규약: MOD: 접두사·Main 앞·
md5 id — 바꾸려면 양쪽을 함께). 이 도구는 개발 반복용으로 남는다 — 기반에서 전체를
다시 짓는 성질이 디버깅에 유용해서다. 그 성질의 이면: **모드를 명시해 돌리면 나열에서
빠진 모드는 결과에서 사라진다**(라이브러리로 설치한 것 포함). 그래서 기본값이 전부이고,
명시 실행 때는 게임에 있던 모드가 빠지면 경고를 낸다.
"""
import argparse
import hashlib
import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from fanlib import rubywrite  # noqa: E402

STORE = Path("/mnt/d/GameVault/mods")
MODS = Path(__file__).resolve().parent / "mods"  # 우리가 짓는 모드의 정본 (git 관리)
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")
MARKER = b"MOD:"


def find_mod(name: str) -> Path:
    """repo(우리 것)를 먼저, 보관소(남에게서 온 것 — 한글패치 등)를 다음에 본다.
    보관소는 게임별 하위 폴더로 나뉜다(<보관소>/<게임>/<모드>)."""
    candidates = sorted(MODS.glob(f"{name}/mod.json")) \
        + sorted(STORE.glob(f"*/{name}/mod.json")) + sorted(STORE.glob(f"{name}/mod.json"))
    for card in candidates:
        return card.parent
    raise SystemExit(f"repo에도 보관소에도 없는 모드예요: {name}")


BASE = find_mod("한글패치 통합") / "Data" / "Scripts.rxdata"


def load_sections(path: Path) -> list:
    from rubymarshal.reader import load

    with open(path, "rb") as fh:
        return load(fh)


def title_of(entry) -> bytes:
    return bytes(entry[1])


def main() -> int:
    ap = argparse.ArgumentParser(description="Scripts.rxdata에 모드 섹션을 주입한다")
    ap.add_argument("mods", nargs="*", help="모드 이름 (비우면 주입형 모드 전부)")
    ap.add_argument("--game", type=Path, default=GAME, help="게임 설치 폴더")
    ap.add_argument("--base", type=Path, default=BASE, help="기반 Scripts.rxdata")
    args = ap.parse_args()

    if not args.mods:
        # 기반부터 다시 짓는 구조라, 모드 하나를 빼먹으면 그 모드가 조용히 빠진다.
        # 그래서 기본값은 「보관소의 주입형 모드 전부」다.
        # repo 정본이 보관소에 수확돼 양쪽에 다 있으므로 이름으로 합친다 —
        # 중복 주입은 같은 alias가 두 번 걸려 무한 재귀를 만든다(2026-08-01 실사고).
        args.mods = sorted({
            json.loads(card.read_text("utf-8"))["name"]
            for card in list(MODS.glob("*/mod.json")) + list(STORE.glob("*/*/mod.json"))
            if json.loads(card.read_text("utf-8")).get("install") == "inject"
        })
        if not args.mods:
            print("보관소에 주입형 모드가 없어요.", file=sys.stderr)
            return 1

    # 전체 재구축이라, 게임에 있던 주입 모드가 이번 나열에서 빠지면 사라진다 — 경고.
    game_scripts = args.game / "Data" / "Scripts.rxdata"
    if game_scripts.exists():
        current = {
            title_of(e).decode("utf-8").removeprefix("MOD:").split("/", 1)[0]
            for e in load_sections(game_scripts) if title_of(e).startswith(MARKER)
        }
        for dropped in sorted(current - set(args.mods)):
            print(f"경고: 게임에 주입돼 있던 「{dropped}」가 이번 나열에 없어요 — "
                  f"전체 재구축이라 결과에서 빠집니다.", file=sys.stderr)

    sections = load_sections(args.base)
    md5_by_title = {}
    for entry in sections:
        source = zlib.decompress(bytes(entry[2]))  # 겸사겸사 전 섹션 무결성 검사
        md5_by_title.setdefault(title_of(entry).decode("utf-8"), hashlib.md5(source).hexdigest())

    kept = [e for e in sections if not title_of(e).startswith(MARKER)]
    main_at = max(i for i, e in enumerate(kept) if title_of(e) == b"Main")

    injected = []
    for mod_name in args.mods:
        mod_dir = find_mod(mod_name)
        meta = json.loads((mod_dir / "mod.json").read_text("utf-8"))
        for section_title, want in meta.get("expects", {}).items():
            got = md5_by_title.get(section_title)
            if got != want:
                print(f"멈춤: {mod_name}의 기대와 기반이 다르다 — 섹션 {section_title}"
                      f" md5 {got} (기대 {want}). 게임 판이 바뀌었으면 훅을 다시 확인할 것.",
                      file=sys.stderr)
                return 1
        for script in meta["scripts"]:
            source = (mod_dir / script["file"]).read_bytes()
            title = f"MOD:{mod_name}/{script['script_name']}".encode("utf-8")
            sid = int(hashlib.md5(title).hexdigest()[:7], 16)  # 결정적이고 안 겹치는 id
            injected.append([sid, title, zlib.compress(source)])
            print(f"  + {title.decode('utf-8')} ({len(source)}자)")

    result = kept[:main_at] + injected + kept[main_at:]
    payload = rubywrite.dumps(result)

    # 쓰기 전에 되읽어 왕복을 확인한다
    import io
    from rubymarshal.reader import load as rload

    again = rload(io.BytesIO(payload))
    assert len(again) == len(result), "왕복에서 섹션 수가 달라졌다"
    for a, b in zip(again, result):
        assert title_of(a) == bytes(b[1]) and zlib.decompress(bytes(a[2])) == zlib.decompress(bytes(b[2]))

    out = args.game / "Data" / "Scripts.rxdata"
    out.write_bytes(payload)
    print(f"{out} ← 기반 {len(kept)}섹션 + 주입 {len(injected)}섹션")

    # repo가 정본인 모드는 보관소에 사본을 수확해 둔다 — 라이브러리 화면이
    # 보관소만 보므로, 이게 없으면 모드가 목록에서 사라진다.
    import shutil

    for mod_name in args.mods:
        src = MODS / mod_name
        if src.is_dir():
            # 라이브러리와 같은 규칙(mod.json game 필드, 콜론 제거)으로 게임 폴더를
            # 정한다 — 딴 폴더에 앉히면 라이브러리 설치 현황에서 사라진다(2026-08-01).
            meta = json.loads((src / "mod.json").read_text("utf-8"))
            dst = STORE / meta["game"].replace(":", "").strip() / mod_name
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  보관소 수확: {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
