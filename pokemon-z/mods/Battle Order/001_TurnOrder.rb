# Battle Order — 배틀 행동 순서 (Pokemon Z v2.18 · Essentials v16 · 루비 1.8.7)
#
# 이 게임은 공격 페이즈가 시작될 때 행동 순서를 한 번 계산하고 그 라운드 내내 그
# 배열만 쓴다. 그래서 턴 도중에 생긴 변화 — 방금 걸린 마비, 교체로 들어온 포켓몬의
# 등장 특성이 깐 트릭룸·날씨 — 가 그 턴에 하나도 반영되지 않는다. 8세대 이후 본가는
# 행동이 하나 끝날 때마다 남은 순서를 다시 정렬한다. 여기서 그 방식으로 맞춘다.
#
# 원본 `pbPriority`·`pbAttackPhase`를 그대로 떠 와서 다음만 바꿨다.
#   · `10.times` 루프 머리에서 `bo_resortPriority`로 남은 순서를 다시 정렬
#   · 선제의발톱·구애열매 판정은 라운드에 한 번만 굴리고 재계산은 그 결과를 재사용
#   · 선제의발톱 메시지를 순서 계산 시점이 아니라 그 포켓몬이 움직이기 직전에 표시
#     (원본에도 `# TODO: Quick Claw message`로 남아 있던 자리다)
#   · 재계산 중에는 `pbSpeed`의 등장 턴 전용 부수효과가 다시 돌지 않게 막음
#
# 우선도 브래킷은 손대지 않는다 — 본가도 브래킷은 그대로 두고 같은 브래킷 안의
# 스피드 순서만 다시 매긴다.
#
# 무엇을 왜 이렇게 했는지는 이 폴더의 AGENTS.md가 정본이다.

class PokeBattle_Battle
  # 재계산 중임을 알린다. Battler#pbSpeed가 이 값을 보고 등장 턴 전용 부수효과를 건넌다.
  attr_accessor :bo_quiet_speed

  # 남은 포켓몬의 행동 순서를 다시 정렬한다.
  def bo_resortPriority
    return if !@priority || @priority.length==0
    return if !@bo_quickclaw   # 이 라운드의 첫 계산이 아직 안 돌았다
    @bo_quiet_speed=true
    begin
      @usepriority=false
      pbPriority(true,false,true)
      @usepriority=true
    ensure
      @bo_quiet_speed=false
    end
  end

  # 선제의발톱·구애열매 메시지를 그 포켓몬이 실제로 움직이기 직전에 보여 준다.
  def bo_showQuickClaw(battler)
    return if !@bo_qcmsg
    msg=@bo_qcmsg[battler.index]
    return if !msg
    @bo_qcmsg[battler.index]=nil
    return if @choices[battler.index][0]!=1   # 기술을 쓰는 행동일 때만
    pbCommonAnimation("UseItem",battler,nil)
    pbDisplayBrief(msg)
  end

  def pbPriority(ignorequickclaw=false,log=false,reuse=false)
    return @priority if @usepriority # use stored priority if round isn't over yet
    speeds=[]
    quickclaw=[]; lagging=[]
    minpri=0; maxpri=0
    temp=[]
    # [Battle Order] 재계산일 때는 이 라운드에 이미 굴린 선제의발톱·구애열매 판정을
    # 그대로 쓰고 스피드만 새로 읽는다.
    if reuse && @bo_quickclaw && @bo_lagging
      quickclaw=@bo_quickclaw
      lagging=@bo_lagging
      for i in 0...4
        speeds[i]=@battlers[i].pbSpeed
      end
      return bo_sortPriority(speeds,quickclaw,lagging,log)
    end
    @bo_qcmsg=[] if !ignorequickclaw
    # Calcula la velocidad de cada Pokémon
    for i in 0...4
      speeds[i]=@battlers[i].pbSpeed
      quickclaw[i]=false
      lagging[i]=false
      if !ignorequickclaw && @choices[i][0]==1 # Chose to use a move
        if !quickclaw[i] && @battlers[i].hasWorkingItem(:CUSTAPBERRY) &&
           !@battlers[i].pbOpposing1.hasWorkingAbility(:UNNERVE) &&
           !@battlers[i].pbOpposing2.hasWorkingAbility(:UNNERVE)
          if (@battlers[i].hasWorkingAbility(:GLUTTONY) && @battlers[i].hp<=(@battlers[i].totalhp/2).floor) ||
             @battlers[i].hp<=(@battlers[i].totalhp/4).floor
            quickclaw[i]=true
            @bo_qcmsg[i]=_INTL("¡{1} se mueve primero gracias a la {2}!",
               @battlers[i].pbThis,PBItems.getName(@battlers[i].item))
            @battlers[i].pbConsumeItem
          end
        end
        if !quickclaw[i] && @battlers[i].hasWorkingItem(:QUICKCLAW)
          if pbRandom(10)<2
            quickclaw[i]=true
            @bo_qcmsg[i]=_INTL("¡{1} se mueve primero gracias a la {2}!",
               @battlers[i].pbThis,PBItems.getName(@battlers[i].item))
          end
        end
        if !quickclaw[i] &&
           (@battlers[i].hasWorkingAbility(:STALL) ||
           @battlers[i].hasWorkingItem(:LAGGINGTAIL) ||
           @battlers[i].hasWorkingItem(:FULLINCENSE))
          lagging[i]=true
        end
      end
    end
    if !ignorequickclaw
      @bo_quickclaw=quickclaw
      @bo_lagging=lagging
    end
    return bo_sortPriority(speeds,quickclaw,lagging,log)
  end

  # 원본 pbPriority의 뒷부분 그대로 — 우선도 브래킷을 가르고 같은 브래킷 안을
  # 스피드로 정렬한다. 재계산이 이 자리만 다시 쓰도록 떼어 놓았다.
  def bo_sortPriority(speeds,quickclaw,lagging,log)
    @priority.clear
    priorities=[]
    minpri=0; maxpri=0
    temp=[]
    # Calculate each Pokémon's priority bracket, and get the min/max priorities
    for i in 0...4
      # Assume that doing something other than using a move is priority 0
      pri=0
      if @choices[i][0]==1 # Chose to use a move
        pri=@choices[i][2].priority
        pri+=1 if @field.effects[PBEffects::GrassyTerrain]>0 && 
            @choices[i][2].function == 0x211
        pri+=1 if @field.effects[PBEffects::MistyTerrain]>0 && 
            @choices[i][2].function == 0x208
        pri+=1 if @battlers[i].hasWorkingAbility(:PRANKSTER) &&
                  @choices[i][2].pbIsStatus?
        pri+=1 if @battlers[i].hasWorkingAbility(:GALEWINGS) &&
                  isConst?(@choices[i][2].type,PBTypes,:FLYING)
        pri+=3 if @battlers[i].hasWorkingAbility(:TRIAGE) &&
                  @choices[i][2].isHealingMove? &&
                  !isConst?(@choices[i][2].id,PBMoves,:AQUARING) &&
                  !isConst?(@choices[i][2].id,PBMoves,:GRASSYTERRAIN) &&
                  !isConst?(@choices[i][2].id,PBMoves,:INGRAIN) &&
                  !isConst?(@choices[i][2].id,PBMoves,:LEECHSEED) &&
                  !isConst?(@choices[i][2].id,PBMoves,:PAINSPLIT) &&
                  !isConst?(@choices[i][2].id,PBMoves,:PRESENT)
      end
      priorities[i]=pri
      if i==0
        minpri=pri
        maxpri=pri
      else
        minpri=pri if minpri>pri
        maxpri=pri if maxpri<pri
      end
    end
    # Find and order all moves with the same priority
    curpri=maxpri
    loop do
      temp.clear
      for j in 0...4
        temp.push(j) if priorities[j]==curpri
      end
      # Sort by speed
      if temp.length==1
        @priority[@priority.length]=@battlers[temp[0]]
      elsif temp.length>1
        n=temp.length
        for m in 0...temp.length-1
          for i in 1...temp.length
            # For each pair of battlers, rank the second compared to the first
            # -1 means rank higher, 0 means rank equal, 1 means rank lower
            cmp=0
            if quickclaw[temp[i]]
              cmp=-1
              if quickclaw[temp[i-1]]
                if speeds[temp[i]]==speeds[temp[i-1]]
                  cmp=0
                else
                  cmp=(speeds[temp[i]]>speeds[temp[i-1]]) ? -1 : 1
                end
              end
            elsif quickclaw[temp[i-1]]
              cmp=1
            elsif lagging[temp[i]]
              cmp=1
              if lagging[temp[i-1]]
                if speeds[temp[i]]==speeds[temp[i-1]]
                  cmp=0
                else
                  cmp=(speeds[temp[i]]>speeds[temp[i-1]]) ? 1 : -1
                end
              end
            elsif lagging[temp[i-1]]
              cmp=-1
            elsif speeds[temp[i]]!=speeds[temp[i-1]]
              if @field.effects[PBEffects::TrickRoom]>0
                cmp=(speeds[temp[i]]>speeds[temp[i-1]]) ? 1 : -1
              else
                cmp=(speeds[temp[i]]>speeds[temp[i-1]]) ? -1 : 1
              end
            end
            if cmp<0 || # Swap the pair according to the second battler's rank
               (cmp==0 && pbRandom(2)==0)
              swaptmp=temp[i]
              temp[i]=temp[i-1]
              temp[i-1]=swaptmp
            end
          end
        end
        # Battlers in this bracket are properly sorted, so add them to @priority
        for i in temp
          @priority[@priority.length]=@battlers[i]
        end
      end
      curpri-=1
      break if curpri<minpri
    end
    # Write the priority order to the debug log
    if log
      d="[Priority] "; comma=false
      for i in 0...4
        if @priority[i] && !@priority[i].isFainted?
          d+=", " if comma
          d+="#{@priority[i].pbThis(comma)} (#{@priority[i].index})"; comma=true
        end
      end
      PBDebug.log(d)
    end
    @usepriority=true
    return @priority
  end

  def pbAttackPhase
    @scene.pbBeginAttackPhase
    for i in 0...4
      @successStates[i].clear
      if @choices[i][0]!=1 && @choices[i][0]!=2
        @battlers[i].effects[PBEffects::DestinyBond]=false
        @battlers[i].effects[PBEffects::Grudge]=false
      end
      @battlers[i].turncount+=1 if !@battlers[i].isFainted?
      @battlers[i].effects[PBEffects::Rage]=false if !pbChoseMove?(i,:RAGE)
    end
    # Calculate priority at this time
    @usepriority=false
    priority=pbPriority(false,true)
    # Mega Evolution
    megaevolved=[]
    for i in priority
      if @choices[i.index][0]==1 && !i.effects[PBEffects::SkipTurn]
        side=(pbIsOpposing?(i.index)) ? 1 : 0
        owner=pbGetOwnerIndex(i.index)
        if @megaEvolution[side][owner]==i.index
          pbMegaEvolve(i.index)
          megaevolved.push(i.index)
        end
      end
    end
    if megaevolved.length>0
      for i in priority
        i.pbAbilitiesOnSwitchIn(true) if megaevolved.include?(i.index)
      end
    end
    # Call at Pokémon
for i in priority
      if @choices[i.index][0]==4 && !i.effects[PBEffects::SkipTurn]
        if $PokemonBag.pbHasItem?(:ULTRABALLCASERA)
          pokeBall=getConst(PBItems,:ULTRABALLCASERA)
          $PokemonBag.pbDeleteItem(:ULTRABALLCASERA,1)
        elsif $PokemonBag.pbHasItem?(:SUPERBALLCASERA)
          pokeBall=getConst(PBItems,:SUPERBALLCASERA)
          $PokemonBag.pbDeleteItem(:SUPERBALLCASERA,1)
        elsif $PokemonBag.pbHasItem?(:POKEBALLCASERA)
          pokeBall=getConst(PBItems,:POKEBALLCASERA)
          $PokemonBag.pbDeleteItem(:POKEBALLCASERA,1)          
        elsif $PokemonBag.pbHasItem?(:ULTRABALL)
          pokeBall=getConst(PBItems,:ULTRABALL)
          $PokemonBag.pbDeleteItem(:ULTRABALL,1)
        elsif $PokemonBag.pbHasItem?(:GREATBALL)
          pokeBall=getConst(PBItems,:GREATBALL)
          $PokemonBag.pbDeleteItem(:GREATBALL,1)
        elsif $PokemonBag.pbHasItem?(:POKEBALL)
          pokeBall=getConst(PBItems,:POKEBALL)
          $PokemonBag.pbDeleteItem(:POKEBALL,1)          
        end  
          if pokeBall
            pbThrowPokeBall(1,pokeBall)
          end   
      end
    end
    # Switch out Pokémon
    @switching=true
    switched=[]
    for i in priority
      if @choices[i.index][0]==2 && !i.effects[PBEffects::SkipTurn]
        index=@choices[i.index][1] # party position of Pokémon to switch to
        newpokename=index
        if isConst?(pbParty(i.index)[index].ability,PBAbilities,:ILLUSION)
          newpokename=pbGetLastPokeInTeam(i.index)
        end
        self.lastMoveUser=i.index
        if !pbOwnedByPlayer?(i.index)
          owner=pbGetOwner(i.index)
          pbDisplayBrief(_INTL("¡{1} saca a {2}!",owner.fullname,i.name))
          PBDebug.log("[Sacar Pokémon] Oponente sacó #{i.pbThis(true)}")
        else
          pbDisplayBrief(_INTL("¡{1}, cambio!\r\n¡Vuelve aquí!",i.name))
          PBDebug.log("[Sacar Pokémon] Jugador sacó #{i.pbThis(true)}")
        end
        for j in priority
          next if !i.pbIsOpposing?(j.index)
          # if Pursuit and this target ("i") was chosen
          if pbChoseMoveFunctionCode?(j.index,0x88) && # Pursuit
             !j.hasMovedThisRound?
            if j.status!=PBStatuses::SLEEP && j.status!=PBStatuses::FROZEN &&
               !j.effects[PBEffects::SkyDrop] &&
               (!j.hasWorkingAbility(:TRUANT) || !j.effects[PBEffects::Truant])
              @choices[j.index][3]=i.index # Make sure to target the switching Pokémon
              j.pbUseMove(@choices[j.index]) # This calls pbGainEXP as appropriate
              j.effects[PBEffects::Pursuit]=true
              @switching=false
              return if @decision>0
            end
          end
          break if i.isFainted?
        end
        if !pbRecallAndReplace(i.index,index,newpokename)
          # If a forced switch somehow occurs here in single battles
          # the attack phase now ends
          if !@doublebattle
            @switching=false
            return
          end
        else
          switched.push(i.index)
        end
      end
    end
    if switched.length>0
      for i in priority
        i.pbAbilitiesOnSwitchIn(true) if switched.include?(i.index)
      end
    end
    @switching=false
    # Uso de objetos
    for i in priority
      if @choices[i.index][0]==3 && !i.effects[PBEffects::SkipTurn]
        if pbIsOpposing?(i.index)
          # Opponent use item
          pbEnemyUseItem(@choices[i.index][1],i)
        else
          # Player use item
          item=@choices[i.index][1]
          if item>0
            usetype=$ItemData[item][ITEMBATTLEUSE]
            if usetype==1 || usetype==3
              if @choices[i.index][2]>=0
                pbUseItemOnPokemon(item,@choices[i.index][2],i,@scene)
              end
            elsif usetype==2 || usetype==4
              if !ItemHandlers.hasUseInBattle(item) # Poké Ball/Poké Doll used already
                pbUseItemOnBattler(item,@choices[i.index][2],i,@scene)
              end
            end
          end
        end
      end
    end
    # Uso de ataques
    for i in priority
      next if i.effects[PBEffects::SkipTurn]
      if pbChoseMoveFunctionCode?(i.index,0x115) # Focus Punch  /  Puño Certero
        pbCommonAnimation("FocusPunch",i,nil)
        pbDisplay(_INTL("¡{1} está reforzando su concentración!",i.pbThis))
      end
    end
    10.times do
      # [Battle Order] 남은 순서를 다시 정렬한다(8세대 이후 본가 방식). 교체로 들어온
      # 포켓몬의 등장 특성(트릭룸·날씨)과 방금 걸린 마비가 여기서 반영된다.
      bo_resortPriority
      # Forced to go next
      advance=false
      for i in priority
        next if !i.effects[PBEffects::MoveNext]
        next if i.hasMovedThisRound? || i.effects[PBEffects::SkipTurn]
        bo_showQuickClaw(i)
        advance=i.pbProcessTurn(@choices[i.index])
        break if advance
      end
      return if @decision>0
      next if advance
      # Regular priority order
      for i in priority
        next if i.effects[PBEffects::Quash]
        next if i.hasMovedThisRound? || i.effects[PBEffects::SkipTurn]
        bo_showQuickClaw(i)
        advance=i.pbProcessTurn(@choices[i.index])
        break if advance
      end
      return if @decision>0
      next if advance
      # Quashed
      for i in priority
        next if !i.effects[PBEffects::Quash]
        next if i.hasMovedThisRound? || i.effects[PBEffects::SkipTurn]
        bo_showQuickClaw(i)
        advance=i.pbProcessTurn(@choices[i.index])
        break if advance
      end
      return if @decision>0
      next if advance
      # Check for all done
      for i in priority
        advance=true if @choices[i.index][0]==1 && !i.hasMovedThisRound? &&
                        !i.effects[PBEffects::SkipTurn]
        break if advance
      end
      next if advance
      break
    end
    pbWait(20)
  end
end

class PokeBattle_Battler
  # `pbSpeed`에는 값을 읽는 일 말고 등장 턴에만 도는 부수효과가 섞여 있다(커스텀 특성
  # `TINTINEO`가 아군 상태이상을 치료하고 메시지를 띄운다). 순서를 여러 번 다시
  # 계산하면 그것도 여러 번 돈다. 재계산 동안만 등장 턴 판정(`turncount==0`)을 피해
  # 값만 읽는다. 라운드 첫 계산은 원본 그대로 두므로 게임 동작은 안 바뀐다.
  # ponytail: turncount를 잠깐 갈아 끼우는 우회다. 부수효과를 pbSpeed 밖으로 빼내는
  # 것이 옳은 수술이지만 그건 이 모드 범위 밖이다(Z-42).
  alias bo_pbSpeed pbSpeed
  def pbSpeed
    # 사파리존은 PokeBattle_Battle을 안 물려받는 딴 클래스다 — 물어보고 쓴다.
    return bo_pbSpeed if !@battle.respond_to?(:bo_quiet_speed)
    return bo_pbSpeed if !@battle.bo_quiet_speed
    saved=@turncount
    @turncount=2 if saved==0
    begin
      return bo_pbSpeed
    ensure
      @turncount=saved
    end
  end
end
