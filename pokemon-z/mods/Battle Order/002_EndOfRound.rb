# Battle Order — 라운드 종료 연출 순서 (Pokemon Z v2.18 · Essentials v16 · 루비 1.8.7)
#
# 이 게임은 라운드 끝의 지속 데미지를 「체력을 깎고 나서 연출·메시지」 순서로 낸다.
# 본가는 반대다 — 메시지가 뜨고 체력이 깎인다. 순정 Essentials에서는 체력 갱신이
# 조용해서 티가 덜 났는데, 이 게임은 체력 변화를 그리는 `pbHPChanged`를 고쳐 인자와
# 무관하게 언제나 체력바를 흘리고 데미지 숫자까지 띄우므로 어긋남이 그대로 보인다.
#
# 원본 `pbEndOfRoundPhase`를 그대로 떠 와서, 아래 자리에서만 연출·메시지를 체력 변화
# 앞으로 옮겼다. 다른 줄은 한 글자도 건드리지 않았다.
#   · 독 · 화상 · 얼음 — 연출과 메시지를 내는 `pbContinueStatus`를 체력 감소 앞으로
#   · 태양의힘(맑음/강한 햇살) · 모래바람 · 섀도우스카이 · 악몽 · 저주 · 조이기 기술 ·
#     끈적끈적바늘 — 메시지를 체력 감소 앞으로
#
# 손대지 않은 자리와 그 이유는 이 폴더의 AGENTS.md에 적어 두었다.

class PokeBattle_Battle
  def pbEndOfRoundPhase
    PBDebug.log("[Final de la ronda]")
    for i in 0...4
      @battlers[i].effects[PBEffects::Electrify]=false
      @battlers[i].effects[PBEffects::Endure]=false
      @battlers[i].effects[PBEffects::FirstPledge]=0
      @battlers[i].effects[PBEffects::HyperBeam]-=1 if @battlers[i].effects[PBEffects::HyperBeam]>0
      @battlers[i].effects[PBEffects::KingsShield]=false
      @battlers[i].effects[PBEffects::LifeOrb]=false
      @battlers[i].effects[PBEffects::MoveNext]=false
      @battlers[i].effects[PBEffects::Powder]=false
      @battlers[i].effects[PBEffects::Protect]=false
      @battlers[i].effects[PBEffects::ProtectNegation]=false
      @battlers[i].effects[PBEffects::Quash]=false
      @battlers[i].effects[PBEffects::Roost]=false
      @battlers[i].effects[PBEffects::SpikyShield]=false
      @battlers[i].effects[PBEffects::BanefulBunker]=false
    end
    @usepriority=false  # recalculate priority
    priority=pbPriority(true) # Ignoring Quick Claw here
    # Weather
    case @weather
    when PBWeather::SUNNYDAY
      @weatherduration=@weatherduration-1 if @weatherduration>0
      if @weatherduration==0
        pbDisplay(_INTL("Se ha ido el sol."))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima Día Soleado se terminó")
      else
        pbCommonAnimation("Sunny",nil,nil)
#        pbDisplay(_INTL("Hace mucho sol..."))
        if pbWeather==PBWeather::SUNNYDAY
          for i in priority
            if i.hasWorkingAbility(:SOLARPOWER)                       # Poder solar
              PBDebug.log("[Habilidad disparada] Poder Solar de #{i.pbThis}")
              @scene.pbDamageAnimation(i,0)
              pbDisplay(_INTL("¡{1} perdió algunos PS debido al Poder Solar!",i.pbThis))
              i.pbReduceHP((i.totalhp/8).floor)
              if i.isFainted?
                return if !i.pbFaint
              end
            end
          end
        end
      end
    when PBWeather::RAINDANCE
      @weatherduration=@weatherduration-1 if @weatherduration>0
      if @weatherduration==0
        pbDisplay(_INTL("Ha dejado de llover."))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima Lluvia se terminó")
      else
        pbCommonAnimation("Rain",nil,nil)
#        pbDisplay(_INTL("Sigue lloviendo..."))
      end
    when PBWeather::SANDSTORM
      @weatherduration=@weatherduration-1 if @weatherduration>0
      if @weatherduration==0
        pbDisplay(_INTL("La tormenta de arena amainó."))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima Tormenta de Arena terminó")
      else
        pbCommonAnimation("Sandstorm",nil,nil)
#        pbDisplay(_INTL("La tormenta de arena arrecia..."))
        if pbWeather==PBWeather::SANDSTORM
          PBDebug.log("[Efecto prolongado disparado] El clima Tormenta de Arena inflinge daño")
          for i in priority
            next if i.isFainted?
            if !i.pbHasType?(:GROUND) && !i.pbHasType?(:ROCK) && !i.pbHasType?(:STEEL) &&
               !i.hasWorkingAbility(:SANDVEIL) &&
               !i.hasWorkingAbility(:SANDRUSH) &&
               !i.hasWorkingAbility(:SANDFORCE) &&
               !i.hasWorkingAbility(:MAGICGUARD) &&
               !i.hasWorkingAbility(:OVERCOAT) &&
               !i.hasWorkingItem(:SAFETYGOGGLES) &&
               ![0xCA,0xCB].include?(PBMoveData.new(i.effects[PBEffects::TwoTurnAttack]).function) # Dig, Dive
              @scene.pbDamageAnimation(i,0)
              pbDisplay(_INTL("¡La tormenta de arena zarandea a {1}!",i.pbThis))
              i.pbReduceHP((i.totalhp/16).floor)
              if i.isFainted?
                return if !i.pbFaint
              end
            end
          end
        end
      end
    when PBWeather::HAIL
      @weatherduration=@weatherduration-1 if @weatherduration>0
      if @weatherduration==0
        pbDisplay(_INTL("Ha dejado de nevar."))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima Granizo terminó")
      else
        pbCommonAnimation("Hail",nil,nil)
#        pbDisplay(_INTL("Sigue granizando..."))
        if false#PBWeather::HAIL
          PBDebug.log("[Efecto prolongado disparado] El clima Granizo inflinge daño")
          for i in priority
            next if i.isFainted?
            if !i.pbHasType?(:ICE) &&
               !i.hasWorkingAbility(:ICEBODY) &&
               !i.hasWorkingAbility(:PODERGELIDO) &&
               !i.hasWorkingAbility(:SNOWCLOAK) &&
               !i.hasWorkingAbility(:MAGICGUARD) &&
               !i.hasWorkingAbility(:OVERCOAT) &&
               !i.hasWorkingItem(:SAFETYGOGGLES) &&
               ![0xCA,0xCB].include?(PBMoveData.new(i.effects[PBEffects::TwoTurnAttack]).function) # Dig, Dive
              if i.isFainted?
                return if !i.pbFaint
              end
            end
          end
        end
      end
    when PBWeather::HEAVYRAIN                              # Mar del Albor
      hasabil=false
      for i in 0...4
        if isConst?(@battlers[i].ability,PBAbilities,:PRIMORDIALSEA) && !@battlers[i].isFainted?
          hasabil=true; break
        end
      end
      @weatherduration=0 if !hasabil
      if @weatherduration==0
        pbDisplay(_INTL("¡El diluvio ha terminado!"))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima del Mar del Albor ha terminado")
      else
        pbCommonAnimation("HeavyRain",nil,nil)
      end
    when PBWeather::HARSHSUN                               # Tierra del Ocaso
      hasabil=false
      for i in 0...4
        if isConst?(@battlers[i].ability,PBAbilities,:DESOLATELAND) && !@battlers[i].isFainted?
          hasabil=true; break
        end
      end
      @weatherduration=0 if !hasabil
      if @weatherduration==0
        pbDisplay(_INTL("¡El sol vuelve a brillar como siempre!"))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima de la Tierra del Ocaso ha terminado")
      else
        pbCommonAnimation("HarshSun",nil,nil)
        if pbWeather==PBWeather::HARSHSUN
          for i in priority
            if i.hasWorkingAbility(:SOLARPOWER)            # Poder Solar
              PBDebug.log("[Habilidad disparada] Poder Solar de #{i.pbThis}")
              @scene.pbDamageAnimation(i,0)
              pbDisplay(_INTL("¡{1} ha sido dañado por la luz solar!",i.pbThis))
              i.pbReduceHP((i.totalhp/8).floor)
              if i.isFainted?
                return if !i.pbFaint
              end
            end
          end
        end
      end
    when PBWeather::STRONGWINDS                            # Ráfaga Delta
      hasabil=false
      for i in 0...4
        if isConst?(@battlers[i].ability,PBAbilities,:DELTASTREAM) && !@battlers[i].isFainted?
          hasabil=true; break
        end
      end
      @weatherduration=0 if !hasabil
      if @weatherduration==0
        pbDisplay(_INTL("¡Las misteriosas turbulencias han amainado!"))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima de Ráfaga Delta ha terminado")
      else
        pbCommonAnimation("StrongWinds",nil,nil)
      end
    end
    # Shadow Sky weather  /  Clima Cielo Oscuro (de Pkm XD)
    if isConst?(@weather,PBWeather,:SHADOWSKY)
      @weatherduration=@weatherduration-1 if @weatherduration>0
      if @weatherduration==0
        pbDisplay(_INTL("El cielo oscuro se ha aclarado."))
        @weather=0
        PBDebug.log("[Fin de efecto] El clima Cielo Oscuro ha terminado")
      else
        pbCommonAnimation("ShadowSky",nil,nil)
#        pbDisplay(_INTL("El cielo sigue oscuro..."));
        if isConst?(pbWeather,PBWeather,:SHADOWSKY)
          PBDebug.log("[Efecto prolongado disparado] El clima Cielo Oscuro inflinge daño")
          for i in priority
            next if i.isFainted?
            if !i.isShadow?
              @scene.pbDamageAnimation(i,0)
              pbDisplay(_INTL("¡{1} ha sido dañado por el cielo oscuro!",i.pbThis))
              i.pbReduceHP((i.totalhp/16).floor)
              if i.isFainted?
                return if !i.pbFaint
              end
            end
          end
        end
      end
    end
    # Future Sight/Doom Desire     -   Premonición/Deseo Oculto
    for i in battlers   # not priority
      next if i.isFainted?
      if i.effects[PBEffects::FutureSight]>0
        i.effects[PBEffects::FutureSight]-=1
        if i.effects[PBEffects::FutureSight]==0
          move=i.effects[PBEffects::FutureSightMove]
          PBDebug.log("[Efecto prolongado disparado] #{PBMoves.getName(move)} ha golpeado a #{i.pbThis(true)}")
          pbDisplay(_INTL("¡{1} ha sufrido el ataque {2}!",i.pbThis,PBMoves.getName(move)))
          moveuser=nil
          for j in battlers
            next if j.pbIsOpposing?(i.effects[PBEffects::FutureSightUserPos])
            if j.pokemonIndex==i.effects[PBEffects::FutureSightUser] && !j.isFainted?
              moveuser=j; break
            end
          end
          if !moveuser
            party=pbParty(i.effects[PBEffects::FutureSightUserPos])
            if party[i.effects[PBEffects::FutureSightUser]].hp>0
              moveuser=PokeBattle_Battler.new(self,i.effects[PBEffects::FutureSightUserPos])
              moveuser.pbInitDummyPokemon(party[i.effects[PBEffects::FutureSightUser]],
                                          i.effects[PBEffects::FutureSightUser])
            end
          end
          if !moveuser
            pbDisplay(_INTL("¡Pero falló!"))
          else
            @futuresight=true
            moveuser.pbUseMoveSimple(move,-1,i.index)
            @futuresight=false
          end
          i.effects[PBEffects::FutureSight]=0
          i.effects[PBEffects::FutureSightMove]=0
          i.effects[PBEffects::FutureSightUser]=-1
          i.effects[PBEffects::FutureSightUserPos]=-1
          if i.isFainted?
            return if !i.pbFaint
            next
          end
        end
      end
    end
    for i in priority
      next if i.isFainted?
      # Rain Dish   /   Cura Lluvia
      if i.hasWorkingAbility(:RAINDISH) &&
         (pbWeather==PBWeather::RAINDANCE ||
         pbWeather==PBWeather::HEAVYRAIN)
        PBDebug.log("[Habilidad disparada] Cura Lluvia de #{i.pbThis}")
        hpgain=i.pbRecoverHP((i.totalhp/16).floor,true)
        pbDisplay(_INTL("¡{1} ha restaurado algunos PS gracias a {2}!",i.pbThis,PBAbilities.getName(i.ability))) if hpgain>0
      end
      # Dry Skin  /  Piel Seca
      if i.hasWorkingAbility(:DRYSKIN)
        if pbWeather==PBWeather::RAINDANCE ||
           pbWeather==PBWeather::HEAVYRAIN
          PBDebug.log("[Habilidad disparada] Piel Seca de #{i.pbThis} (bajo lluvia)")
          hpgain=i.pbRecoverHP((i.totalhp/8).floor,true)
          pbDisplay(_INTL("¡{1} ha restaurado algunos PS por su {2}!",i.pbThis,PBAbilities.getName(i.ability))) if hpgain>0
        elsif pbWeather==PBWeather::SUNNYDAY ||
              pbWeather==PBWeather::HARSHSUN
          PBDebug.log("[Habilidad disparada] Piel Seca de #{i.pbThis} (al sol)")
          @scene.pbDamageAnimation(i,0)
          hploss=i.pbReduceHP((i.totalhp/8).floor)
          pbDisplay(_INTL("¡{1} ha sido dañado por la fuerte luz del sol sobre su {2}!",i.pbThis,PBAbilities.getName(i.ability))) if hploss>0
        end
      end
      # Ice Body  /  Gélido
      if i.hasWorkingAbility(:ICEBODY) && pbWeather==PBWeather::HAIL
        PBDebug.log("[Habilidad disparada] Gélido de #{i.pbThis}")
        hpgain=i.pbRecoverHP((i.totalhp/16).floor,true)
        pbDisplay(_INTL("{1} ha restaurado algunos PS con {2}!",i.pbThis,PBAbilities.getName(i.ability))) if hpgain>0
      end
      if i.isFainted?
        return if !i.pbFaint
      end
    end
    # Wish  /  Deseo
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Wish]>0
        i.effects[PBEffects::Wish]-=1
        if i.effects[PBEffects::Wish]==0
          PBDebug.log("[Efecto prolongado disparado] Deseo de #{i.pbThis}")
          hpgain=i.pbRecoverHP(i.effects[PBEffects::WishAmount],true)
          if hpgain>0
            wishmaker=pbThisEx(i.index,i.effects[PBEffects::WishMaker])
            pbDisplay(_INTL("¡El deseo de {1} se hizo realidad!",wishmaker))
          end
        end
      end
    end
    # Fire Pledge + Grass Pledge combination damage
    for i in 0...2
      if sides[i].effects[PBEffects::SeaOfFire]>0 &&
         pbWeather!=PBWeather::RAINDANCE &&
         pbWeather!=PBWeather::HEAVYRAIN
        @battle.pbCommonAnimation("SeaOfFire",nil,nil) if i==0
        @battle.pbCommonAnimation("SeaOfFireOpp",nil,nil) if i==1
        for j in priority
          next if (j.index&1)!=i
          next if j.pbHasType?(:FIRE) || j.hasWorkingAbility(:MAGICGUARD)
          @scene.pbDamageAnimation(j,0)
          hploss=j.pbReduceHP((j.totalhp/8).floor)
          pbDisplay(_INTL("¡{1} ha sido dañado por el mar de llamas!",j.pbThis)) if hploss>0
          if j.isFainted?
            return if !j.pbFaint
          end
        end
      end
    end
    for i in priority
      next if i.isFainted?
      # Shed Skin, Hydration
      if (i.hasWorkingAbility(:SHEDSKIN) && pbRandom(10)<3) ||
         (i.hasWorkingAbility(:HYDRATION) && (pbWeather==PBWeather::RAINDANCE ||
                                              pbWeather==PBWeather::HEAVYRAIN))
        if i.status>0
          PBDebug.log("[Habilidad disparada] #{PBAbilities.getName(i.ability)} de #{i.pbThis}")
          s=i.status
          i.pbCureStatus(false)
          case s
          when PBStatuses::SLEEP
            pbDisplay(_INTL("¡{2} de {1} lo despertó!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::POISON
            pbDisplay(_INTL("¡{2} de {1} le curó el veneno!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::BURN
            pbDisplay(_INTL("¡{2} de {1} le curó la quemadura!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::PARALYSIS
            pbDisplay(_INTL("¡{2} de {1} le curó la parálisis!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::FROZEN
            pbDisplay(_INTL("¡{2} de {1} le permitió descongelarse!",i.pbThis,PBAbilities.getName(i.ability)))
          end
        end
      end
      # Healer
      if i.hasWorkingAbility(:HEALER) && pbRandom(10)<3
        partner=i.pbPartner
        if partner && partner.status>0
          PBDebug.log("[Habilidad disparada] #{PBAbilities.getName(i.ability)} de #{i.pbThis}")
          s=partner.status
          partner.pbCureStatus(false)
          case s
          when PBStatuses::SLEEP
            pbDisplay(_INTL("¡{2} de {1} le quitó el sueño a su compañero!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::POISON
            pbDisplay(_INTL("¡{2} de {1} le curó el venenó a su compañero!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::BURN
            pbDisplay(_INTL("¡{2} de {1} le curó la quemadura a su compañero!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::PARALYSIS
            pbDisplay(_INTL("¡{2} de {1} liberó de la parálisis a su compañero!",i.pbThis,PBAbilities.getName(i.ability)))
          when PBStatuses::FROZEN
            pbDisplay(_INTL("¡{2} de {1} descongeló a su compañero!",i.pbThis,PBAbilities.getName(i.ability)))
          end
        end
      end
    end
    for i in priority
      next if i.isFainted?
      # Grassy Terrain (healing)
      if @field.effects[PBEffects::GrassyTerrain]>0 && !i.isAirborne?
        hpgain=i.pbRecoverHP((i.totalhp/16).floor,true)
        pbDisplay(_INTL("Los PS de {1} han sido recuperados.",i.pbThis)) if hpgain>0
      end
      # Held berries/Leftovers/Black Sludge
      i.pbBerryCureCheck(true)
      if i.isFainted?
        return if !i.pbFaint
      end
    end
    # Acua Aro / Aqua Ring
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::AquaRing]
        PBDebug.log("[Efecto prolongado disparado] Acua Aro de #{i.pbThis}")
        hpgain=(i.totalhp/16).floor
        hpgain=(hpgain*1.3).floor if i.hasWorkingItem(:BIGROOT)
        hpgain=i.pbRecoverHP(hpgain,true)
        pbDisplay(_INTL("¡Acua Aro ha recuperado salud de {1}!",i.pbThis)) if hpgain>0
      end
    end
    # Arraigo / Ingrain
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Ingrain]
        PBDebug.log("[Efecto prolongado disparado] Arraigo de #{i.pbThis}")
        hpgain=(i.totalhp/16).floor
        hpgain=(hpgain*1.3).floor if i.hasWorkingItem(:BIGROOT)         # Raíz Grande
        hpgain=i.pbRecoverHP(hpgain,true)
        pbDisplay(_INTL("¡{1} ha absorbido nutrientes con las raíces!",i.pbThis)) if hpgain>0
      end
    end
    # Drenadoras / Leech Seed
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::LeechSeed]>=0 && !i.hasWorkingAbility(:MAGICGUARD)
        recipient=@battlers[i.effects[PBEffects::LeechSeed]]
        if recipient && !recipient.isFainted?            # si existe beneficiario
          PBDebug.log("[Efecto prolongado disparado] Drenadoras de #{i.pbThis}")
          pbCommonAnimation("LeechSeed",recipient,i)
          hploss=i.pbReduceHP((i.totalhp/8).floor,true)
          if i.hasWorkingAbility(:LIQUIDOOZE)
            recipient.pbReduceHP(hploss,true)
            pbDisplay(_INTL("¡{1} ha absorbido el Lodo Líquido!",recipient.pbThis))
          else
            if recipient.effects[PBEffects::HealBlock]==0
              hploss=(hploss*1.3).floor if recipient.hasWorkingItem(:BIGROOT)
              recipient.pbRecoverHP(hploss,true)
            end
            pbDisplay(_INTL("¡Las drenadoras restaron salud a {1}!",i.pbThis))
          end
          if i.isFainted?
            return if !i.pbFaint
          end
          if recipient.isFainted?
            return if !recipient.pbFaint
          end
        end
      end
    end
    for i in priority
      next if i.isFainted?
      # Envenenado/Gravemente envenenado         Poison/Bad poison
      if i.status==PBStatuses::POISON
        if i.statusCount>0
          i.effects[PBEffects::Toxic]+=1
          i.effects[PBEffects::Toxic]=[15,i.effects[PBEffects::Toxic]].min
        end
        if i.hasWorkingAbility(:POISONHEAL)                # Antídoto
          pbCommonAnimation("Poison",i,nil)
          if i.effects[PBEffects::HealBlock]==0 && i.hp<i.totalhp
            PBDebug.log("[Habilidad disparada] Antídoto de #{i.pbThis}")
            i.pbRecoverHP((i.totalhp/8).floor,true)
            pbDisplay(_INTL("¡{1} ha recuperado salud gracias al Antídoto!",i.pbThis))
          end
        else
          if !i.hasWorkingAbility(:MAGICGUARD)             # Muro Mágico
            PBDebug.log("[Daño por estado] #{i.pbThis} recibió daño por el veneno/tóxico")
            i.pbContinueStatus
            if i.statusCount==0
              if i.pbOpposing1.hasWorkingAbility(:ALQUIMIAVIL) || i.pbOpposing2.hasWorkingAbility(:ALQUIMIAVIL)
                i.pbReduceHP((i.totalhp/6).floor)
              else
                i.pbReduceHP((i.totalhp/12).floor)
              end
            else
              if i.pbOpposing1.hasWorkingAbility(:ALQUIMIAVIL) || i.pbOpposing2.hasWorkingAbility(:ALQUIMIAVIL)
                i.pbReduceHP(((i.totalhp*i.effects[PBEffects::Toxic])/8).floor)
              else
                i.pbReduceHP(((i.totalhp*i.effects[PBEffects::Toxic])/16).floor)
              end
            end
          end
        end
      end
      # Quemadura  /  Burn
      if i.status==PBStatuses::BURN
        i.pbContinueStatus
        if !i.hasWorkingAbility(:MAGICGUARD)               # Muro Mágico
          PBDebug.log("[Daño por estado] #{i.pbThis} recibió daño por la quemadura")
          if i.hasWorkingAbility(:HEATPROOF)               # Ignífugo
            PBDebug.log("[Habilidad disparada] Ignífugo de #{i.pbThis}")
            i.pbReduceHP((i.totalhp/16).floor)
          else
            i.pbReduceHP((i.totalhp/16).floor)
          end
        end
      end
      
      # Congelación Arceus
      if i.status==PBStatuses::FROZEN
        i.pbContinueStatus
        if !i.hasWorkingAbility(:MAGICGUARD)               # Muro Mágico
          PBDebug.log("[Daño por estado] #{i.pbThis} recibió daño por congelación")
          i.pbReduceHP((i.totalhp/16).floor)
        end
      end
      
      # Caduco Mensaje
      if i.status==PBStatuses::CADUCO && i.hp<=(i.totalhp/2).floor
        PBDebug.log("¡El Pokémon ha perdido su luz!")
        i.pbContinueStatus
      end
      
      # Hemorragia Mensaje
      if i.status==PBStatuses::HEMORRAGIA
        PBDebug.log("¡El Pokémon sufre Hemorragia!")
        i.pbContinueStatus
      end      
      
      
      # Pesadilla  /  Nightmare
      if i.effects[PBEffects::Nightmare]
        if i.status==PBStatuses::SLEEP
          if !i.hasWorkingAbility(:MAGICGUARD)
            PBDebug.log("[Efecto prolongado disparado] Pesadilla de #{i.pbThis}")
            pbDisplay(_INTL("¡{1} está inmerso en una Pesadilla!",i.pbThis))
            i.pbReduceHP((i.totalhp/4).floor,true)
          end
        else
          i.effects[PBEffects::Nightmare]=false
        end
      end
      if i.isFainted?
        return if !i.pbFaint
        next
      end
    end
    # Maldición  /  Curse
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Curse] && !i.hasWorkingAbility(:MAGICGUARD)
        PBDebug.log("[Efecto prolongado disparado] Maldición de #{i.pbThis}")
        pbDisplay(_INTL("¡{1} es víctima de una Maldición!",i.pbThis))
        i.pbReduceHP((i.totalhp/4).floor,true)
      end
      if i.isFainted?
        return if !i.pbFaint
        next
      end
    end
    # Ataques Multi-turnos (Bind/Clamp/Fire Spin/Magma Storm/Sand Tomb/Whirlpool/Wrap)
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::MultiTurn]>0
        i.effects[PBEffects::MultiTurn]-=1
        movename=PBMoves.getName(i.effects[PBEffects::MultiTurnAttack])
        if i.effects[PBEffects::MultiTurn]==0
          PBDebug.log("[Fin de efecto] El movimiento de trampa #{movename} que afectaba a #{i.pbThis} terminó")
          pbDisplay(_INTL("¡{1} se liberó de {2}!",i.pbThis,movename))
        else
          if isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:BIND)
            pbCommonAnimation("Bind",i,nil)
          elsif isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:CLAMP)
            pbCommonAnimation("Clamp",i,nil)
          elsif isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:FIRESPIN)
            pbCommonAnimation("FireSpin",i,nil)
          elsif isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:MAGMASTORM)
            pbCommonAnimation("MagmaStorm",i,nil)
          elsif isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:SANDTOMB)
            pbCommonAnimation("SandTomb",i,nil)
          elsif isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:WRAP)
            pbCommonAnimation("Wrap",i,nil)
          elsif isConst?(i.effects[PBEffects::MultiTurnAttack],PBMoves,:INFESTATION)
            pbCommonAnimation("Infestation",i,nil)
          else
            pbCommonAnimation("Wrap",i,nil)
          end
          if !i.hasWorkingAbility(:MAGICGUARD)
            PBDebug.log("[Efecto prolongado disparado] #{i.pbThis} ha sido dañado por el movimiento de trampa #{movename}")
            @scene.pbDamageAnimation(i,0)
            amt=(USENEWBATTLEMECHANICS) ? (i.totalhp/8).floor : (i.totalhp/16).floor
            if @battlers[i.effects[PBEffects::MultiTurnUser]].hasWorkingItem(:BINDINGBAND)
              amt=(USENEWBATTLEMECHANICS) ? (i.totalhp/6).floor : (i.totalhp/8).floor
            end
      if isConst?( i.effects[PBEffects::MultiTurnAttack],PBMoves,:SALAZON) && ( i.pbHasType?(PBTypes::WATER) || i.pbHasType?(PBTypes::STEEL) )
        amt= (i.totalhp/4).floor 
      end               
            pbDisplay(_INTL("¡{1} ha sido dañado por {2}!",i.pbThis,movename))
            i.pbReduceHP(amt)
          end
        end
      end  
      if i.isFainted?
        return if !i.pbFaint
      end
    end
    # Mofa  /  Taunt
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Taunt]>0
        i.effects[PBEffects::Taunt]-=1
        if i.effects[PBEffects::Taunt]==0
          pbDisplay(_INTL("¡El efecto de Mofa de {1} ha pasado!",i.pbThis))
          PBDebug.log("[Fin de efecto] #{i.pbThis} ya no está afectado por Mofa")
        end 
      end
    end
    # Otra Vez  /  Encore
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Encore]>0
        if i.moves[i.effects[PBEffects::EncoreIndex]].id!=i.effects[PBEffects::EncoreMove]
          i.effects[PBEffects::Encore]=0
          i.effects[PBEffects::EncoreIndex]=0
          i.effects[PBEffects::EncoreMove]=0
          PBDebug.log("[Fin de efecto] #{i.pbThis} is no longer encored (encored move was lost)")
        else
          i.effects[PBEffects::Encore]-=1
          if i.effects[PBEffects::Encore]==0 || i.moves[i.effects[PBEffects::EncoreIndex]].pp==0
            i.effects[PBEffects::Encore]=0
            pbDisplay(_INTL("¡Otra Vez ya no hace efecto en {1}!",i.pbThis))
            PBDebug.log("[Fin de efecto] #{i.pbThis} ya no es afectado por Otra Vez")
          end 
        end
      end
    end
    # Anulación/Cuerpo Maldito  -  Disable/Cursed Body
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Disable]>0
        i.effects[PBEffects::Disable]-=1
        if i.effects[PBEffects::Disable]==0
          i.effects[PBEffects::DisableMove]=0
          pbDisplay(_INTL("¡{1} ya no está desactivado!",i.pbThis))
          PBDebug.log("[Fin de efecto] #{i.pbThis} ya no está desactivado")
        end
      end
    end
    # Levitón  /  Magnet Rise
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::MagnetRise]>0
        i.effects[PBEffects::MagnetRise]-=1
        if i.effects[PBEffects::MagnetRise]==0
          pbDisplay(_INTL("¡El electromagnetismo de {1} desapareció!",i.pbThis))
          PBDebug.log("[Fin de efecto] #{i.pbThis} dejó de levitar con Levitón")
        end
      end
    end
    # Telequinesis / Telekinesis (Gen5)
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Telekinesis]>0
        i.effects[PBEffects::Telekinesis]-=1
        if i.effects[PBEffects::Telekinesis]==0
          pbDisplay(_INTL("¡{1} se liberó de la Telequinesis!",i.pbThis))
          PBDebug.log("[Fin de efecto] #{i.pbThis} ya no está levitando por Telequinesis")
        end
      end
    end
    # Anticura  /  Heal Block
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::HealBlock]>0
        i.effects[PBEffects::HealBlock]-=1
        if i.effects[PBEffects::HealBlock]==0
          pbDisplay(_INTL("¡Anticura ya no hace efecto en {1}!",i.pbThis))
          PBDebug.log("[Fin de efecto] #{i.pbThis} ya no tiene Anticura")
        end
      end
    end
    # Embargo
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Embargo]>0
        i.effects[PBEffects::Embargo]-=1
        if i.effects[PBEffects::Embargo]==0
          pbDisplay(_INTL("¡{1} puede volver a usar objetos!",i.pbThis(true)))
          PBDebug.log("[Fin de efecto] #{i.pbThis} ya no está afectado por Embargo")
        end
      end
    end
    # Bostezo  /  Yawn
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Yawn]>0
        i.effects[PBEffects::Yawn]-=1
        if i.effects[PBEffects::Yawn]==0 && i.pbCanSleepYawn?
          PBDebug.log("[Efecto prolongado disparado] Bostezo de #{i.pbThis}")
          i.pbSleep
        end
      end
    end
    # Canto Mortal / Perish Song
    perishSongUsers=[]
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::PerishSong]>0
        i.effects[PBEffects::PerishSong]-=1
        pbDisplay(_INTL("¡El contador de salud de {1} bajó a {2}!",i.pbThis,i.effects[PBEffects::PerishSong]))
        PBDebug.log("[Efecto prolongado disparado] El contador de Canto Mortal de #{i.pbThis} bajó a #{i.effects[PBEffects::PerishSong]}")
        if i.effects[PBEffects::PerishSong]==0
          perishSongUsers.push(i.effects[PBEffects::PerishSongUser])
          i.pbReduceHP(i.hp,true)
        end
      end
      if i.isFainted?
        return if !i.pbFaint
      end
    end
    if perishSongUsers.length>0
      # If all remaining Pokemon fainted by a Perish Song triggered by a single side
      if (perishSongUsers.find_all{|item| pbIsOpposing?(item) }.length==perishSongUsers.length) ||
         (perishSongUsers.find_all{|item| !pbIsOpposing?(item) }.length==perishSongUsers.length)
        pbJudgeCheckpoint(@battlers[perishSongUsers[0]])
      end
    end
    if @decision>0
      pbGainEXP
      return
    end
    # Reflejo  /  Reflect
    for i in 0...2
      if sides[i].effects[PBEffects::Reflect]>0
        sides[i].effects[PBEffects::Reflect]-=1
        if sides[i].effects[PBEffects::Reflect]==0
          pbDisplay(_INTL("¡Los efectos de Reflejo de tu equipo se disiparon!")) if i==0
          pbDisplay(_INTL("¡Los efectos de Reflejo del equipo enemigo se disiparon!")) if i==1
          PBDebug.log("[Fin de efecto] Reflejo del lado del jugador terminó") if i==0
          PBDebug.log("[Fin de efecto] Reflejo del lado del oponente terminó") if i==1
        end
      end
    end
    # Pantalla Luz  /  Light Screen
    for i in 0...2
      if sides[i].effects[PBEffects::LightScreen]>0
        sides[i].effects[PBEffects::LightScreen]-=1
        if sides[i].effects[PBEffects::LightScreen]==0
          pbDisplay(_INTL("¡Los efectos de Pantalla de Luz de tu equipo se disiparon!")) if i==0
          pbDisplay(_INTL("¡Los efectos de Pantalla de Luz del equipo enemigo se disiparon!")) if i==1
          PBDebug.log("[Fin de efecto] Pantalla de Luz del lado del jugador se terminó") if i==0
          PBDebug.log("[Fin de efecto] Pantalla de Luz del lado del oponente se terminó") if i==1
        end
      end
    end
    # Velo Sagrado / Safeguard
    for i in 0...2
      if sides[i].effects[PBEffects::Safeguard]>0
        sides[i].effects[PBEffects::Safeguard]-=1
        if sides[i].effects[PBEffects::Safeguard]==0
          pbDisplay(_INTL("¡Velo Sagrado de tu equipo dejó de hacer efecto!")) if i==0
          pbDisplay(_INTL("¡Velo Sagrado del equipo enemigo dejó de hacer efecto!")) if i==1
          PBDebug.log("[Fin de efecto] Velo Sagrado del lado del jugador terminó") if i==0
          PBDebug.log("[Fin de efecto] Velo Sagrado del lado del oponente terminó") if i==1
        end
      end
    end
    # Neblina  /  Mist
    for i in 0...2
      if sides[i].effects[PBEffects::Mist]>0
        sides[i].effects[PBEffects::Mist]-=1
        if sides[i].effects[PBEffects::Mist]==0
          pbDisplay(_INTL("¡Neblina de tu equipo dejó de hacer efecto!")) if i==0
          pbDisplay(_INTL("¡Neblina del equipo enemigo dejó de hacer efecto!")) if i==1
          PBDebug.log("[Fin de efecto] Neblina del lado del jugador terminó") if i==0
          PBDebug.log("[Fin de efecto] Neblina del lado del oponente terminó") if i==1
        end
      end
    end
    # Viento Afín / Tailwind
    for i in 0...2
      if sides[i].effects[PBEffects::Tailwind]>0
        sides[i].effects[PBEffects::Tailwind]-=1
        if sides[i].effects[PBEffects::Tailwind]==0
          pbDisplay(_INTL("¡Viento Afín de tu equipo dejó de hacer efecto!")) if i==0
          pbDisplay(_INTL("¡Viento Afín del equipo enemigo dejó de hacer efecto!")) if i==1
          PBDebug.log("[Fin de efecto] Viento Afín del lado del jugador terminó") if i==0
          PBDebug.log("[Fin de efecto] Viento Afín del lado del oponente terminó") if i==1
        end
      end
    end
    # Conjuro  /  Lucky Chant
    for i in 0...2
      if sides[i].effects[PBEffects::LuckyChant]>0
        sides[i].effects[PBEffects::LuckyChant]-=1
        if sides[i].effects[PBEffects::LuckyChant]==0
          pbDisplay(_INTL("¡Conjuro de tu equipo dejó de hacer efecto!")) if i==0
          pbDisplay(_INTL("¡Conjuro del equipo enemigo dejó de hacer efecto!")) if i==1
          PBDebug.log("[Fin de efecto] Conjuro del lado del jugador terminó") if i==0
          PBDebug.log("[Fin de efecto] Conjuro del lado del oponente terminó") if i==1
        end
      end
    end
    # Final de los movimientos combiandos Voto
    for i in 0...2
      if sides[i].effects[PBEffects::Swamp]>0
        sides[i].effects[PBEffects::Swamp]-=1
        if sides[i].effects[PBEffects::Swamp]==0
          pbDisplay(_INTL("The swamp around your team disappeared!")) if i==0
          pbDisplay(_INTL("The swamp around the opposing team disappeared!")) if i==1
          PBDebug.log("[Fin de efecto] Grass Pledge's swamp ended on the player's side") if i==0
          PBDebug.log("[Fin de efecto] Grass Pledge's swamp ended on the opponent's side") if i==1
        end
      end
      if sides[i].effects[PBEffects::SeaOfFire]>0
        sides[i].effects[PBEffects::SeaOfFire]-=1
        if sides[i].effects[PBEffects::SeaOfFire]==0
          pbDisplay(_INTL("The sea of fire around your team disappeared!")) if i==0
          pbDisplay(_INTL("The sea of fire around the opposing team disappeared!")) if i==1
          PBDebug.log("[Fin de efecto] Fire Pledge's sea of fire ended on the player's side") if i==0
          PBDebug.log("[Fin de efecto] Fire Pledge's sea of fire ended on the opponent's side") if i==1
        end
      end
      if sides[i].effects[PBEffects::Rainbow]>0
        sides[i].effects[PBEffects::Rainbow]-=1
        if sides[i].effects[PBEffects::Rainbow]==0
          pbDisplay(_INTL("The rainbow around your team disappeared!")) if i==0
          pbDisplay(_INTL("The rainbow around the opposing team disappeared!")) if i==1
          PBDebug.log("[Fin de efecto] Water Pledge's rainbow ended on the player's side") if i==0
          PBDebug.log("[Fin de efecto] Water Pledge's rainbow ended on the opponent's side") if i==1
        end
      end
    end
    # Gravedad  /  Gravity
    if @field.effects[PBEffects::Gravity]>0
      @field.effects[PBEffects::Gravity]-=1
      if @field.effects[PBEffects::Gravity]==0
        pbDisplay(_INTL("¡La Gravedad volvió a la normalidad!"))
        PBDebug.log("[Fin de efecto] Se terminó la gravedad intensa")
      end
    end
    # Espacio Raro  /  Trick Room
    if @field.effects[PBEffects::TrickRoom]>0
      @field.effects[PBEffects::TrickRoom]-=1
      if @field.effects[PBEffects::TrickRoom]==0
        pbDisplay(_INTL("¡Las dimensiones han vuelto a la normalidad!"))
        PBDebug.log("[Fin de efecto] Espacio Raro ha terminado")
      end
    end
    # Zona Extraña  /  Wonder Room
    if @field.effects[PBEffects::WonderRoom]>0
      @field.effects[PBEffects::WonderRoom]-=1
      if @field.effects[PBEffects::WonderRoom]==0
        pbDisplay(_INTL("¡Se ha acabado el efecto de Zona Extraña!"))
        PBDebug.log("[Fin de efecto] Zona Extraña ha terminado")
      end
    end
    # Zona Mágica  / Magic Room
    if @field.effects[PBEffects::MagicRoom]>0
      @field.effects[PBEffects::MagicRoom]-=1
      if @field.effects[PBEffects::MagicRoom]==0
        pbDisplay(_INTL("The area returned to normal."))
        PBDebug.log("[Fin de efecto] Zona Mágica ha terminado")
      end
    end
    # Mud Sport
    if @field.effects[PBEffects::MudSportField]>0
      @field.effects[PBEffects::MudSportField]-=1
      if @field.effects[PBEffects::MudSportField]==0
        pbDisplay(_INTL("The effects of Mud Sport have faded."))
        PBDebug.log("[Fin de efecto] Mud Sport ended")
      end
    end
    # Water Sport
    if @field.effects[PBEffects::WaterSportField]>0
      @field.effects[PBEffects::WaterSportField]-=1
      if @field.effects[PBEffects::WaterSportField]==0
        pbDisplay(_INTL("The effects of Water Sport have faded."))
        PBDebug.log("[Fin de efecto] Water Sport ended")
      end
    end
    # Electric Terrain
    if @field.effects[PBEffects::ElectricTerrain]>0
      @field.effects[PBEffects::ElectricTerrain]-=1
      if @field.effects[PBEffects::ElectricTerrain]==0
        pbDisplay(_INTL("¡La corriente eléctrica ha desaparecido del campo de batalla!"))
        @scene.pbDeleteField()
        PBDebug.log("[Fin de efecto] Electric Terrain ended")
      end
    end
    # Grassy Terrain (counting down)
    if @field.effects[PBEffects::GrassyTerrain]>0
      @field.effects[PBEffects::GrassyTerrain]-=1
      if @field.effects[PBEffects::GrassyTerrain]==0
        pbDisplay(_INTL("¡El campo de hierba ha desaparecido del campo de batalla!"))
        @scene.pbDeleteField()
        PBDebug.log("[Fin de efecto] Grassy Terrain ended")
      end
    end
    # Misty Terrain
    if @field.effects[PBEffects::MistyTerrain]>0
      @field.effects[PBEffects::MistyTerrain]-=1
      if @field.effects[PBEffects::MistyTerrain]==0
        pbDisplay(_INTL("¡La niebla se ha desvanecido del campo de batalla!"))
        @scene.pbDeleteField()
        PBDebug.log("[Fin de efecto] Misty Terrain ended")
      end
    end
    # Psychic Terrain
    if @field.effects[PBEffects::PsychicTerrain]>0
      @field.effects[PBEffects::PsychicTerrain]-=1
      if @field.effects[PBEffects::PsychicTerrain]==0
        pbDisplay(_INTL("¡La sensación extraña desapareció del campo de batalla!"))
        @scene.pbDeleteField()
        PBDebug.log("[End of effect] Psychic Terrain ended")
      end
    end
    # Alboroto  /  Uproar
    for i in priority
      next if i.isFainted?
      if i.effects[PBEffects::Uproar]>0
        for j in priority
          if !j.isFainted? && j.status==PBStatuses::SLEEP && !j.hasWorkingAbility(:SOUNDPROOF)
            PBDebug.log("[Efecto prolongado disparado] Alboroto ha despertado a #{j.pbThis(true)}")
            j.pbCureStatus(false)
            pbDisplay(_INTL("¡{1} se despertó por el Alboroto!",j.pbThis))
          end
        end
        i.effects[PBEffects::Uproar]-=1
        if i.effects[PBEffects::Uproar]==0
          pbDisplay(_INTL("{1} se tranquilizó.",i.pbThis))
          PBDebug.log("[Fin de efecto] #{i.pbThis} ya no está haciendo alboroto")
        else
          pbDisplay(_INTL("¡{1} está montando un Alboroto!",i.pbThis)) 
        end
      end
    end
    for i in priority
      next if i.isFainted?
      # Impulso  /  Speed Boost
      # A Pokémon's turncount is 0 if it became active after the beginning of a round
      if i.turncount>0 && i.hasWorkingAbility(:SPEEDBOOST)
        if i.pbIncreaseStatWithCause(PBStats::SPEED,1,i,PBAbilities.getName(i.ability))
          PBDebug.log("[Habilidad disparada] #{PBAbilities.getName(i.ability)} de #{i.pbThis}")
        end
      end
      # Bad Dreams
      if i.status==PBStatuses::SLEEP && !i.hasWorkingAbility(:MAGICGUARD)
        if i.pbOpposing1.hasWorkingAbility(:BADDREAMS) ||
           i.pbOpposing2.hasWorkingAbility(:BADDREAMS)
          PBDebug.log("[Habilidad disparada] Pesadilla de #{i.pbThis}")
          hploss=i.pbReduceHP((i.totalhp/6).floor,true)
          pbDisplay(_INTL("¡{1} sufre por el mal sueño!",i.pbThis)) if hploss>0
        end
      end
      # GRAN PESADILLA
      if i.status==PBStatuses::SLEEP && !i.hasWorkingAbility(:MAGICGUARD)
        if i.pbOpposing1.hasWorkingAbility(:GRANPESADILLA) ||
           i.pbOpposing2.hasWorkingAbility(:GRANPESADILLA)
          PBDebug.log("[Habilidad disparada] Pesadilla de #{i.pbThis}")
          hploss=i.pbReduceHP((i.totalhp/4).floor,true)
          pbDisplay(_INTL("¡{1} sufre una terrible pesadilla!",i.pbThis)) if hploss>0
        end
      end      
      if i.isFainted?
        return if !i.pbFaint
        next
      end
      # Recogida  /  Pickup
      if i.hasWorkingAbility(:PICKUP) && i.item<=0
        item=0; index=-1; use=0
        for j in 0...4
          next if j==i.index
          if @battlers[j].effects[PBEffects::PickupUse]>use
            item=@battlers[j].effects[PBEffects::PickupItem]
            index=j
            use=@battlers[j].effects[PBEffects::PickupUse]
          end
        end
        if item>0
          i.item=item
          @battlers[index].effects[PBEffects::PickupItem]=0
          @battlers[index].effects[PBEffects::PickupUse]=0
          @battlers[index].pokemon.itemRecycle=0 if @battlers[index].pokemon.itemRecycle==item
          if !@opponent && # In a wild battle
             i.pokemon.itemInitial==0 &&
             @battlers[index].pokemon.itemInitial==item
            i.pokemon.itemInitial=item
            @battlers[index].pokemon.itemInitial=0
          end
          pbDisplay(_INTL("¡{1} ha encontrado una {2}!",i.pbThis,PBItems.getName(item)))
          i.pbBerryCureCheck(true)
        end
      end
      # Cosecha  /  Harvest
      if i.hasWorkingAbility(:HARVEST) && i.item<=0 && i.pokemon.itemRecycle>0
        if pbIsBerry?(i.pokemon.itemRecycle) &&
           (pbWeather==PBWeather::SUNNYDAY || 
           pbWeather==PBWeather::HARSHSUN || pbRandom(10)<5)
          i.item=i.pokemon.itemRecycle
          i.pokemon.itemRecycle=0
          i.pokemon.itemInitial=item if i.pokemon.itemInitial==0
          pbDisplay(_INTL("¡{1} ha cosechado una {2}!",i.pbThis,PBItems.getName(i.item)))
          i.pbBerryCureCheck(true)
        end
      end
      # Veleta  /  Moody
      if i.hasWorkingAbility(:MOODY)
        randomup=[]; randomdown=[]
        for j in [PBStats::ATTACK,PBStats::DEFENSE,PBStats::SPEED,PBStats::SPATK,
                  PBStats::SPDEF,PBStats::ACCURACY,PBStats::EVASION]
          randomup.push(j) if i.pbCanIncreaseStatStage?(j,i)
          randomdown.push(j) if i.pbCanReduceStatStage?(j,i)
        end
        if randomup.length>0
          PBDebug.log("[Habilidad disparada] Veleta de #{i.pbThis} (suba caractarística)")
          r=pbRandom(randomup.length)
          i.pbIncreaseStatWithCause(randomup[r],2,i,PBAbilities.getName(i.ability))
          for j in 0...randomdown.length
            if randomdown[j]==randomup[r]
              randomdown[j]=nil; randomdown.compact!
              break
            end
          end
        end
        if randomdown.length>0
          PBDebug.log("[Habilidad disparada] Veleta de #{i.pbThis} (baja caractarística)")
          r=pbRandom(randomdown.length)
          i.pbReduceStatWithCause(randomdown[r],1,i,PBAbilities.getName(i.ability))
        end
      end
    end
    for i in priority
      next if i.isFainted?
      # Punzasfera
      if i.hasWorkingItem(:PUNZASFERA) && i.status==0 && i.pbCanHemorragia?(nil,false)
        PBDebug.log("[Objeto disparado] Toxisfera de #{i.pbThis}")
        i.pbHemorragia(nil,_INTL("¡{1} empieza a sangrar por la {2}!",i.pbThis,
           PBItems.getName(i.item)))
      end      
      # Toxisfera  /  Toxic Orb
      if i.hasWorkingItem(:TOXICORB) && i.status==0 && i.pbCanPoison?(nil,false)
        PBDebug.log("[Objeto disparado] Toxisfera de #{i.pbThis}")
        i.pbPoison(nil,_INTL("¡{1} ha sido gravemente envenenado por la {2}!",i.pbThis,
           PBItems.getName(i.item)),true)
      end
      # Llamasfera  /  Flame Orb
      if i.hasWorkingItem(:FLAMEORB) && i.status==0 && i.pbCanBurn?(nil,false)
        PBDebug.log("[Objeto disparado] Llamasfera de #{i.pbThis}")
        i.pbBurn(nil,_INTL("¡{1} ha sido quemado por la {2}!",i.pbThis,PBItems.getName(i.item)))
      end
      # Toxiestrella  /  Sticky Barb
      if i.hasWorkingItem(:STICKYBARB) && !i.hasWorkingAbility(:MAGICGUARD)
        PBDebug.log("[Objeto disparado] Toxiestrella de #{i.pbThis}")
        @scene.pbDamageAnimation(i,0)
        pbDisplay(_INTL("¡{1} ha sido dañado por la {2}!",i.pbThis,PBItems.getName(i.item)))
        i.pbReduceHP((i.totalhp/8).floor)
      end
      if i.isFainted?
        return if !i.pbFaint
      end
    end
    # Revisión de formas
    for i in 0...4
      next if @battlers[i].isFainted?
      @battlers[i].pbCheckForm
    end
    pbGainEXP
    pbSwitch
    return if @decision>0
    for i in priority
      next if i.isFainted?
      i.pbAbilitiesOnSwitchIn(false)
    end
    # Healing Wish/Lunar Dance - should go here
    # Spikes/Toxic Spikes/Stealth Rock - should go here (in order of their 1st use)
    for i in 0...4
      if @battlers[i].turncount>0 && @battlers[i].hasWorkingAbility(:TRUANT)
        @battlers[i].effects[PBEffects::Truant]=!@battlers[i].effects[PBEffects::Truant]
      end
      if @battlers[i].effects[PBEffects::LockOn]>0   # Also Mind Reader
        @battlers[i].effects[PBEffects::LockOn]-=1
        @battlers[i].effects[PBEffects::LockOnPos]=-1 if @battlers[i].effects[PBEffects::LockOn]==0
      end
      @battlers[i].effects[PBEffects::Flinch]=false
      @battlers[i].effects[PBEffects::FollowMe]=0
      @battlers[i].effects[PBEffects::HelpingHand]=false
      @battlers[i].effects[PBEffects::MagicCoat]=false
      @battlers[i].effects[PBEffects::Snatch]=false
      @battlers[i].effects[PBEffects::Charge]-=1 if @battlers[i].effects[PBEffects::Charge]>0
      @battlers[i].lastHPLost=0
      @battlers[i].tookDamage=false
      @battlers[i].lastAttacker.clear
      @battlers[i].effects[PBEffects::Counter]=-1
      @battlers[i].effects[PBEffects::CounterTarget]=-1
      @battlers[i].effects[PBEffects::MirrorCoat]=-1
      @battlers[i].effects[PBEffects::MirrorCoatTarget]=-1
    end
    for i in 0...2
      if !@sides[i].effects[PBEffects::EchoedVoiceUsed]
        @sides[i].effects[PBEffects::EchoedVoiceCounter]=0
      end
      @sides[i].effects[PBEffects::EchoedVoiceUsed]=false
      @sides[i].effects[PBEffects::QuickGuard]=false
      @sides[i].effects[PBEffects::WideGuard]=false
      @sides[i].effects[PBEffects::CraftyShield]=false
      @sides[i].effects[PBEffects::Round]=0
    end
    @field.effects[PBEffects::FusionBolt]=false
    @field.effects[PBEffects::FusionFlare]=false
    @field.effects[PBEffects::IonDeluge]=false
    @field.effects[PBEffects::FairyLock]-=1 if @field.effects[PBEffects::FairyLock]>0
    # invalidate stored priority
    @usepriority=false
  end
end
