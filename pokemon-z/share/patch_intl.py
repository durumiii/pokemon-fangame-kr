# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scripts.rxdata 보간 리터럴 수술 — _INTL("...#{x}...") → _INTL("...{1}...",x).

루비 보간이 _INTL 리터럴 안에 있으면 런타임 문자열이 매번 달라져 번역표 키와
영원히 안 맞는다(원장 티켓 「루비 보간 리터럴 12곳」). 이 도구는 원문 소스를
정확 일치로 치환해 정상 템플릿 경로에 합류시킨다. 대응 번역은
translate/ko/23-script-texts.add.jsonl (「보간 수술」 src 행들).

12곳 중 수술 대상은 6곳 — 주머니 번호 보간 5곳은 런타임 키(bagPocket1~8)가
이미 dat에 번역돼 있어 손댈 필요가 없고, 1곳(166 타일퍼즐)은 그래픽 경로다.

멱등: 새 문자열이 이미 있으면 건너뛴다. 옛/새 어느 쪽도 없으면 에러로 멈춘다
(게임 판 갱신으로 원문이 바뀐 신호).

usage: uv run patch_intl.py [대상 Scripts.rxdata ...]
  무인자면 보관소 기반판 + 게임 설치본 둘 다.
"""
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from rubymarshal.reader import load  # noqa: E402
from fanlib import rubywrite  # noqa: E402

DEFAULT_TARGETS = [
    Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/Scripts.rxdata"),
    Path("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata"),
]

# (섹션명 실마리, 옛 소스, 새 소스) — 옛 소스는 추출본과 글자 단위 일치해야 한다.
EDITS = [
    ("PokeBattle_Battler",
     '_INTL("¡#{pbThis} alteró las dimensiones!")',
     '_INTL("¡{1} alteró las dimensiones!",pbThis)'),
    ("PokeBattle_Battle",
     '_INTL("¡Solo puedes capturar Pokémon de tipo #{allowed_type}!")',
     '_INTL("¡Solo puedes capturar Pokémon de tipo {1}!",allowed_type)'),
    ("Following",
     '_INTL("#{$Trainer.party[0].name} está debilitado.\\nApenas puede tenerse en pie...")',
     '_INTL("{1} está debilitado.\\nApenas puede tenerse en pie...",$Trainer.party[0].name)'),
    ("Following",
     '_INTL("Sin duda, tienes el mejor #{$Trainer.party[0].name} del mundo.")',
     '_INTL("Sin duda, tienes el mejor {1} del mundo.",$Trainer.party[0].name)'),
    ("Cambia Habilidades",
     '_INTL("¿Qué habilidad quieres para #{pokemon.name}?")',
     '_INTL("¿Qué habilidad quieres para {1}?",pokemon.name)'),
]

# 이벤트 선택지(command_102) — 선택지 문자열이 번역 조회 없이 pbShowCommands로
# 직행해 Sí/No가 스페인어로 노출되는 기능 버그(원장 「제보 6건」 첫 티켓).
# Messages 절이 Interpreter/Game_Interpreter 양쪽에 같은 본문을 정의하므로
# 한 EDIT이 2곳을 치환한다. 조회는 게임의 정규 사슬(현재 맵 해시 → 맵0 공통
# 이벤트 폴백)을 그대로 탄다. 루비 1.8 문법 유의.
EDITS += [
    ("Messages",
     "command=Kernel.pbShowCommands(nil,@list[@index].parameters[0],@list[@index].parameters[1])",
     "command=Kernel.pbShowCommands(nil,@list[@index].parameters[0].collect{|c| "
     "MessageTypes.getFromMapHash($game_map ? $game_map.map_id : 0,c)},"
     "@list[@index].parameters[1])"),
]

# 부적(Amuleto) 18종 — pbAmuleto(116_PItem_ItemEffects)가 번역된 아이템 이름을
# 스페인어 원문과 문자열 비교해 인카운터 스위치(280~297)를 켠다. 이름이
# 한글화되면 영원히 거짓이 되는 기능 버그라, 이름 비교를 상수 비교로 수술한다.
_AMULETOS = [
    ("Amuleto Bicho", "AMULETOBICHO"), ("Amuleto Siniestro", "AMULETOSINIESTRO"),
    ("Amuleto Dragón", "AMULETODRAGON"), ("Amuleto Eléctrico", "AMULETOELECTRICO"),
    ("Amuleto Hada", "AMULETOHADA"), ("Amuleto Lucha", "AMULETOLUCHA"),
    ("Amuleto Fuego", "AMULETOFUEGO"), ("Amuleto Volador", "AMULETOVOLADOR"),
    ("Amuleto Fantasma", "AMULETOFANTASMA"), ("Amuleto Planta", "AMULETOPLANTA"),
    ("Amuleto Tierra", "AMULETOTIERRA"), ("Amuleto Hielo", "AMULETOHIELO"),
    ("Amuleto Normal", "AMULETONORMAL"), ("Amuleto Veneno", "AMULETOVENENO"),
    ("Amuleto Psíquico", "AMULETOPSIQUICO"), ("Amuleto Roca", "AMULETOROCA"),
    ("Amuleto Acero", "AMULETOACERO"), ("Amuleto Agua", "AMULETOAGUA"),
]
EDITS += [
    ("PItem_ItemEffects",
     f'PBItems.getName(item) == "{name}"',
     f'isConst?(item,PBItems,:{const})')
    for name, const in _AMULETOS
]


def patch_file(path: Path) -> None:
    secs = load(open(path, "rb"))
    done = skipped = 0
    for hint, old, new in EDITS:
        hit = False
        for sec in secs:
            name = bytes(sec[1]).decode("utf-8", "replace")
            if hint not in name or name.startswith("MOD:"):
                continue
            src = zlib.decompress(bytes(sec[2])).decode("utf-8")
            if new in src and old not in src:
                skipped += 1
                hit = True
                break
            if old in src:
                n = src.count(old)
                sec[2] = zlib.compress(src.replace(old, new).encode("utf-8"))
                print(f"  {name}: {n}곳 치환")
                done += n
                hit = True
                break
        if not hit:
            sys.exit(f"중단: {path} 의 '{hint}' 절에서 옛/새 소스 모두 못 찾음 — 원문이 바뀌었는지 확인")
    if done:
        bak = path.with_suffix(".rxdata.pre-intl.bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())
        with open(path, "wb") as fd:
            rubywrite.dump(fd, secs)
    print(f"{path}: 치환 {done}곳, 기적용 건너뜀 {skipped}건")


if __name__ == "__main__":
    targets = [Path(a) for a in sys.argv[1:]] or DEFAULT_TARGETS
    for t in targets:
        patch_file(t)
