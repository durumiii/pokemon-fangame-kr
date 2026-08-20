# Battle Order — 먹밥·검은먹밥 (Pokemon Z v2.18 · Essentials v16 · 루비 1.8.7)
#
# 원본 `pbBerryCureCheck`를 그대로 떠 와서, 먹밥과 검은먹밥 세 자리에서만 메시지를
# 체력 변화 앞으로 옮겼다. 셋 다 메시지가 조건 없이 나오는 자리라 순서만 바뀐다.
# 열매 회복은 손대지 않았다 — 그쪽은 메시지가 실제 회복량에 걸려 있어 순서를 바꾸려면
# 회복량을 미리 계산해야 한다(AGENTS.md 「손대지 않은 자리」).

class PokeBattle_Battler
  def pbBerryCureCheck(hpcure=false)
    return if self.isFainted?
    unnerver=(pbOpposing1.hasWorkingAbility(:UNNERVE) ||
              pbOpposing2.hasWorkingAbility(:UNNERVE))
    itemname=(self.item==0) ? "" : PBItems.getName(self.item)
    if hpcure
      if self.hasWorkingItem(:BERRYJUICE) && self.hp<=(self.totalhp/2).floor   # Zumo de Baya
        amt=self.pbRecoverHP(20,true)
        if amt>0
          @battle.pbCommonAnimation("UseItem",self,nil)
          @battle.pbDisplay(_INTL("¡{1} ha restaurado su salud gracias a la {2}!",pbThis,itemname))
          pbConsumeItem
          return
        end
      end
    end
    if !unnerver
      if hpcure 
        if self.hp<=(self.totalhp/2).floor
          if self.hasWorkingItem(:ORANBERRY) ||
             self.hasWorkingItem(:SITRUSBERRY)
            pbActivateBerryEffect
            return
          end
          if self.hasWorkingItem(:FIGYBERRY) ||
             self.hasWorkingItem(:WIKIBERRY) ||
             self.hasWorkingItem(:MAGOBERRY) ||
             self.hasWorkingItem(:AGUAVBERRY) ||
             self.hasWorkingItem(:IAPAPABERRY)
            pbActivateBerryEffect
            return
          end
        end
      end
        if (self.hasWorkingAbility(:GLUTTONY) && self.hp<=(self.totalhp/2).floor) ||
           self.hp<=(self.totalhp/4).floor
          if self.hasWorkingItem(:LIECHIBERRY) ||
             self.hasWorkingItem(:GANLONBERRY) ||
             self.hasWorkingItem(:SALACBERRY) ||
             self.hasWorkingItem(:PETAYABERRY) ||
             self.hasWorkingItem(:APICOTBERRY)
            pbActivateBerryEffect
            return
          end
          if self.hasWorkingItem(:LANSATBERRY) ||
             self.hasWorkingItem(:STARFBERRY)
            pbActivateBerryEffect
            return
          end
          if self.hasWorkingItem(:MICLEBERRY)
            pbActivateBerryEffect
            return
          end
        end
        if self.hasWorkingItem(:LEPPABERRY)
          pbActivateBerryEffect
          return
        end
      if self.hasWorkingItem(:CHESTOBERRY) ||
         self.hasWorkingItem(:PECHABERRY) ||
         self.hasWorkingItem(:RAWSTBERRY) ||
         self.hasWorkingItem(:CHERIBERRY) ||
         self.hasWorkingItem(:ASPEARBERRY) ||
         self.hasWorkingItem(:PERSIMBERRY) ||
         self.hasWorkingItem(:LUMBERRY)
        pbActivateBerryEffect
        return
      end
    end
    if self.hasWorkingItem(:WHITEHERB)
      reducedstats=false
      for i in [PBStats::ATTACK,PBStats::DEFENSE,
                PBStats::SPEED,PBStats::SPATK,PBStats::SPDEF,
                PBStats::ACCURACY,PBStats::EVASION]
        if @stages[i]<0
          @stages[i]=0; reducedstats=true
        end
      end
      if reducedstats
        PBDebug.log("[Objeto disparado] #{itemname} de #{pbThis}")
        @battle.pbCommonAnimation("UseItem",self,nil)
        @battle.pbDisplay(_INTL("¡{1} ha restaurado su estado gracias a la {2}!",pbThis,itemname))
        pbConsumeItem
        return
      end
    end
    if self.hasWorkingItem(:MENTALHERB) &&              # Hierba Mental
       (@effects[PBEffects::Attract]>=0 ||
       @effects[PBEffects::Taunt]>0 ||
       @effects[PBEffects::Encore]>0 ||
       @effects[PBEffects::Torment] ||
       @effects[PBEffects::Disable]>0 ||
       @effects[PBEffects::HealBlock]>0)
      PBDebug.log("[Objeto disparado] #{itemname} de #{pbThis}")
      @battle.pbCommonAnimation("UseItem",self,nil)
      @battle.pbDisplay(_INTL("¡{1} se le pasó el enamoramiento usando {2}!",pbThis,itemname)) if @effects[PBEffects::Attract]>=0    # Enamoramiento
      @battle.pbDisplay(_INTL("¡El efecto de Mofa de {1} ha pasado!",pbThis)) if @effects[PBEffects::Taunt]>0                        # Mofa
      @battle.pbDisplay(_INTL("¡{1} se liberó de Repetición!",pbThis)) if @effects[PBEffects::Encore]>0                              # Repetición
      @battle.pbDisplay(_INTL("¡El efecto de Tormento de {1} ha pasado!",pbThis)) if @effects[PBEffects::Torment]                    # Tormento
      @battle.pbDisplay(_INTL("¡{1} se ha liberado de la anulación!",pbThis)) if @effects[PBEffects::Disable]>0                      # Anulación
      @battle.pbDisplay(_INTL("¡Anticura de {1} se agotó!",pbThis)) if @effects[PBEffects::HealBlock]>0                              # Anticura
      self.pbCureAttract
      @effects[PBEffects::Taunt]=0
      @effects[PBEffects::Encore]=0
      @effects[PBEffects::EncoreMove]=0
      @effects[PBEffects::EncoreIndex]=0
      @effects[PBEffects::Torment]=false
      @effects[PBEffects::Disable]=0
      @effects[PBEffects::HealBlock]=0
      pbConsumeItem
      return
    end
    if hpcure && self.hasWorkingItem(:LEFTOVERS) && self.hp!=self.totalhp &&        # Restos 
       @effects[PBEffects::HealBlock]==0
      PBDebug.log("[Objeto disparado] Restos de #{pbThis}")
      @battle.pbCommonAnimation("UseItem",self,nil)
      @battle.pbDisplay(_INTL("¡{1} ha restaurado un poco sus PS con {2}!",pbThis,itemname))
      pbRecoverHP((self.totalhp/16).floor,true)
    end
    if hpcure && self.hasWorkingItem(:BLACKSLUDGE)                                  # Lodo Negro
      if pbHasType?(:POISON)
        if self.hp!=self.totalhp &&
           (!USENEWBATTLEMECHANICS || @effects[PBEffects::HealBlock]==0)
          PBDebug.log("[Objeto disparado] Lodo Negro de #{pbThis} (cura)")          # Lodo Negro
          @battle.pbCommonAnimation("UseItem",self,nil)
          @battle.pbDisplay(_INTL("¡{1} ha restaurado un poco sus PS con {2}!",pbThis,itemname))
          pbRecoverHP((self.totalhp/16).floor,true)
        end
      elsif !self.hasWorkingAbility(:MAGICGUARD)
        PBDebug.log("[Objeto disparado] Lodo Negro de #{pbThis} (daño)")            # Lodo Negro
        @battle.pbCommonAnimation("UseItem",self,nil)
        @battle.pbDisplay(_INTL("¡{1} ha sido herido por {2}!",pbThis,itemname))
        pbReduceHP((self.totalhp/8).floor,true)
      end
      pbFaint if self.isFainted?
    end
  end
end
