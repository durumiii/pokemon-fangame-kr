# 기술 선택창의 기술 이름을 상대 타입 상성 배율로 색칠한다 (Ruby 1.8.7 / 3.1+ 공통).
# 출처: 디시 레쿠쟈 갤 228378 「상성턱받이 패치」의 Bui 섹션 — 우리 모드 형식으로 이식.
#
# FightMenuButtons·FightMenuDisplay를 alias 없이 재정의한다. 코어(PokeBattle_Scene)의
# 두 클래스는 한글패치가 손대지 않은 순정이라 덮어도 잃는 것이 없다(2026-08-09 실측).
# 재정의가 아니라 클래스 재오픈이라 여기 없는 메서드(생성자·dispose·속성 접근자)는
# 코어 것이 그대로 산다. 배틀 UI를 만지는 다른 모드가 생기면 로드 순서를 확인할 것.
class FightMenuButtons < BitmapSprite
  def update(index=0,moves=nil,megaButton=0,opponents=[])
    refresh(index,moves,megaButton,opponents)
  end

  def pbSingleTypeMod(moveType,defType)
    begin
      raw=PBTypes.getEffectiveness(moveType,defType)
      return raw/2.0
    rescue
      return 1.0
    end
  end

  # 타입은 「플레이어에게 보이는 모습」 기준 — 일루전(조로아크)이 서 있으면
  # 위장 종의 타입으로 계산한다. battler.type1/2를 그대로 읽으면 진짜 타입이 새서
  # 위장이 색으로 들통난다. 소크·변신 같은 타입 변화는 화면에 보이는 것이라 그대로 둔다.
  def pbTypeMultiplier(moveType,opponent)
    return 1.0 if !opponent || !opponent.pokemon
    seen=(opponent.effects[PBEffects::Illusion] rescue nil)
    t1=seen ? seen.type1 : opponent.type1
    t2=seen ? seen.type2 : opponent.type2
    mult=pbSingleTypeMod(moveType,t1)
    if t2 && t2!=t1
      mult*=pbSingleTypeMod(moveType,t2)
    end
    return mult
  end

  # 상대가 여럿(더블)이면 전원 배율이 일치할 때만 그 색을 쓰고, 갈리면 색을 내지
  # 않는다(1배 취급) — 어느 한쪽 기준의 색이 다른 쪽에 대한 오정보가 되는 것을 막는다.
  def pbAgreedMultiplier(moveType,opponents)
    return 1.0 if !opponents || opponents.length==0
    first=nil
    for op in opponents
      m=pbTypeMultiplier(moveType,op)
      first=m if first.nil?
      return 1.0 if m!=first
    end
    return first
  end

  def pbEffectivenessColor(mult)
    return nil if mult.nil?
    if mult==0
      return Color.new(0,0,0)                                   # 무효 - 검정
    elsif mult<1
      return (mult<=0.25) ? Color.new(255,0,0) : Color.new(255,140,0)  # 0.25배 빨강 / 0.5배 주황
    elsif mult==1
      return nil                                                # 1배 - 색 없음(기본색 유지)
    else
      return (mult>=4) ? Color.new(135,206,250) : Color.new(0,210,0)   # 4배 하늘색 / 2배 초록
    end
  end

  # 본가처럼 공격기에만 색을 낸다 — 변화기는 상성 배율이 뜻이 없어 기본색 그대로.
  def pbMoveNameColor(move,opponents)
    return PokeBattle_SceneConstants::MENUBASECOLOR if move.pbIsStatus?
    mult=pbAgreedMultiplier(move.type,opponents)
    color=pbEffectivenessColor(mult)
    return color || PokeBattle_SceneConstants::MENUBASECOLOR
  end

  def refresh(index,moves,megaButton,opponents=[])
    return if !moves
    self.bitmap.clear
    textpos=[]
    for i in 0...4
      next if i==index
      next if moves[i].id==0
      x=((i%2)==0) ? 4 : 192
      y=((i/2)==0) ? 6 : 48
      y+=UPPERGAP
      self.bitmap.blt(x,y,@buttonbitmap.bitmap,Rect.new(0,moves[i].type*46,192,46))
      namecolor=pbMoveNameColor(moves[i],opponents)
      textpos.push([_INTL("{1}",moves[i].name),x+96,y+8,2,
         namecolor,PokeBattle_SceneConstants::MENUSHADOWCOLOR])
    end
    ppcolors=[
       PokeBattle_SceneConstants::PPTEXTBASECOLOR,PokeBattle_SceneConstants::PPTEXTSHADOWCOLOR,
       PokeBattle_SceneConstants::PPTEXTBASECOLOR,PokeBattle_SceneConstants::PPTEXTSHADOWCOLOR,
       PokeBattle_SceneConstants::PPTEXTBASECOLORYELLOW,PokeBattle_SceneConstants::PPTEXTSHADOWCOLORYELLOW,
       PokeBattle_SceneConstants::PPTEXTBASECOLORORANGE,PokeBattle_SceneConstants::PPTEXTSHADOWCOLORORANGE,
       PokeBattle_SceneConstants::PPTEXTBASECOLORRED,PokeBattle_SceneConstants::PPTEXTSHADOWCOLORRED
    ]
    for i in 0...4
      next if i!=index
      next if moves[i].id==0
      x=((i%2)==0) ? 4 : 192
      y=((i/2)==0) ? 6 : 48
      y+=UPPERGAP
      self.bitmap.blt(x,y,@buttonbitmap.bitmap,Rect.new(192,moves[i].type*46,192,46))
      self.bitmap.blt(416,20+UPPERGAP,@typebitmap.bitmap,Rect.new(0,moves[i].type*28,64,28))
      namecolor=pbMoveNameColor(moves[i],opponents)
      textpos.push([_INTL("{1}",moves[i].name),x+96,y+8,2,
         namecolor,PokeBattle_SceneConstants::MENUSHADOWCOLOR])
      if moves[i].totalpp>0
        ppfraction=(4.0*moves[i].pp/moves[i].totalpp).ceil
        textpos.push([_INTL("PP: {1}/{2}",moves[i].pp,moves[i].totalpp),
           448,50+UPPERGAP,2,ppcolors[(4-ppfraction)*2],ppcolors[(4-ppfraction)*2+1]])
      end
    end
    pbDrawTextPositions(self.bitmap,textpos)
    if megaButton>0
      self.bitmap.blt(146,0,@megaevobitmap.bitmap,Rect.new(0,(megaButton-1)*46,96,46))
    end
  end
end


class FightMenuDisplay
  def refresh
    return if !@battler
    commands=[]
    for i in 0...4
      break if @battler.moves[i].id==0
      commands.push(@battler.moves[i].name)
    end
    @window.commands=commands
    selmove=@battler.moves[@index]
    movetype=PBTypes.getName(selmove.type)
    if selmove.totalpp==0
      @info.text=_ISPRINTF("{1:s}PP: ---<br>TIPO/{2:s}",@ctag,movetype)
    else
      @info.text=_ISPRINTF("{1:s}PP: {2: 2d}/{3: 2d}<br>TIPO/{4:s}",
         @ctag,selmove.pp,selmove.totalpp,movetype)
    end
    @buttons.refresh(self.index,@battler ? @battler.moves : nil,@megaButton,pbGetOpponents) if @buttons
  end

  def update
    @info.update
    @window.update
    @display.update if @display
    if @buttons
      moves=@battler ? @battler.moves : nil
      @buttons.update(self.index,moves,@megaButton,pbGetOpponents)
    end
  end

  def pbGetOpponents
    return [] if !@battler
    battle=@battler.battle rescue nil
    return [] if !battle
    return battle.battlers.select{|b| b && !b.isFainted? && @battler.pbIsOpposing?(b.index)}
  end
end