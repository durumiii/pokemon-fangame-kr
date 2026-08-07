# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""Scripts.rxdata 보간 리터럴 수술 — _INTL("...#{x}...") → _INTL("...{1}...",x).

루비 보간이 _INTL 리터럴 안에 있으면 런타임 문자열이 매번 달라져 번역표 키와
영원히 안 맞는다(제보 목록의 「루비 보간 리터럴 12곳」). 이 도구는 원문 소스를
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
    Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/Scripts.rxdata"),
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
# 직행해 Sí/No가 스페인어로 노출되는 기능 버그(제보 목록 「제보 6건」의 첫 건).
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

# 앙코르 성공 문구가 저주 문구다(원작 소스의 문자열 오배치 — 2026-08-05 제보·조사).
# 0BC(Otra Vez/Encore)가 Encore 상태 값 셋을 세팅한 바로 다음 줄에서 저주 문구를 띄운다.
# 진짜 저주 자리는 PokeBattle_Battle의 턴 종료 처리에 따로 있고 그쪽은 정상이다.
# 두 자리가 같은 리터럴을 쓰므로 번역표로는 원리상 분리할 수 없다 — 소스에서 가른다.
# 새 문자열은 본가 스페인어판 자구(공식 코퍼스 실측: "¡… ha sufrido los efectos de
# Otra Vez!" → 「… 앙코르를 받았다!」), 짝 번역은 23-script-texts.add.jsonl.
# 옛 문자열이 저주 쪽과 안 겹치는 근거: 인자가 다르다(여기는 opponent.pbThis, 저주는 i.pbThis).
EDITS += [
    ("PokeBattle_MoveEffects",
     '_INTL("¡{1} es víctima de una Maldición!",opponent.pbThis)',
     '_INTL("¡{1} ha sufrido los efectos de Otra Vez!",opponent.pbThis)'),
]

# Constants.rxdata 로드 실패 표면화(진단 전용, 동작 불변) — JoiPlay에서 이 로드가
# 조용히 삼켜져 뒤(246 RandomObjects)에서 NameError로 터지는 사슬(제보 목록의 JoiPlay
# 건). 실패 시 진짜 원인을 화면에 띄운다. 문구는 ASCII — JoiPlay는 한글 폰트가
# 깨지는 환경이라서다. 기능 수정은 원인 확정 전 금지(2026-08-04 사용자 결정).
EDITS += [
    ("PSystem_System",
     '  begin\r\n'
     '    consts=pbSafeLoad("Data/Constants.rxdata")\r\n'
     '    consts=[] if !consts\r\n'
     '  rescue\r\n'
     '    consts=[]\r\n'
     '  end',
     '  begin\r\n'
     '    consts=pbSafeLoad("Data/Constants.rxdata")\r\n'
     '    consts=[] if !consts\r\n'
     '  rescue\r\n'
     '    p "KR-PATCH DIAG: Constants.rxdata load failed - #{$!.class}: #{$!.message}"\r\n'
     '    consts=[]\r\n'
     '  end\r\n'
     '  p "KR-PATCH DIAG: Constants.rxdata empty - game constants missing (please report this screen)" if consts.length==0'),
]

# 요약 화면 성격 한 줄 — 명사(얌전)를 활용형(얌전한)으로. 성격명 자체는 성격
# 변경 목록 등에서 명사로 계속 쓰이므로 이 화면의 변수에만 25종 표를 얹는다.
# 짝인 템플릿 번역은 절23 「{1} 성격이다.」 (translate/ko 정본). 루비 1.8 문법.
_NATURE_ADJ = ("노력하는,외로움을 타는,용감한,고집스러운,개구쟁이,대담한,온순한,"
               "무사태평한,장난꾸러기,촐랑거리는,겁이 많은,성급한,성실한,명랑한,"
               "천진난만한,조심스러운,의젓한,냉정한,수줍음이 많은,덜렁거리는,"
               "차분한,얌전한,건방진,신중한,변덕스러운").split(",")
EDITS += [
    ("PScreen_Summary",
     "naturename=PBNatures.getName(pokemon.nature)",
     "naturename=([" + ",".join(f'"{a}"' for a in _NATURE_ADJ) + "]"
     "[pokemon.nature] || PBNatures.getName(pokemon.nature))"),
]

# 트레이너 메모 — 장소 줄의 개행을 지워 다음 만남 문구와 한 줄로 병합한다:
# 「1번도로」+「에서 Lv. 5일 때 발견됨.」. 만난 곳·부화한 곳이 같은 리터럴이라
# EDIT 하나가 2곳을 치환한다. 만남 문구(절23 번역)는 「에서 …」로 시작하고
# sprintf가 회색 접두를 이미 붙이므로 색 경계도 그대로 선다.
EDITS += [
    ("PScreen_Summary",
     'memo+=sprintf("<c3=F83820,E09890>%s\\n",mapname)',
     'memo+=sprintf("<c3=F83820,E09890>%s",mapname)'),
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
