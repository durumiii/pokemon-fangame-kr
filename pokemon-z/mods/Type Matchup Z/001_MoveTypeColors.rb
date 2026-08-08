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

  def pbTypeMultiplier(moveType,opponent)
    return 1.0 if !opponent || !opponent.pokemon
    mult=pbSingleTypeMod(moveType,opponent.type1)
    if opponent.type2 && opponent.type2!=opponent.type1
      mult*=pbSingleTypeMod(moveType,opponent.type2)
    end
    return mult
  end

  # 상대가 여러 명이면 "가장 낮은 배율"(더 조심해야 하는 쪽) 기준으로 색 결정
  def pbWorstMultiplier(moveType,opponents)
    return 1.0 if !opponents || opponents.length==0
    return opponents.map{|op| pbTypeMultiplier(moveType,op)}.min
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

  def pbMoveNameColor(moveType,opponents)
    mult=pbWorstMultiplier(moveType,opponents)
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
      namecolor=pbMoveNameColor(moves[i].type,opponents)
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
      namecolor=pbMoveNameColor(moves[i].type,opponents)
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