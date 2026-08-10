# 배틀 처리 순서 전수 감사 (2026-08-10)

유지자 제보 셋에서 출발했다. ① 독·화상 같은 상태이상과 먹밥에서 체력이 먼저 깎이고
연출이 나중에 나온다. ② 더블배틀에서 등장하자마자 트릭룸을 까는 파라섹트가 나와도
그 턴은 여전히 빠른 순으로 행동한다. ③ 접촉기로 마비를 걸었는데 마비가 안 걸린 것처럼
상대가 그대로 움직인다.

셋 다 실물 코드에서 원인을 확정했고, ②와 ③은 같은 뿌리였다. 감사 범위를 제보 밖으로
넓혀 라운드 종료 순서 전체와 등장 특성 발동 순서까지 본가와 대조했다.

읽은 것: 게임 설치본(`/mnt/d/Game/Pokemon Z/V2.18`)의 `Data/Scripts.rxdata` 272개 섹션
전부를 풀어서 `PokeBattle_Battle`(4,553줄) · `PokeBattle_Battler`(3,921줄) ·
`PokeBattle_BattlerEffects`(1,211줄) · `PokeBattle_Scene`을 직접 읽었다. 순정 백업
`Scripts.rxdata.orig`도 함께 풀어 대조했다. 아래 줄 번호는 전부 그 덤프 기준이다.

푸는 법(재현): essentials-modkit의 `modkit.scripts.sources(<게임 폴더>)`가 (섹션 이름,
소스)를 내놓는다. `.orig`는 파일 이름이 달라 그대로는 안 읽히니 임시 폴더의
`Data/Scripts.rxdata`로 복사해서 읽는다.

## 확정한 결함 넷

### ① 행동 순서가 턴 시작에 고정된다 — 실측

`pbAttackPhase`(085:3141)가 3153–3154에서 순서를 한 번 계산하고 지역 변수에 담는다.

    @usepriority=false
    priority=pbPriority(false,true)

`pbPriority`(085:1154)는 첫 줄이 `return @priority if @usepriority`이고 마지막에
`@usepriority=true`를 세운다. 즉 한 라운드에 한 번만 계산된다.

그 뒤에 도는 것들이 순서를 바꿀 수 있는데 반영될 자리가 없다. 교체 처리는 3200 언저리,
교체로 들어온 포켓몬의 등장 특성(`pbAbilitiesOnSwitchIn`)은 3245 언저리다. 기술 사용
루프(`10.times do`)는 그다음이다. 마비도 같다 — 마비를 거는 `pbParalyze`
(082:396)는 즉시 상태를 세우지만, 스피드를 다시 읽는 곳이 그 라운드에 없다.

스피드 자체는 `pbSpeed`(081:699)가 마비를 반영한다(081:841, ¼로 감소). 읽는 시점이
문제이지 계산이 틀린 게 아니다.

### ② 파라섹트의 트릭룸은 커스텀 특성이다 — 실측

기술이 아니라 이 팬게임 고유 특성 `PRESENCIARARA`다(081:1238–1245). `onactive` 조건
안에 있어 등장 시 발동하고 `@battle.field.effects[PBEffects::TrickRoom]=5`를 세운다.
발동 자리가 ①의 순서 계산 뒤라서 그 턴에 안 먹힌다.

    grep -n "PRESENCIARARA" <덤프>/081_PokeBattle_Battler.rb

### ③ 라운드 종료가 「연출 → 체력 → 메시지」다 — 실측

독은 `pbReduceHP`를 먼저 부르고(085:3766–3778) 연출·메시지를 내는 `pbContinueStatus`를
그다음에 부른다(085:3779). 화상(3794)·얼음(3803)도 같다. `pbContinueStatus`(082:479)가
`pbCommonAnimation` 다음 `pbDisplay`를 부르는 자리다.

모래바람은 피격 연출은 앞에 있는데(085:3405) 메시지가 체력 감소 뒤다(3406–3407).
먹밥도 아이템 연출은 앞, 메시지는 뒤다(081:2364–2366).

**순정 백업과 이 구간들은 한 글자도 다르지 않다.** 섹션 전체 diff가 여덟 줄뿐이고
(포획 문구 하나, 날씨 종료 문구 셋의 한글 박음), 라운드 종료 함수와 공격 페이즈 안에는
없다. 우리 한글패치나 배속 모드가 만든 문제가 아니라는 뜻이다.

    diff <(순정 섹션) <(설치본 섹션)   # 8줄

어긋남이 유난히 눈에 띄는 이유는 따로 있다. 이 게임은 체력 변화를 그리는
`pbHPChanged`(088:2741)를 다시 짜서, **인자로 받은 「애니메이션 없이」를 아예 무시하고**
언제나 체력바를 흘리고 데미지 숫자를 띄운다. 순정이라면 조용히 지나갔을 자리가 전부
눈에 띄는 연출이 됐다.

### ④ 선제의발톱 메시지가 턴 머리에 몰려 나온다 — 실측

`pbPriority` 안에서 판정과 동시에 표시한다(085:1180–1190). 그 시점은 아무도 행동하기
전이다. 본가는 그 포켓몬이 움직일 때 나온다. 엔진 원저자도 알고 있었다 — 기술 사용
함수에 `# TODO: Quick Claw message` 주석만 남아 있다(081:3466).

구애열매(Custap)는 같은 자리에서 소비까지 한다(`pbConsumeItem`). 소비 시점은 본가도
턴 시작이라 그대로 둔다.

## 정상이라 확인한 것

**접촉 특성은 즉시 발동한다.** 정전기·불꽃몸·독가시·포자·까칠한피부·바늘몸은 전부
`pbEffectsOnDealingDamage`(081:1520~)에 모여 있고, 이 메서드는 기술이 한 대 맞힐 때마다
`pbProcessMoveAgainstTarget` 안에서 불린다(081:3264). 큐에 쌓아 두는 구조는 없다.
제보 ③은 이 자리가 아니라 결함 ①이 원인이었다(유지자 확인 2026-08-10).

**기절 후 교체 투입은 라운드 끝에 일어난다**(085:4357에서 `pbSwitch`). 5세대 이후
본가와 같다.

**전투 시작 시 등장 특성은 스피드 순으로 돈다**(`pbOnActiveAll`, 085:2462에서
`pbPriority`를 부른 순서로 순회).

**라운드 종료의 항목 순서는 대체로 본가와 맞는다.** Bulbapedia의 6세대 정본 순서와
견줘 날씨 감소 → 미래예지 → 소원 → 아쿠아링 → 뿌리박기 → 씨뿌리기 → 독 → 화상 →
저주 → 조이기 → 각종 지속효과 감소가 같은 자리에 있다. 어긋난 것은 하나 —
비의은혜·건조피부·아이스바디 같은 날씨 연동 회복 특성이 본가에서는 날씨 데미지와 한
묶음(2번)인데 이 게임은 미래예지 뒤(085:3572~)다. 실전 영향이 거의 없어 그대로 둔다.

## 본가 기준 — 무엇을 정답으로 삼았나

유지자 판정: **가능한 한 최신 세대를 따른다.** 챔피언스의 굵직한 변화를 전부 들여올
필요는 없지만 매커니즘은 최신 쪽을 존중한다(2026-08-10).

- 턴 도중 순서 재계산은 **8세대에 들어왔다.** Bulbapedia Priority 문서: "Starting in
  Generation VIII, in-battle changes to a move's priority immediately take effect,
  allowing the Pokémon to use the move in the proper priority bracket or, if the
  priority bracket has already passed, immediately."
  (https://bulbapedia.bulbagarden.net/wiki/Priority · 복수 확인)
- 무엇을 다시 정렬하는가: Pokémon Showdown이 8세대용으로 넣은 동적 스피드 갱신
  PR이 "speeds are updated after each action in the queue completes"라고 적고, 검증한
  상호작용 목록에 After You + Trick Room, 스위치로 바뀐 날씨 + 쓱쓱이 들어 있다.
  (https://github.com/smogon/pokemon-showdown/pull/6100 · 웹 1소스)
- 트릭룸은 우선도 브래킷을 바꾸지 않는다. 같은 브래킷 안의 스피드 순서만 뒤집는다.
  (Bulbapedia Priority · Trick Room)
- 라운드 종료 순서의 **최신 세대 정본 표는 못 찾았다 — 미확인.** Bulbapedia의 해당
  문서(User:SnorlaxMonster/End-turn resolution order)는 6세대까지만 정리돼 있고 2017년
  이후 갱신이 없다. 위의 대조는 그 6세대 표 기준이다.

## 판정과 반영

판정은 [품질 원장](../../ledger/quality.md)의 「배틀 처리 순서는 최신 세대를 따른다」 절.
반영은 모드 `Battle Order`(티켓 Z-41)이고, 무엇을 어디서 떠 와 어디를 바꿨는지는
[모드 폴더의 README](../../../mods/Battle%20Order/README.md)가 정본이다.

건드리지 않기로 한 것 셋(유지자 판정 2026-08-10): 마비의 스피드 감소 배율(이 게임 ¼,
7세대 이후 본가 ½ — 밸런스 변경이라 지금 건드릴 자리가 아니다) · 날씨 연동 회복 특성의
위치 · 싸라기눈 데미지가 `if false`로 꺼져 있는 것(085:3424. 9세대에서 눈이 데미지를
주지 않으니 최신 기준으로는 오히려 맞는 결과다).

## 곁에서 발견한 것 — pbSpeed에 부수효과가 있다

`pbSpeed`(081:699~852) 안에 커스텀 특성 `TINTINEO` 분기가 있고, 등장 턴에 **아군 전원의
상태이상을 치료하고 메시지를 띄운다**(081:738–790). 값을 읽는 함수가 게임 상태를 바꾼다.

지금도 순서 계산과 AI 판단에서 여러 번 불리므로 이미 여러 번 발동하고 있을 것으로
보이나(추정 — 실제로 발동하는 표본을 잡아 확인하지 않았다), 순서 재계산을 넣으면 그
횟수가 늘어난다. `Battle Order` 모드는 재계산 동안만 등장 턴 판정을 피하는 우회를
넣었고, 근본 수술은 티켓 Z-42로 뒀다.

## 모드를 다시 뜨는 법

게임 판이 올라 원본 메서드가 달라지면 이 모드는 옛 코드를 덮어씌우는 모드가 된다.
새 판에서 다시 뜨는 절차는 이렇다.

1. 새 설치본의 섹션을 풀어 네 메서드의 줄 범위를 다시 잡는다(README의 표).
2. 그 범위를 그대로 떠서, README의 「바꾼 자리」 표에 적힌 치환만 다시 적용한다.
   치환은 **정확히 한 번** 일치해야 한다 — 0번이나 2번이면 원본이 달라진 것이니 멈추고
   무엇이 달라졌는지부터 본다.
3. `mod.json`의 `expects`를 새 순정 백업(`Scripts.rxdata.orig`)의 섹션 md5로 갱신한다.
4. `share/qa-ruby-compat.py`의 패턴 층으로 신형 루비 지뢰 0을 확인한다.
5. mkxp-z 시험대에서 실제로 띄워 본다. 문법 오류는 부팅에서 바로 드러난다.

## 이 문서의 근거 diff

아래는 원본 메서드와 모드 파일의 차이 전문이다. 이것 말고 바뀐 줄은 없다.

```diff
--- pbAttackPhase (원본)
+++ 001_TurnOrder.rb
@@ -144,4 +144,7 @@
     end
     10.times do
+      # [Battle Order] 남은 순서를 다시 정렬한다(8세대 이후 본가 방식). 교체로 들어온
+      # 포켓몬의 등장 특성(트릭룸·날씨)과 방금 걸린 마비가 여기서 반영된다.
+      bo_resortPriority
       # Forced to go next
       advance=false
@@ -149,4 +152,5 @@
         next if !i.effects[PBEffects::MoveNext]
         next if i.hasMovedThisRound? || i.effects[PBEffects::SkipTurn]
+        bo_showQuickClaw(i)
         advance=i.pbProcessTurn(@choices[i.index])
         break if advance
@@ -158,4 +162,5 @@
         next if i.effects[PBEffects::Quash]
         next if i.hasMovedThisRound? || i.effects[PBEffects::SkipTurn]
+        bo_showQuickClaw(i)
         advance=i.pbProcessTurn(@choices[i.index])
         break if advance
@@ -167,4 +172,5 @@
         next if !i.effects[PBEffects::Quash]
         next if i.hasMovedThisRound? || i.effects[PBEffects::SkipTurn]
+        bo_showQuickClaw(i)
         advance=i.pbProcessTurn(@choices[i.index])
         break if advance
@@ -183,2 +189,4 @@
     pbWait(20)
   end
+end
+

--- pbEndOfRoundPhase (원본)
+++ 002_EndOfRound.rb
@@ -35,6 +35,6 @@
               PBDebug.log("[Habilidad disparada] Poder Solar de #{i.pbThis}")
               @scene.pbDamageAnimation(i,0)
+              pbDisplay(_INTL("¡{1} perdió algunos PS debido al Poder Solar!",i.pbThis))
               i.pbReduceHP((i.totalhp/8).floor)
-              pbDisplay(_INTL("¡{1} perdió algunos PS debido al Poder Solar!",i.pbThis))
               if i.isFainted?
                 return if !i.pbFaint
@@ -76,6 +76,6 @@
                ![0xCA,0xCB].include?(PBMoveData.new(i.effects[PBEffects::TwoTurnAttack]).function) # Dig, Dive
               @scene.pbDamageAnimation(i,0)
+              pbDisplay(_INTL("¡La tormenta de arena zarandea a {1}!",i.pbThis))
               i.pbReduceHP((i.totalhp/16).floor)
-              pbDisplay(_INTL("¡La tormenta de arena zarandea a {1}!",i.pbThis))
               if i.isFainted?
                 return if !i.pbFaint
@@ -147,6 +147,6 @@
               PBDebug.log("[Habilidad disparada] Poder Solar de #{i.pbThis}")
               @scene.pbDamageAnimation(i,0)
+              pbDisplay(_INTL("¡{1} ha sido dañado por la luz solar!",i.pbThis))
               i.pbReduceHP((i.totalhp/8).floor)
-              pbDisplay(_INTL("¡{1} ha sido dañado por la luz solar!",i.pbThis))
               if i.isFainted?
                 return if !i.pbFaint
@@ -188,6 +188,6 @@
             if !i.isShadow?
               @scene.pbDamageAnimation(i,0)
+              pbDisplay(_INTL("¡{1} ha sido dañado por el cielo oscuro!",i.pbThis))
               i.pbReduceHP((i.totalhp/16).floor)
-              pbDisplay(_INTL("¡{1} ha sido dañado por el cielo oscuro!",i.pbThis))
               if i.isFainted?
                 return if !i.pbFaint
@@ -436,4 +436,5 @@
           if !i.hasWorkingAbility(:MAGICGUARD)             # Muro Mágico
             PBDebug.log("[Daño por estado] #{i.pbThis} recibió daño por el veneno/tóxico")
+            i.pbContinueStatus
             if i.statusCount==0
               if i.pbOpposing1.hasWorkingAbility(:ALQUIMIAVIL) || i.pbOpposing2.hasWorkingAbility(:ALQUIMIAVIL)
@@ -449,5 +450,4 @@
               end
             end
-            i.pbContinueStatus
           end
         end
@@ -455,4 +455,5 @@
       # Quemadura  /  Burn
       if i.status==PBStatuses::BURN
+        i.pbContinueStatus
         if !i.hasWorkingAbility(:MAGICGUARD)               # Muro Mágico
           PBDebug.log("[Daño por estado] #{i.pbThis} recibió daño por la quemadura")
@@ -464,14 +465,13 @@
           end
         end
-        i.pbContinueStatus
       end
       
       # Congelación Arceus
       if i.status==PBStatuses::FROZEN
+        i.pbContinueStatus
         if !i.hasWorkingAbility(:MAGICGUARD)               # Muro Mágico
           PBDebug.log("[Daño por estado] #{i.pbThis} recibió daño por congelación")
           i.pbReduceHP((i.totalhp/16).floor)
         end
-        i.pbContinueStatus
       end
       
@@ -494,6 +494,6 @@
           if !i.hasWorkingAbility(:MAGICGUARD)
             PBDebug.log("[Efecto prolongado disparado] Pesadilla de #{i.pbThis}")
+            pbDisplay(_INTL("¡{1} está inmerso en una Pesadilla!",i.pbThis))
             i.pbReduceHP((i.totalhp/4).floor,true)
-            pbDisplay(_INTL("¡{1} está inmerso en una Pesadilla!",i.pbThis))
           end
         else
@@ -511,6 +511,6 @@
       if i.effects[PBEffects::Curse] && !i.hasWorkingAbility(:MAGICGUARD)
         PBDebug.log("[Efecto prolongado disparado] Maldición de #{i.pbThis}")
+        pbDisplay(_INTL("¡{1} es víctima de una Maldición!",i.pbThis))
         i.pbReduceHP((i.totalhp/4).floor,true)
-        pbDisplay(_INTL("¡{1} es víctima de una Maldición!",i.pbThis))
       end
       if i.isFainted?
@@ -556,6 +556,6 @@
         amt= (i.totalhp/4).floor 
       end               
+            pbDisplay(_INTL("¡{1} ha sido dañado por {2}!",i.pbThis,movename))
             i.pbReduceHP(amt)
-            pbDisplay(_INTL("¡{1} ha sido dañado por {2}!",i.pbThis,movename))
           end
         end
@@ -1014,6 +1014,6 @@
         PBDebug.log("[Objeto disparado] Toxiestrella de #{i.pbThis}")
         @scene.pbDamageAnimation(i,0)
+        pbDisplay(_INTL("¡{1} ha sido dañado por la {2}!",i.pbThis,PBItems.getName(i.item)))
         i.pbReduceHP((i.totalhp/8).floor)
-        pbDisplay(_INTL("¡{1} ha sido dañado por la {2}!",i.pbThis,PBItems.getName(i.item)))
       end
       if i.isFainted?

--- pbBerryCureCheck (원본)
+++ 003_Leftovers.rb
@@ -115,6 +115,6 @@
       PBDebug.log("[Objeto disparado] Restos de #{pbThis}")
       @battle.pbCommonAnimation("UseItem",self,nil)
+      @battle.pbDisplay(_INTL("¡{1} ha restaurado un poco sus PS con {2}!",pbThis,itemname))
       pbRecoverHP((self.totalhp/16).floor,true)
-      @battle.pbDisplay(_INTL("¡{1} ha restaurado un poco sus PS con {2}!",pbThis,itemname))
     end
     if hpcure && self.hasWorkingItem(:BLACKSLUDGE)                                  # Lodo Negro
@@ -124,12 +124,12 @@
           PBDebug.log("[Objeto disparado] Lodo Negro de #{pbThis} (cura)")          # Lodo Negro
           @battle.pbCommonAnimation("UseItem",self,nil)
+          @battle.pbDisplay(_INTL("¡{1} ha restaurado un poco sus PS con {2}!",pbThis,itemname))
           pbRecoverHP((self.totalhp/16).floor,true)
-          @battle.pbDisplay(_INTL("¡{1} ha restaurado un poco sus PS con {2}!",pbThis,itemname))
         end
       elsif !self.hasWorkingAbility(:MAGICGUARD)
         PBDebug.log("[Objeto disparado] Lodo Negro de #{pbThis} (daño)")            # Lodo Negro
         @battle.pbCommonAnimation("UseItem",self,nil)
+        @battle.pbDisplay(_INTL("¡{1} ha sido herido por {2}!",pbThis,itemname))
         pbReduceHP((self.totalhp/8).floor,true)
-        @battle.pbDisplay(_INTL("¡{1} ha sido herido por {2}!",pbThis,itemname))
       end
       pbFaint if self.isFainted?

```

`pbPriority`는 구조를 갈라 diff가 길어져 싣지 않는다 — 바꾼 것은 README의 표 넷 줄이고,
정렬 코드 자체(`bo_sortPriority`로 뗀 부분)는 원본 그대로다.
