# Auto Box — 포켓몬을 잡았을 때 파티가 꽉 찼으면 박스로 바로 보낸다 (Z-50 ②)
#
# 원본 `PokeBattle_BattleCommon#pbStorePokemon`(절 PokeBattle_Battle 13-56줄)은 파티가
# 여섯 마리면 「파티에 넣을까?」를 묻고, 넣겠다고 하면 교체할 포켓몬을 고르게 한다.
# 옵션이 「자동 보관」이면 그 물음 블록만 건너뛴다 — 그 아래 `@peer.pbStorePokemon`이
# 알아서 박스로 보내므로 다른 자리는 손댈 것이 없다(절 PokeBattle_BattlePeer 28-43줄).
#
# 별명 물음(원본 15줄)은 이 블록보다 **앞**이라 어느 갈래로 가든 그대로 뜬다. 옵션
# 「별명 물음」이 「끄기」면 그 물음을 통째로 건너뛰고 원래 이름 그대로 간다(유지자 판정
# 2026-08-21 — 8·9세대 방식. 확인을 연타하다 이름짓기로 들어가 버린다는 제보에서 나왔고,
# 커서를 뒤집는 길은 선택지 차례가 「아니요·예」로 보이는 대가가 있어 접었다).
# 필드 경로(알 부화·선물)의 별명 물음은 다른 함수라 이 파일 꼬리에서 따로 잡는다.
#
# 문구 리터럴은 원본 스페인어 그대로다 — 번역표가 그 원문을 열쇠로 등재하고 있어
# 자구가 바뀌면 조회가 깨진다.
#
# 벌레잡기 대회는 제 클래스에서 pbStorePokemon을 따로 정의하므로 여기 안 걸린다.
# 사파리존은 같은 모듈을 쓰므로 함께 걸린다.
#
# 값은 $PokemonSystem에 실어 세이브에 남긴다. 옛 세이브에는 그 인스턴스 변수가 없어
# nil이 오므로 게터가 기본값 0(자동 보관)을 돌려준다 — 원작의 다른 게터들과 같은 꼴이다
# (절 PScreen_Options 384-421줄).

class PokemonSystem
  attr_accessor :qol_autobox

  # 0 = 자동 보관(기본) · 1 = 물어보기
  def qol_autobox
    return (!@qol_autobox) ? 0 : @qol_autobox
  end

  attr_accessor :qol_nickname

  # 0 = 켜기(기본) · 1 = 끄기
  def qol_nickname
    return (!@qol_nickname) ? 0 : @qol_nickname
  end
end

# 별명을 물을 차례인가. 옛 세이브($PokemonSystem이 아직 없는 자리 포함)에서는 켜기다.
def qol_pbAskNickname?
  return !($PokemonSystem && $PokemonSystem.qol_nickname==1)
end

module PokeBattle_BattleCommon
  def pbStorePokemon(pokemon)
    if !(pokemon.isShadow? rescue false) && qol_pbAskNickname?
      if pbDisplayConfirm(_INTL("¿Quieres ponerle un apodo a {1}?",pokemon.name))
        species=PBSpecies.getName(pokemon.species)
        nickname=@scene.pbNameEntry(_INTL("Apodo de {1}",species),pokemon)
        pokemon.name=nickname if nickname!=""
      end
    end
    
    # --- 자동 보관 분기 (옵션 「파티가 꽉 찼을 때」) ---
    # 자동 보관이면 이 물음을 통째로 건너뛴다 — 아래 @peer.pbStorePokemon이 알아서
    # 박스로 보낸다. 「물어보기」면 원본 그대로다. 파티에 자리가 있으면 원본도 안 묻는다.
    qolautobox=($PokemonSystem && $PokemonSystem.qol_autobox==0)
    if $Trainer.party.length>5 && !qolautobox
      if Kernel.pbConfirmMessage(_INTL("¿Quieres añadir a {1} a tu equipo?",pokemon.name))
        pbDisplayPaused(_INTL("¿Por cuál lo quieres remplazar?"))
        pbChoosePokemon(1,2,proc {|poke| !poke.isEgg? && !(poke.isShadow? rescue false)})
        if $game_variables[1]!=-1
          pbSet(3,$Trainer.party[pbGet(1)])
          $Trainer.party[pbGet(1)]=pokemon
          pbDisplayPaused(_INTL("{1} fue añadido a tu equipo.",pokemon.name))
          pokemon=pbGet(3)
        end
      end
    end
    
    oldcurbox=@peer.pbCurrentBox()
    storedbox=@peer.pbStorePokemon(self.pbPlayer,pokemon)
    creator=@peer.pbGetStorageCreator()
    return if storedbox<0
    curboxname=@peer.pbBoxName(oldcurbox)
    boxname=@peer.pbBoxName(storedbox)
    if storedbox!=oldcurbox
      if creator
        pbDisplayPaused(_INTL("La caja \"{1}\" del Rancho de {2} está llena.",curboxname,creator))
      else
        pbDisplayPaused(_INTL("La caja \"{1}\" del Rancho está llena.",curboxname))
      end
      pbDisplayPaused(_INTL("{1} fue transferido a la caja \"{2}\".",pokemon.name,boxname))
    else
      if creator
        pbDisplayPaused(_INTL("{1} fue transferido al Rancho.",pokemon.name,creator))
      else
        pbDisplayPaused(_INTL("{1} fue transferido al Rancho.",pokemon.name))
      end
      pbDisplayPaused(_INTL("Fue guardado en la caja \"{1}\".",boxname))
    end
  end
end

# 옵션 화면에 항목 하나를 세운다. 원작이 그 용도로 비워 둔 훅(pbAddOnOptions)에 얹으므로
# 큰 목록을 베낄 것이 없다.
#
# ⚠ 설명 문구를 여기서 직접 못 쓴다 — 원작 pbOptions의 `case idx`가 항목 번호로 설명을
# 내는데 else가 없고, 끝에 붙인 우리 항목의 번호(난이도 스위치가 꺼진 보통 판에서는 10)는
# 원래 「Salir」 줄 몫이라 빈 문자열이 박힌다. 그 case는 pbUpdate **뒤**에 도므로
# pbUpdate에서 써 봐야 곧바로 덮인다. 그래서 case보다 뒤에 도는 자리가 하나 필요한데,
# 그 루프에서 case 다음으로 불리는 것이 `@sprites["option"].mustUpdateOptions`다
# (절 PScreen_Options 763줄 — 이 값을 읽는 자리는 게임 전체에 그 한 곳뿐이다).
# 읽힐 때 우리 설명을 써 넣는다. 항목 번호는 어디에도 박지 않는다 — 다른 모드가 항목을
# 더해도 이름으로 찾으므로 어긋나지 않는다.
class PokemonOptionScene
  QOL_AUTOBOX_NAME = "파티가 꽉 찼을 때"
  QOL_AUTOBOX_DESC = "포켓몬을 잡았을 때 파티가 꽉 차 있으면 어떻게 할지 정한다."
  QOL_NICKNAME_NAME = "별명 물음"
  QOL_NICKNAME_DESC = "포켓몬을 잡거나 알을 깼을 때 별명을 붙일지 물어본다."

  # 이름 → 설명. 우리 항목인지도 이 표로 가린다(항목 번호를 어디에도 안 박는다).
  QOL_DESCS = {
    QOL_AUTOBOX_NAME  => QOL_AUTOBOX_DESC,
    QOL_NICKNAME_NAME => QOL_NICKNAME_DESC
  }

  alias qol_autobox_pbAddOnOptions pbAddOnOptions
  def pbAddOnOptions(options)
    options=qol_autobox_pbAddOnOptions(options)
    options.push(EnumOption.new(QOL_AUTOBOX_NAME,["자동 보관","물어보기"],
       proc { $PokemonSystem.qol_autobox },
       proc {|value| $PokemonSystem.qol_autobox=value }
    ))
    options.push(EnumOption.new(QOL_NICKNAME_NAME,["켜기","끄기"],
       proc { $PokemonSystem.qol_nickname },
       proc {|value| $PokemonSystem.qol_nickname=value }
    ))
    return options
  end

  # 화면이 서 있는 동안 옵션 창에 텍스트 상자를 쥐여 준다(창은 pbAddOnOptions 뒤에
  # 만들어지므로 그때는 아직 없다). 페이드인처럼 pbOptions 루프 밖에서 도는 프레임은
  # 여기서 쓴 것이 그대로 남는다.
  alias qol_autobox_pbUpdate pbUpdate
  def pbUpdate
    qol_autobox_pbUpdate
    return if !@sprites
    win=@sprites["option"]
    box=@sprites["textbox"]
    return if !win || !box || !win.respond_to?("qol_autobox_textbox=")
    win.qol_autobox_textbox=box
    win.qol_autobox_showDesc
  end
end

class Window_PokemonOption
  attr_writer :qol_autobox_textbox

  def qol_autobox_showDesc
    return if !@qol_autobox_textbox
    return if self.index<0 || self.index>=@options.length
    desc=PokemonOptionScene::QOL_DESCS[@options[self.index].name]
    return if !desc
    @qol_autobox_textbox.text=desc
  end

  # pbOptions 루프에서 `case idx` 바로 다음에 불린다 — 우리 설명을 그 뒤에 써 넣는 자리다.
  alias qol_autobox_mustUpdateOptions mustUpdateOptions
  def mustUpdateOptions
    qol_autobox_showDesc
    return qol_autobox_mustUpdateOptions
  end
end

# ── 필드 경로의 별명 물음 ────────────────────────────────────────────────────
# 전투에서 잡은 포켓몬 말고, 알을 깨거나 선물을 받을 때는 다른 함수가 묻는다
# (절 `PSystem_Utilities NUEVO` 1699줄 `pbNickname` — 문구도 apodo가 아니라 mote다).
# 「별명 물음」이라는 이름의 설정이 전투에만 먹으면 알을 깼을 때 그대로 물어 이상하므로
# 같은 값으로 여기도 잡는다. 끄기면 묻지 않고 원래 이름을 그대로 둔다.
#
# 전수 확인 — pbNickname을 부르는 자리는 스크립트 285절 통틀어 pbNicknameAndStore
# (같은 절 1758줄) 하나뿐이고, 맵·공통 이벤트의 스크립트 명령에도 없다. 별명 물음 말고
# 다른 용도로 불리는 자리는 없다.
#
# 원본이 최상위 def라 Object의 비공개 메서드다 — 여기서도 최상위에서 별칭을 걸어
# 그 성질을 그대로 둔다.
alias qol_nickname_pbNickname pbNickname
def pbNickname(pokemon)
  return if !qol_pbAskNickname?
  return qol_nickname_pbNickname(pokemon)
end

# ── 마지막 그물 — 박스가 꽉 차 저장에 실패했을 때 ────────────────────────────
# 원작 `PokeBattle_RealBattlePeer#pbStorePokemon`(절 PokeBattle_BattlePeer 37줄)이
# 실패를 알리려고 `pbDisplayPaused`를 부르는데 **그 클래스에 그 메서드가 없다** —
# 닿으면 NoMethodError로 죽는다(구판 루비 실물 확인).
#
# 메서드를 통째로 다시 정의하는 대신 **없는 메서드 하나만 채운다** — 고칠 것이 호출
# 대상뿐이라 이쪽이 훨씬 작고, 원작 몸통이 판올림으로 달라져도 그대로 산다.
class PokeBattle_RealBattlePeer
  def pbDisplayPaused(msg)
    Kernel.pbMessage(msg)
  end
end
