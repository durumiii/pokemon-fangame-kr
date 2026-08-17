  def pbEndOfBattle(canlose=false)
    case @decision
    ##### VICTORIA #####
    when 1
      PBDebug.log("")
      PBDebug.log("***Jugador ganó***")
      if @opponent
        @scene.pbTrainerBattleSuccess
        if @opponent.is_a?(Array)
          pbDisplayPaused(_INTL("¡{1} ha derrotado a {2} y {3}!",self.pbPlayer.name,@opponent[0].fullname,@opponent[1].fullname))
        else
          pbDisplayPaused(_INTL("¡{1} ha derrotado a\r\n{2}!",self.pbPlayer.name,@opponent.fullname))
        end
        @scene.pbShowOpponent(0)
        pbDisplayPaused(@endspeech.gsub(/\\[Pp][Nn]/,self.pbPlayer.name))
        if @opponent.is_a?(Array)
          @scene.pbHideOpponent
          @scene.pbShowOpponent(1)
          pbDisplayPaused(@endspeech2.gsub(/\\[Pp][Nn]/,self.pbPlayer.name))
        end
        # Se calcula el dinero ganado por la victoria
        if @internalbattle
          tmoney=0
          if @opponent.is_a?(Array)             # Batallas dobles
            maxlevel1=0; maxlevel2=0; limit=pbSecondPartyBegin(1)
            for i in 0...limit
              if @party2[i]
                maxlevel1=@party2[i].level if maxlevel1<@party2[i].level
              end
              if @party2[i+limit]
                maxlevel2=@party2[i+limit].level if maxlevel1<@party2[i+limit].level
              end
            end
            tmoney+=maxlevel1*@opponent[0].moneyEarned
            tmoney+=maxlevel2*@opponent[1].moneyEarned
          else
            maxlevel=0
            for i in @party2
              next if !i
              maxlevel=i.level if maxlevel<i.level
            end
            tmoney+=maxlevel*@opponent.moneyEarned
          end
          # If Amulet Coin/Luck Incense's effect applies, double money earned
          tmoney*=2 if @amuletcoin
          # If Happy Hour's effect applies, double money earned
          tmoney*=2 if @doublemoney
          oldmoney=self.pbPlayer.money
          self.pbPlayer.money+=tmoney
          moneygained=self.pbPlayer.money-oldmoney
          if moneygained>0
            pbDisplayPaused(_INTL("¡{1} ha obtenido ${2}\r\npor la victoria!",self.pbPlayer.name,tmoney))
          end
        end
      end
      if @internalbattle && @extramoney>0
        @extramoney*=2 if @amuletcoin
        @extramoney*=2 if @doublemoney
        oldmoney=self.pbPlayer.money
        self.pbPlayer.money+=@extramoney
        moneygained=self.pbPlayer.money-oldmoney
        if moneygained>0
          pbDisplayPaused(_INTL("¡{1} ha recogido ${2}!",self.pbPlayer.name,@extramoney))
        end
      end
      for pkmn in @snaggedpokemon
        pbStorePokemon(pkmn)
        self.pbPlayer.shadowcaught=[] if !self.pbPlayer.shadowcaught
        self.pbPlayer.shadowcaught[pkmn.species]=true
      end
      @snaggedpokemon.clear
    ##### DERROTA, EMPATE #####
    when 2, 5
      PBDebug.log("")
      PBDebug.log("***Jugador perdió***") if @decision==2
      PBDebug.log("***Jugador empató con oponente***") if @decision==5
      if @internalbattle
        pbDisplayPaused(_INTL("¡{1} no tiene más Pokémon que puedan pelear!",self.pbPlayer.name))
        moneylost=pbMaxLevelFromIndex(0)   # Player's Pokémon only, not partner's
        multiplier=[8,16,24,36,48,60,80,100,120]
        moneylost*=multiplier[[multiplier.length-1,self.pbPlayer.numbadges].min]
        moneylost=self.pbPlayer.money if moneylost>self.pbPlayer.money
        moneylost=0 if $game_switches[NO_MONEY_LOSS]
        oldmoney=self.pbPlayer.money
        self.pbPlayer.money-=moneylost
        lostmoney=oldmoney-self.pbPlayer.money
        if @opponent
          if @opponent.is_a?(Array)
            pbDisplayPaused(_INTL("¡{1} ha perdido contra {2} y {3}!",self.pbPlayer.name,@opponent[0].fullname,@opponent[1].fullname))
          else
            pbDisplayPaused(_INTL("¡{1} ha perdido contra\r\n{2}!",self.pbPlayer.name,@opponent.fullname))
          end
          if moneylost>0
            pbDisplayPaused(_INTL("{1} ha entregado ${2} al ganador...",self.pbPlayer.name,lostmoney))
            pbDisplayPaused(_INTL("...")) if !canlose
          end
        else
          if moneylost>0
            pbDisplayPaused(_INTL("{1} entró en pánico y dejó caer\r\n${2}...",self.pbPlayer.name,lostmoney))
            pbDisplayPaused(_INTL("...")) if !canlose
          end
        end
        pbDisplayPaused(_INTL("¡{1} se desmayó!",self.pbPlayer.name)) if !canlose
      elsif @decision==2
        @scene.pbShowOpponent(0)
        pbDisplayPaused(@endspeechwin.gsub(/\\[Pp][Nn]/,self.pbPlayer.name))
        if @opponent.is_a?(Array)
          @scene.pbHideOpponent
          @scene.pbShowOpponent(1)
          pbDisplayPaused(@endspeechwin2.gsub(/\\[Pp][Nn]/,self.pbPlayer.name))
        end
      end
    end
    # Pass on Pokérus within the party
    infected=[]
    for i in 0...$Trainer.party.length
      if $Trainer.party[i].pokerusStage==1
        infected.push(i)
      end
    end
    if infected.length>=1
      for i in infected
        strain=$Trainer.party[i].pokerus/16
        if i>0 && $Trainer.party[i-1].pokerusStage==0
          $Trainer.party[i-1].givePokerus(strain) if rand(3)==0
        end
        if i<$Trainer.party.length-1 && $Trainer.party[i+1].pokerusStage==0
          $Trainer.party[i+1].givePokerus(strain) if rand(3)==0
        end
      end
    end
    @scene.pbEndBattle(@decision)
    for i in @battlers
      i.pbResetForm
      i.makeDisguised rescue nil
      if i.hasWorkingAbility(:NATURALCURE)
        i.status=0
      end
    end
    for i in $Trainer.party
      i.setItem(i.itemInitial)
      i.itemInitial=i.itemRecycle=0
      i.belch=false
    end
    return @decision
  end
