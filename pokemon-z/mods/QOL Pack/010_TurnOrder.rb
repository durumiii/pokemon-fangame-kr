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
#   · `pbSpeed`는 등장 턴 전용 부수효과를 아예 돌리지 않게 막고, 그 부수효과는
#     등장 특성이 실제로 발동하는 `pbAbilitiesOnSwitchIn`으로 옮겼다(Z-42)
#   · 볼 단축키가 마지막에 쓴 볼을 먼저 낸다(Z-50 ①, 기억하는 자리는 070_BallShortcut.rb)
#
# 우선도 브래킷은 손대지 않는다 — 본가도 브래킷은 그대로 두고 같은 브래킷 안의
# 스피드 순서만 다시 매긴다.
#
# 무엇을 왜 이렇게 했는지는 이 폴더의 AGENTS.md가 정본이다.

class PokeBattle_Battle
  # 남은 포켓몬의 행동 순서를 다시 정렬한다.
  def bo_resortPriority
    return if !@priority || @priority.length==0
    return if !@bo_quickclaw   # 이 라운드의 첫 계산이 아직 안 돌았다
    @usepriority=false
    pbPriority(true,false,true)
    @usepriority=true
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
        # Z-76 — 박스 만석 가드. 전투 가방에서 볼을 고르는 길은 원작이 이미 막지만
        # (절 PItem_ItemEffects 2516줄), 볼 단축키는 가방을 안 거치고 곧바로 여기로 온다.
        # 가드가 없으면 절 PokeBattle_BattlePeer 37줄의 죽은 호출에 닿아 NoMethodError다.
        # 볼을 가방에서 빼기 **전에** 검사해서, 만석이면 안내만 띄우고 그 포켓몬의 행동을 넘긴다.
        # 문구는 가방 경로와 같은 리터럴이다 — 번역표가 그 원문을 열쇠로 등재하고 있다.
        if pbPlayer.party.length>=6 && $PokemonStorage && $PokemonStorage.full?
          pbDisplay(_INTL("¡No hay espacio en la PC!"))
          next
        end
        # Z-50 ① — 마지막으로 전투 가방에서 고른 볼을 먼저 낸다.
        # 그 볼을 기억하는 자리는 070_BallShortcut.rb다.
        # pokeBall을 반복마다 비운다 — 원본은 앞 포켓몬의 값이 남았다.
        pokeBall=nil
        if $lastUsedBall && $lastUsedBall>0 && $PokemonBag.pbHasItem?($lastUsedBall)
          pokeBall=$lastUsedBall
          $PokemonBag.pbDeleteItem($lastUsedBall,1)
        elsif $PokemonBag.pbHasItem?(:ULTRABALLCASERA)
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
  # Z-42 — `pbSpeed`는 값을 읽는 함수인데 원본은 그 안에서 등장 턴(`turncount==0`)에만
  # 도는 특성 둘을 처리한다. `TINTINEO`는 아군·파티 전원의 상태이상을 치료하며 멈추는
  # 문구를 띄우고, `ACOMETIDA`는 문구를 띄운다. 한 번 돌았다는 표시가 없어 `pbSpeed`가
  # 불릴 때마다 다시 돌고, 부르는 자리는 배틀 시작·교체 뒤 재정렬·AI의 스피드 조회로
  # 여럿이다. 그래서 둘로 나눈다.
  #
  #   ① `pbSpeed`는 등장 턴이면 `turncount`를 2로 위장해 그 두 분기를 지나간다.
  #      같은 메서드의 다른 `turncount` 참조는 `SLOWSTART`의 `<=5`(0도 2도 참)과
  #      `ACOMETIDA`의 `==1`(0도 2도 거짓)뿐이라 위장이 배율을 바꾸지 않는다.
  #   ② 치료와 문구는 등장 특성이 실제로 발동하는 `pbAbilitiesOnSwitchIn`으로 옮겼다.
  #
  # 옮기면서 원본의 결함 하나를 바로잡았다 — 첫 치료 루프의 쇠약·출혈 가지가
  # `party[i].name`을 쓰는데 그 루프의 `i`는 Battler 객체이고 지역변수 `party`는 그
  # 아래에서야 대입된다(루비 1.8.7에서 NameError). 다른 가지처럼 `i.pbThis`를 쓴다.
  # 문구는 번역표 조회 열쇠라 원본 리터럴 그대로 둔다.

  alias qol_z42_pbSpeed pbSpeed
  def pbSpeed
    # @battle을 안 물으므로 사파리존(딴 배틀 클래스)에서도 그대로 선다.
    return qol_z42_pbSpeed if @turncount!=0
    @turncount=2
    begin
      return qol_z42_pbSpeed
    ensure
      @turncount=0
    end
  end

  # 등장마다 한 번만 돌게 하는 표시를 교체 초기화 때 내린다.
  alias qol_z42_pbInitEffects pbInitEffects
  def pbInitEffects(batonpass)
    @qol_z42_entryDone=false
    qol_z42_pbInitEffects(batonpass)
  end

  alias qol_z42_pbAbilitiesOnSwitchIn pbAbilitiesOnSwitchIn
  def pbAbilitiesOnSwitchIn(onactive)
    qol_z42_pbAbilitiesOnSwitchIn(onactive)
    qol_z42_entryAbilities if onactive
  end

  def qol_z42_entryAbilities
    return if self.isFainted?
    return if @turncount!=0      # 원본의 발동 조건 그대로
    return if @qol_z42_entryDone # 같은 등장에서 두 번 불려도(메가진화 등) 한 번만
    @qol_z42_entryDone=true
    if self.hasWorkingAbility(:TINTINEO)
      @battle.pbDisplayPaused(_INTL("¡{1} tintinea como una campana!",pbThis))
      activepkmn=[]
      for i in @battle.battlers
        next if self.pbIsOpposing?(i.index) || i.isFainted?
        activepkmn.push(i.pokemonIndex)
        case i.status
        when PBStatuses::PARALYSIS
          @battle.pbDisplay(_INTL("¡{1} se curó de la parálisis!",i.pbThis))
        when PBStatuses::SLEEP
          @battle.pbDisplay(_INTL("¡{1} se despertó!",i.pbThis))
        when PBStatuses::POISON
          @battle.pbDisplay(_INTL("¡{1} se curó del envenenamiento!",i.pbThis))
        when PBStatuses::BURN
          @battle.pbDisplay(_INTL("¡{1} se curó de la quemadura!",i.pbThis))
        when PBStatuses::FROZEN
          @battle.pbDisplay(_INTL("¡{1} se descongeló!",i.pbThis))
        when PBStatuses::CADUCO
          @battle.pbDisplay(_INTL("¡{1} se curó del estado Caduco!",i.pbThis))
        when PBStatuses::HEMORRAGIA
          @battle.pbDisplay(_INTL("¡{1} se curó de la Hemorragia!",i.pbThis))
        end
        i.pbCureStatus(false)
      end
      party=@battle.pbParty(self.index) # NOTE: Considers both parties in multi battles
      for i in 0...party.length
        next if activepkmn.include?(i)
        next if !party[i] || party[i].isEgg? || party[i].hp<=0
        case party[i].status
        when PBStatuses::PARALYSIS
          @battle.pbDisplay(_INTL("¡{1} se curó de la parálisis!",party[i].name))
        when PBStatuses::SLEEP
          @battle.pbDisplay(_INTL("¡{1} se despertó!",party[i].name))
        when PBStatuses::POISON
          @battle.pbDisplay(_INTL("¡{1} se curó del envenenamiento!",party[i].name))
        when PBStatuses::BURN
          @battle.pbDisplay(_INTL("¡{1} se curó de la quemadura!",party[i].name))
        when PBStatuses::FROZEN
          @battle.pbDisplay(_INTL("¡{1} se descongeló!",party[i].name))
        when PBStatuses::CADUCO
          @battle.pbDisplay(_INTL("¡{1} se curó del estado Caduco!",party[i].name))
        when PBStatuses::HEMORRAGIA
          @battle.pbDisplay(_INTL("¡{1} se curó de la Hemorragia!",party[i].name))
        end
        party[i].status=0
        party[i].statusCount=0
      end
    end
    if self.hasWorkingAbility(:ACOMETIDA)
      @battle.pbDisplayPaused(_INTL("¡{1} entra a combatir con furia desmedida!",pbThis))
    end
  end
end
