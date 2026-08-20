# /// script
# requires-python = ">=3.12"
# ///
"""동봉용 통합 모드 둘을 보관소에 짓는다 — `UI KR` · `Utility Pack`.

    uv run runa/make-union-mods.py [--store <보관소>] [--dry-run]

합본(v6)에 싣는 코드 모드가 아홉이라 낱개로 주입하면 받는 쪽 서랍이 지저분해진다.
쓰임이 같은 것끼리 묶어 둘로 낸다. 재료 모드는 그대로 두고 여기서 사본을 뜬다.

재료는 **보관소**다(저장소 `mods/`가 아니다). 셋 다 보관소만 가진 것이 있기 때문이다 —
Z-GUI의 제3자 GUI 그림 여덟 장은 git에 없고, Battle Scene Speed·Better Movements는
poke-essentials 몫이며(보관소에 이미 서 있다), 유지자 실기 손질이 먼저 닿는 곳도
보관소다. 합본 조립기(`share/make_package.py`)가 주입해 오는 자리와 같은 자리이기도 하다.

짓는 법은 이어붙이기다 — 재료 모드의 `.rb`를 파일째 옮기고 이름 앞에 번호를 붙여
로드 순서를 못 박는다(`MOD:Utility Pack/010_Battle Order_001_TurnOrder.rb`). 재정의가
겹치는 자리가 없어서(2026-08-20 전수 대조) 이어붙임만으로 선다. 카드의 `expects`·
`touches`·`order`·`requires`·`provides`·`conflicts`와 기준선(`baseline/`)은 합집합으로
옮긴다 — 기준선이 따라와야 패치판 위에서 `expects`가 어긋나도 modkit이 훅 메서드를
다시 대조해 넘어간다.

같은 재료로 다시 돌리면 같은 산출이 나온다. 옆(`.new`)에 다 지은 뒤 갈아 끼운다 —
제자리에서 지우고 채우면 하드링크로 이어진 원본 모드까지 함께 바뀐다.
"""
import argparse
import json
import shutil
from pathlib import Path

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame")

# 통합 모드 → (한 줄 소개, 머리말, 재료 모드 차례대로)
UNIONS = {
    "UI KR": (
        "화면 문구 한국어화와 GUI 그림을 한 벌로 묶습니다",
        "한글패치 합본이 싣는 화면 쪽 모드를 한 벌로 묶은 것이에요. 스크립트에 박혀 "
        "번역표로는 못 고치는 화면 문구를 한국어로 바꾸고, 전투·도감 GUI 그림을 개선판과 "
        "번역판으로 갈아 끼워요.",
        ["UI Text KR", "Z-GUI"],
    ),
    "Utility Pack": (
        "배틀·이동·지도의 편의 개선 일곱 가지를 한 벌로 묶습니다",
        "한글패치 합본이 싣는 편의 모드 일곱을 한 벌로 묶은 것이에요. 서로 건드리는 "
        "자리가 겹치지 않아 함께 서고, 낱개로 받아 두었다면 그쪽을 지우고 이것만 얹으면 "
        "돼요.",
        ["Battle Order", "Battle Scene Speed", "Better Movements", "Bridge Fix",
         "Map Cursor Snap", "Type Matchup", "Native Tilemap"],
    ),
}
SWALLOWED = "통합본이 이미 품고 있어요 — 따로 얹으면 같은 코드가 두 겹으로 걸려요."


def _card(folder: Path) -> dict:
    return json.loads((folder / "mod.json").read_text(encoding="utf-8"))


def _assets(card: dict) -> list:
    """카드의 에셋 목록을 사전 꼴로 고른다 — 이름만 적힌 옛 꼴도 받는다."""
    out = []
    for one in card.get("assets") or []:
        out.append(one if isinstance(one, dict) else {"file": one, "install_to": one})
    return out


def build(name: str, store: Path, dry: bool = False) -> Path:
    summary, intro, members = UNIONS[name]
    folder = store / name
    stage = folder.with_name(folder.name + ".new")

    def claim(bag: dict, items, member: str, what: str) -> None:
        """건드리는 자리를 재료 이름과 함께 적는다 — 겹치면 멈춘다.

        조용히 접으면 재료 카드가 낡아 같은 자리를 둘이 잡게 됐을 때 조립이 침묵한다.
        나중 정의가 이기는 주입 방식이라 그 침묵이 곧 한쪽 기능의 실종이다.
        """
        for one in items or []:
            if one in bag:
                raise SystemExit(f"{name}: {what} `{one}`를 {bag[one]}와 {member}가 함께 "
                                 "건드려요 — 재료 카드를 대조해 한쪽을 정리해요")
            bag[one] = member

    scripts, assets, touch_methods, touch_files = [], [], {}, {}
    expects, order_after, order_before = {}, [], []
    requires, provides, conflicts = [], [], {}
    baseline, blurbs = {}, []
    step = 0

    for member in members:
        src = store / member
        if not (src / "mod.json").is_file():
            raise SystemExit(f"재료 모드가 없어요: {src}")
        card = _card(src)
        blurbs.append(f"· {member} — {card.get('summary') or card['name']}")

        for entry in card.get("scripts") or []:
            step += 10
            filename = f"{step:03d}_{member}_{entry['file']}"
            if not dry:
                shutil.copy2(src / entry["file"], stage / filename)
            scripts.append({"file": filename, "script_name": filename})

        for asset in _assets(card):
            if not dry:
                target = stage / asset["file"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src / asset["file"], target)
            assets.append(asset)

        for place, digest in (card.get("expects") or {}).items():
            if expects.get(place, digest) != digest:
                raise SystemExit(
                    f"{name}: `{place}` 지문이 재료끼리 어긋나요 — {member}가 {digest}, "
                    f"앞의 재료가 {expects[place]}. 재료 모드를 먼저 맞춰요")
            expects[place] = digest

        touches = card.get("touches") or {}
        claim(touch_methods, touches.get("methods"), member, "메서드")
        claim(touch_files, touches.get("files"), member, "파일")
        told = card.get("order") or {}
        order_after += told.get("after") or []
        order_before += told.get("before") or []
        requires += card.get("requires") or []
        provides += card.get("provides") or []
        for enemy, why in (card.get("conflicts") or {}).items():
            said = conflicts.get(enemy)
            conflicts[enemy] = why if said in (None, why) else f"{said}; {why}"

        room = src / "baseline"
        for rb in sorted(room.glob("*.rb")) if room.is_dir() else []:
            seen = baseline.get(rb.name)
            if seen is not None and seen.read_bytes() != rb.read_bytes():
                raise SystemExit(f"{name}: 기준선 {rb.name}이 재료끼리 달라요 — 손으로 가려요")
            baseline[rb.name] = rb

    if dry:
        print(f"{name} — 스크립트 {len(scripts)}개 · 에셋 {len(assets)}개 · "
              f"기준선 {len(baseline)}개 (짓지 않았어요)")
        return folder

    for fname, rb in sorted(baseline.items()):
        (stage / "baseline").mkdir(exist_ok=True)
        shutil.copy2(rb, stage / "baseline" / fname)

    # 재료 모드 자신은 「함께 못 서는 것」으로 적는다 — 통합본이 같은 코드를 품고 있다.
    for member in members:
        conflicts[member] = SWALLOWED
    order_after = [one for one in dict.fromkeys(order_after) if one not in members]
    order_before = [one for one in dict.fromkeys(order_before) if one not in members]

    card = {
        "name": name,
        "game": "Pokemon Z Fangame",
        "version": "6",
        "summary": summary,
        "description": intro + "\n\n담긴 모드는 이것들이에요.\n" + "\n".join(blurbs)
        + "\n\n설치는 파일 복사가 아니라 주입입니다 — 한글패치판 Scripts.rxdata에 섹션으로"
          " 덧붙여요. 낱개 모드의 설명과 설정값(파일 첫머리의 상수)은 그대로예요.",
        "engine": "essentials-v16",
        "install": "inject",
        "created_at": "2026-08-20",
        "scripts": scripts,
        "assets": assets,
        "touches": {
            "methods": sorted(touch_methods),
            "files": sorted(touch_files),
        },
        "expects": dict(sorted(expects.items())),
        "baseline_taken": bool(baseline),
    }
    for key, value in (("order", {k: v for k, v in
                                  (("after", order_after), ("before", order_before)) if v}),
                       ("requires", sorted(dict.fromkeys(requires))),
                       ("provides", sorted(dict.fromkeys(provides))),
                       ("conflicts", dict(sorted(conflicts.items())))):
        if value:
            card[key] = value
    (stage / "mod.json").write_text(
        json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    old = folder.with_name(folder.name + ".old")
    if old.exists():
        shutil.rmtree(old)
    if folder.exists():
        folder.rename(old)
    stage.rename(folder)
    if old.exists():
        shutil.rmtree(old)

    print(f"{folder} — 스크립트 {len(scripts)}개 · 에셋 {len(assets)}개 · "
          f"기준선 {len(baseline)}개 · expects {len(expects)}자리")
    return folder


def main() -> None:
    ap = argparse.ArgumentParser(description="동봉용 통합 모드 둘을 짓는다")
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=sorted(UNIONS), help="하나만 짓는다")
    args = ap.parse_args()

    for name in ([args.only] if args.only else list(UNIONS)):
        stage = args.store / (name + ".new")
        if stage.exists():
            shutil.rmtree(stage)
        if not args.dry_run:
            stage.mkdir(parents=True)
        build(name, args.store, dry=args.dry_run)


if __name__ == "__main__":
    main()
