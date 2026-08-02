# 한국 포켓몬 배틀 표현집

Pokemon Z(스페인어, Essentials v16) 한글화에서 배틀 시스템 메시지를 **새로 짓지 않고**
한국 포켓몬이 전통적으로 쓰는 표현으로 맞추기 위한 대조 재료.

## 수집 방법

두 소스에서 뽑았고, 셋째 소스(웹)는 쓰지 않았다 — 앞의 둘로 필요한 자리가 다 찼다.

**소스 A — pokeemerald-kr** (공식 3세대 한국어 텍스트의 소스 레벨 이식).
`git clone --depth 1 https://github.com/poketony/pokeemerald-kr`,
배틀 문자열은 전부 `src/battle_message.c`(3,192줄, 한글 포함 512줄)에 있다.
표의 출처 칸은 그 파일의 줄 번호다.

**소스 B — Pokémon Wishing Star v1.0.7** (같은 Essentials 엔진의 한국어 번역본).
배틀 메시지는 `Data/Scripts.rxdata`가 아니라 **번역 테이블**에 있다 —
`Data/messages_1_core.dat`의 Ruby Marshal 배열, 인덱스 24가 `ScriptTexts`(영문 원문 → 한국어) 사전이다.
스크립트 파일 403개에는 한글이 **0줄**이라 그쪽을 뒤지면 안 나온다.
재현:

```
uv run --with rubymarshal python -c "
from rubymarshal.reader import load
d = load(open('/mnt/d/Game/Pokemon Wishing Star/v1.0.7/Data/messages_1_core.dat','rb'))
print(d[24]['A critical hit!'])"
```

표의 출처 칸 `WS core[24]`는 그 사전을 뜻하고, 조회 키는 표에 적힌 **영문 원문**이다.
게임 고유 메시지는 `messages_1_game.dat` 인덱스 24에 따로 있다(`WS game[24]`).
한글이 붙은 문자열은 두 파일 합쳐 13,377쌍이고, 그중 배틀 관련으로 추린 것이 이 문서다.

## 플레이스홀더와 조사 처리 — 이게 제일 중요하다

두 소스 다 **조사를 자동으로 고르는 토큰**을 쓴다. 한글화할 때 이 장치부터 정해야 한다.

| 소스 | 이름 자리 | 조사 토큰 |
|---|---|---|
| pokeemerald-kr | `{B_ATK_NAME_WITH_PREFIX}`, `{B_DEF_NAME_WITH_PREFIX}`, `{B_BUFF1}` | `{B_TXT_EUNNEUN}`(은/는) · `{B_TXT_EULREUL}`(을/를) · `{B_TXT_IGA}`(이/가) · `{B_TXT_EU}`(으로/로) · `{B_TXT_WAGWA}`(과/와) |
| Wishing Star (Essentials) | `{1}` `{2}` `{3}` | `\j[은,는]` · `\j[을,를]` · `\j[이,가]` · `\j[으로,로]` · `\j[과,와]` · `\j[으로부터,로부터]` |

Essentials 쪽 `\j[…]`는 앞 글자 받침을 보고 고르는 플러그인 문법이라 **Z에 그대로 이식하려면 그 플러그인이 있어야 한다.**
없으면 「○○은(는)」 병기로 떨어뜨리는 수밖에 없다.

아래 표에서는 이름 자리를 전부 **○○**(첫째)·**△△**(둘째)·**□□**(셋째)로 통일했다.
조사는 받침 있는 이름 기준(은/를/이/으로)으로 적었다.

## 한계

- pokeemerald-kr은 **3세대** 텍스트다. 4세대 이후 공식판에서 문구가 바뀐 자리가 있다(아래 「갈리는 자리」).
- Wishing Star 번역은 **공식이 아니라 팬 번역**이다. 다만 Essentials 메시지 자리와 1:1이라 이식 대응표로는 이쪽이 직접적이다.
- 두 소스 다 「데미지」로 적는다. 현행 공식 표기는 「대미지」다 — 어느 쪽으로 갈지 정해야 한다.
- 특성·기술 이름은 표에 거의 안 넣었다. 그건 게임 데이터에서 조인할 일이지 여기서 옮겨 적을 일이 아니다.

---

## 1. 상태이상 — 걸림 / 지속 피해 / 회복

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 독 걸림 | ○○의 몸에 독이 퍼졌다! | WS core[24] `{1} was poisoned!` |
| 맹독 걸림 | ○○의 몸에 맹독이 퍼졌다! | WS core[24] `{1} was badly poisoned!` |
| 독 피해 | ○○은 독에 의한 데미지를 입었다! | WS core[24] `{1} was hurt by poison!` |
| 독 피해(3세대) | ○○은 독에 의한 데미지를 입고 있다! | battle_message.c:95 |
| 독 해제 | ○○의 독이 말끔히 해독되었다. | WS core[24] `{1} was cured of its poisoning.` |
| 화상 걸림 | ○○은 화상에 걸렸다! | WS core[24] `{1} was burned!` |
| 화상 걸림(3세대) | ○○은 화상을 입었다! | battle_message.c:99 |
| 화상 피해 | ○○은 화상에 의한 데미지를 입었다! | WS core[24] `{1} was hurt by its burn!` |
| 화상 피해(3세대) | ○○은 화상 데미지를 입고 있다! | battle_message.c:101 |
| 화상 치료 | ○○의 화상이 치료됐다. | WS core[24] `{1}'s burn was healed.` |
| 마비 걸림 | ○○은 마비되어 기술이 나오기 어려워졌다! | WS core[24] `{1} is paralyzed! It may be unable to move!` / battle_message.c:109 (동일) |
| 마비로 행동 불가 | ○○은 몸이 저려서 움직일 수 없다! | WS core[24] `{1} is paralyzed! It can't move!` / battle_message.c:111 (동일) |
| 마비 해제 | ○○의 마비가 풀렸다! | battle_message.c:113 |
| 잠듦 | ○○은 잠들었다! | WS core[24] `{1} fell asleep!` |
| 잠듦(3세대) | ○○은 잠들어 버렸다! | battle_message.c:88 |
| 잠든 상태 유지 | ○○은 쿨쿨 잠들어 있다. | WS core[24] `{1} is fast asleep.` / battle_message.c:167 (동일) |
| 깨어남 | ○○은 잠에서 깨어났다! | WS core[24] `{1} woke up!` |
| 얼음 | ○○은 꽁꽁 얼어붙었다! | WS core[24] `{1} was frozen solid!` |
| 얼어서 행동 불가 | ○○은 얼어버려서 움직일 수 없다! | WS core[24] `{1} is frozen solid!` |
| 해동 | ○○의 얼음이 녹았다! | WS core[24] `{1} thawed out!` / battle_message.c:106 (동일) |
| 기술로 해동 | ○○의 얼음이 △△로 녹았다! | battle_message.c:108 |
| 혼란 걸림 | ○○은 혼란에 빠졌다! | WS core[24] `{1} became confused!` / battle_message.c:121 (동일) |
| 혼란 상태 | ○○은 혼란에 빠져 있다! | battle_message.c:119 |
| 혼란 자해 | 영문도 모르고 자신을 공격했다! | WS core[24] `It hurt itself in its confusion!` |
| 혼란 해제 | ○○은 혼란이 풀렸다. | WS core[24] `{1} snapped out of its confusion.` |
| 피로 혼란 | ○○은 몹시 지쳐서 혼란에 빠졌다! | WS core[24] `{1} became confused due to fatigue!` / battle_message.c:182 (동일) |
| 헤롱헤롱 | ○○은 헤롱헤롱해졌다! | WS core[24] `{1} fell in love!` |
| 풀죽음 | ○○은 풀이 죽어 기술을 쓸 수 없다! | WS core[24] `{1} flinched and couldn't move!` |
| 풀죽음(3세대) | ○○은 풀이 죽어 움직일 수 없었다! | battle_message.c:128 |
| 악몽 | ○○은 악몽을 꾸고 있다! | WS core[24] `{1} is locked in a nightmare!` |
| 이미 걸려 있음 | ○○은 이미 잠들어 있다. / 이미 독에 걸렸다. / 이미 화상에 걸렸다. / 이미 마비됐다. / 이미 얼음 상태다. / 이미 혼란 상태다. | WS core[24] `{1} is already asleep!` 외 |
| 걸리지 않음 | ○○은 독에 걸리지 않는다! / 화상에 걸리지 않는다! / 마비되지 않는다! / 얼음 상태가 되지 않는다! | WS core[24] `{1} cannot be poisoned!` 외 |
| 특성이 막음 | ○○은 △△의 □□ 때문에 독에 걸리지 않는다! | WS core[24] `{1} cannot be poisoned because of {2}'s {3}!` |
| 완전 면역(게임 고유) | ○○은 잠들지 않는다! / 화상을 입지 않는다! / 마비되지 않는다! / 혼란에 빠지지 않는다! | WS game[24] `{1} is completely immune to being put to sleep!` 외 |
| 근성으로 자가 회복 | ○○은 걱정을 끼치지 않으려고 어떻게든 독을 억제했다! | WS core[24] `{1} managed to expel the poison so you wouldn't worry!` |
| 〃 (잠) | ○○은 걱정을 끼치지 않으려고 혼자서 잠을 깼다! | WS core[24] `{1} shook itself awake so you wouldn't worry!` |

## 2. 날씨·필드·설치 기술 피해

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 모래바람 시작 | 모래바람이 불기 시작했다! | WS core[24] `A sandstorm brewed!` / battle_message.c:347 (동일) |
| 모래바람 지속 | 모래바람이 불고 있다. | WS core[24] `A sandstorm is raging.` |
| 모래바람 지속(3세대) | 모래바람이 세차게 불고 있다 | battle_message.c:485 |
| 모래바람 종료 | 모래바람이 가라앉았다. | WS core[24] `The sandstorm subsided.` / battle_message.c:349 (동일) |
| 모래바람 피해 | ○○은 모래바람에 데미지를 입었다! | WS core[24] `{1} is buffeted by the sandstorm!` |
| 모래바람 피해(3세대) | 모래바람이 ○○를 덮쳤다! | battle_message.c:161 |
| 싸라기눈 시작 | 싸라기눈이 내리기 시작했다! | WS core[24] `It started to hail!` / battle_message.c:353 (동일) |
| 싸라기눈 지속 | 싸라기눈이 계속 내리고 있다 | WS core[24] `The hail is crashing down.` / battle_message.c:354 (동일) |
| 싸라기눈 종료 | 싸라기눈이 그쳤다. | WS core[24] `The hail stopped.` / battle_message.c:355 (동일) |
| 싸라기눈 피해 | ○○은 싸라기눈에 데미지를 입었다! | WS core[24] `{1} is buffeted by the hail!` |
| 싸라기눈 피해(3세대) | 싸라기눈이 ○○를 덮쳤다! | battle_message.c:162 |
| 비 시작 / 지속 / 종료 | 비가 내리기 시작했다! / 비가 내리고 있다. / 비가 그쳤다. | WS core[24] `It started to rain!` 외 |
| 폭우 | 세찬 비가 내리기 시작했다! · 비가 퍼붓듯 내리고 있다. · 세찬 비의 기세는 멈추지 않는다! | WS core[24] `A heavy rain began to fall!` 외 |
| 쾌청 시작 / 지속 / 종료 | 햇살이 강해졌다! / 햇살이 강하다. / 햇살이 원래대로 돌아왔다. | WS core[24] `The sunlight turned harsh!` 외 |
| 큰가뭄 | 햇살이 아주 강해졌다! · 강한 햇살의 기세는 멈추지 않는다! | WS core[24] `The sunlight turned extremely harsh!` 외 |
| 날씨로 기술 무효 | 불꽃타입 공격이 폭우 속에서 꺼지고 말았다! / 물타입 공격이 큰가뭄 속에서 증발하고 말았다! | WS core[24] `The Fire-type attack fizzled out in the heavy rain!` 외 |
| 압정뿌리기 피해 | ○○은 압정뿌리기의 데미지를 입었다! | WS core[24] `{1} is hurt by the spikes!` / battle_message.c:208 (동일) |
| 독압정 | ○○은 독압정에 찔러 독에 걸렸다! · ○○은 독압정에 찔려 맹독에 걸렸다! · ○○은 독압정을 흡수했다! | WS core[24] `{1} was poisoned by the poison spikes!` 외 |
| 끈적끈적네트 | ○○은 끈적끈적네트에 걸렸다! | WS core[24] `{1} was caught in a sticky web!` |
| 필드 소멸 | 발밑에 전기가 사라졌다. / 발밑에 풀이 사라졌다. / 발밑에 안개가 사라졌다. / 발밑에 이상한 기운이 사라졌다. | WS core[24] `The electricity disappeared from the battlefield.` 외 |
| 필드 보호 | ○○은 일렉트릭필드 때문에 잠들지 않는다! · ○○은 미스트필드에 감싸여 나쁜 상태가 되지 않는다! · ○○은 사이코필드에 보호받고 있다! | WS core[24] `{1} surrounds itself with electrified terrain!` 외 |

## 3. 급소 · 타입 상성 · 일격필살

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 급소 | 급소에 맞았다! | WS core[24] `A critical hit!` / battle_message.c:316 (동일) |
| 급소(대상 명시) | ○○의 급소에 맞았다! | WS core[24] `A critical hit on {1}!` |
| 효과 굉장 | 효과가 굉장했다! | WS core[24] `It's super effective!` / battle_message.c:322 (동일) |
| 효과 굉장(대상 명시) | ○○에게 효과가 굉장했다! | WS core[24] `It's super effective on {1}!` |
| 효과 별로 | 효과는 별로인 듯 하다. | WS core[24] `It's not very effective...` |
| 효과 별로(3세대) | 효과가 별로인 듯하다 | battle_message.c:321 |
| 효과 없음 | 그러나 효과가 없었다! | WS core[24] `But it had no effect!` / battle_message.c:262 (동일) |
| 효과 없음(대상 명시) | ○○에게는 효과가 없는 것 같다... | battle_message.c:78 |
| 특성으로 무효 | ○○의 △△ 때문에 □□은 효과가 없다! | WS core[24] `{1}'s {2} made {3} ineffective!` / battle_message.c:293 (동일) |
| 일격필살 | 일격필살! | WS core[24] `It's a one-hit KO!` / battle_message.c:317 (동일) |
| 급소 차단 | 주술의 힘으로 ○○의 급소가 숨겨졌다! | WS core[24] `The Lucky Chant shielded {1} from critical hits!` |
| 대타출동 대신 맞음 | 대타출동이 ○○ 대신 데미지를 받았다! | WS core[24] `The substitute took damage for {1}!` |

## 4. 행동 실패 · 회피 · 버티기

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 기술 사용 | ○○의\n△△! (줄바꿈 포함) | WS core[24] `{1} used {2}!` |
| 실패 | 하지만 실패했다! | WS core[24] `But it failed!` |
| 실패(3세대) | 그러나 실패하고 말았다! | battle_message.c:339 |
| 대상에게 무효 | 그러나 ○○에게는 아무 효과가 없다! | WS core[24] `But it failed to affect {1}!` |
| 빗나감 | ○○의 공격이 빗나갔다! | WS core[24] `{1}'s attack missed!` |
| 빗나감(3세대) | 그러나 ○○의 공격은 빗나갔다! | battle_message.c:73 |
| 회피 | ○○은 공격을 피했다! | WS core[24] `{1} avoided the attack!` |
| 방어 성공 | ○○은 공격으로부터 몸을 지켰다! | WS core[24] `{1} protected itself!` |
| 버팀 | ○○은 공격을 버텼다! | WS core[24] `{1} endured the hit!` / battle_message.c:212 (동일) |
| 옹골참 | ○○은 옹골참으로 공격을 버텼다! | WS core[24] `{1} hung on with Sturdy!` |
| 기합의띠 | ○○은 기합의띠로 버텼다! | WS core[24] `{1} hung on using its Focus Sash!` |
| 반동으로 피해 | ○○은 반동으로 데미지를 입었다! | WS core[24] `{1} is damaged by recoil!` |
| 반동으로 행동 불가 | ○○은 반동 때문에 움직일 수 없다! | WS core[24] `{1} must recharge!` |
| 〃 (3세대) | 공격의 반동으로 ○○은 움직일 수 없다! | battle_message.c:190 |
| 게으름 | ○○은 게으름피우고 있다. | WS core[24] `{1} is loafing around!` |
| 〃 (3세대) | ○○은 게으름을 피우고 있다! | battle_message.c:370 |
| PP 없음 | 그러나 기술을 사용할 PP가 남아있지 않다! | WS core[24] `But there was no PP left for the move!` |
| 도발 | ○○은 도발당해서 △△를 쓸 수 없다! | WS core[24] `{1} can't use {2} after the taunt!` |
| 앙코르 | ○○은 앙코르의 효과로 △△만 사용 가능하다! | WS game[24] `{1} can only use {2} due to its Encore!` |
| 명령 불복종 + 자해 | ○○은 명령을 듣지 않는다! 영문도 모르고 자신을 공격했다! | WS core[24] `{1} won't obey! It hurt itself in its confusion!` |

## 5. 능력 변화

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 상승 | ○○의 △△이 올랐다! | WS core[24] `{1}'s {2} rose!` |
| 상승(3세대, 조립형) | ○○의 △△이 올라갔다! | battle_message.c:306+309 |
| 크게 상승 | ○○의 △△이 크게 올랐다! | WS core[24] `{1}'s {2} rose sharply!` |
| 매우 크게 상승 | ○○의 △△이 매우 크게 올랐다! | WS core[24] `{1}'s {2} rose drastically!` |
| 하락 | ○○의 △△이 떨어졌다! | WS core[24] `{1}'s {2} fell!` / battle_message.c:308 (동일) |
| 크게 하락 | ○○의 △△이 크게 떨어졌다! | WS core[24] `{1}'s {2} harshly fell!` |
| 매우 크게 하락 | ○○의 △△이 매우 크게 떨어졌다! | WS core[24] `{1}'s {2} severely fell!` |
| 더 못 올림 | ○○의 △△은 더 이상 올라가지 않는다! | WS core[24] `{1}'s {2} won't go any higher!` |
| 〃 (3세대) | ○○의 능력은 더 올라가지 않는다! | battle_message.c:314 |
| 더 못 내림 | ○○의 능력치는 더 이상 내려가지 않는다! | WS core[24] `{1}'s stats won't go any lower!` |
| 초기화 | ○○의 능력 변화가 초기화됐다! | WS core[24] `{1}'s stat changes were removed!` |
| 반전 | ○○의 능력 변화가 반전되었다! | WS core[24] `{1}'s stats were reversed!` |
| 능력치 이름 | 공격 · 방어 · 특수공격 · 특수방어 · 스피드 · 명중률 · 회피율 | WS core[24] `Attack` 외 |

## 6. 교체 · 등장 · 쓰러짐

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 내보내기 | 가랏! ○○! | WS core[24] `Go! {1}!` / battle_message.c:401 (동일) |
| 상대가 내보냄 | ○○은 △△를 내보냈다! | WS core[24] `{1} sent out {2}!` |
| 회수 (잘했어) | 잘했어, ○○! 돌아와! | WS core[24] `Good job, {1}! Come back!` |
| 회수 (좋아) | 좋아, ○○! 돌아와! | WS core[24] `OK, {1}! Come back!` |
| 회수 (그 정도면) | ○○, 그 정도면 됐어! 돌아와! | WS core[24] `{1}, that's enough! Come back!` |
| 회수 (기본) | ○○, 돌아와! | WS core[24] `{1}, come back!` / battle_message.c:409 (동일) |
| 상대가 회수 | ○○은 △△를 볼로 불러들였다! | WS core[24] `{1} withdrew {2}!` |
| 쓰러짐 | ○○은 쓰러졌다! | WS core[24] `{1} fainted!` / battle_message.c:79 (동일) |
| 야생 등장 | 앗! 야생의 ○○이 튀어나왔다! | WS core[24] `Oh! A wild {1} appeared!` |
| 야생 등장(3세대) | 앗! 야생 ○○이 튀어나왔다! | battle_message.c:386 (「의」 없음) |
| 트레이너 도전 | ○○이 승부를 걸어왔다! | WS core[24] `You are challenged by {1}!` / battle_message.c:390 (동일) |
| 승리 | ○○과의 승부에서 이겼다! | WS core[24] `You defeated {1}!` / battle_message.c:327 (동일) |
| 패배 | ○○과의 승부에서 졌다! | WS core[24] `You lost against {1}!` / battle_message.c:329 (동일) |
| 상금 | 상금으로 $○○ 만큼 받았다! | WS core[24] `You got ${1} for winning!` |
| 도망 성공 | 성공적으로 도망쳤다! | WS core[24] `You got away safely!` |
| 도망 성공(3세대) | 무사히 도망쳤다! | battle_message.c:323 |
| 트레이너전 도망 불가 | 안돼! 트레이너와의 승부 중에 등을 돌릴 순 없어! | WS core[24] `No! There's no running from a Trainer battle!` |
| 〃 (3세대) | 안돼! 승부 도중에 상대에게 등을 보일 순 없어! | battle_message.c:335 |
| 도망 불가 | 도망칠 수 없다! | WS core[24] `You can't escape!` / battle_message.c:336 (동일) |
| 상대가 도망 | ○○은 도망쳤다! | WS core[24] `{1} fled!` / battle_message.c:326 (동일, 「야생 ○○」) |
| 전멸 | 불운히 패배한 후, 포켓몬센터로 서둘러 돌아갔다. | WS core[24] `After the unfortunate defeat, you scurry back to a Pokémon Center.` |
| 메가진화 | ○○은 △△으로 메가진화했다! | WS core[24] `{1} has Mega Evolved into {2}!` |

## 7. 포획

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 트레이너 포켓몬에 볼 | 남의 것에 손 대면 도둑! | WS core[24] `The Trainer blocked your Poké Ball! Don't be a thief!` |
| 〃 (3세대) | 남의 것에 손대면 도둑! | battle_message.c:470 |
| 볼 튕겨냄(3세대) | 트레이너가 볼을 튕겨내 버렸다! | battle_message.c:469 |
| 볼 회피(3세대) | 피했다! 이 녀석은 잡힐 것 같지 않군! | battle_message.c:471 |
| 빗맞음(3세대) | 포켓몬에게 제대로 맞지 않았다! | battle_message.c:472 |
| 볼에서 나옴(3세대) | 안돼! 포켓몬이 볼에서 나와버렸다! | battle_message.c:473 |
| 흔들림 1 | 아아! 잡은 줄 알았는데! | WS core[24] `Aww! It appeared to be caught!` |
| 〃 (3세대) | 아아! 잡았다고 생각했는데! | battle_message.c:474 |
| 흔들림 2 | 아쉽다! 조금만 더하면 잡을 수 있었는데! | WS core[24] `Aargh! Almost had it!` / battle_message.c:475 (동일) |
| 흔들림 3(3세대) | 아깝다! 조금만 더하면 됐는데! | battle_message.c:476 |
| 포획 성공 | 신난다! ○○를 잡았다! | WS core[24] `Gotcha! {1} was caught!` |
| 〃 (3세대) | 신난다-! ○○를 붙잡았다! | battle_message.c:477 |
| 도감 등록 | ○○의 데이터가 포켓몬도감에 등록됩니다. | WS core[24] `{1}'s data was added to the Pokédex.` |
| 닉네임 | ○○에게 닉네임을 붙이겠습니까? | WS core[24] `Would you like to give a nickname to {1}?` |
| 이미 잡음 | 이미 ○○를 잡았습니다. | WS core[24] `You already caught a {1}.` |

## 8. 경험치 · 레벨 · 기술 습득

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 경험치 획득 | ○○은 △△ 경험치를 얻었다! | WS core[24] `{1} got {2} Exp. Points!` / battle_message.c:61 (동일) |
| 보너스 경험치 | ○○은 많은 양의 △△ 경험치를 얻었다! | WS core[24] `{1} got a boosted {2} Exp. Points!` |
| 나머지 파티 | 다른 포켓몬들도 경험치를 얻었다! | WS core[24] `Your other Pokémon also gained Exp. Points!` |
| 레벨업 | ○○은 레벨 △△로 올랐다! | WS core[24] `{1} grew to Lv. {2}!` / battle_message.c:64 (「레벨△△로」, 띄어쓰기 없음) |
| 기술 습득 | ○○은 △△를 배웠다! | WS core[24] `{1} learned {2}!` |
| 기술 망각 | ○○은 △△를 깨끗이 잊었다! 그리고... | WS core[24] `{1} forgot how to use {2}. And...` |
| 망각 연출 | 1, 2, ... ... ... 짠! · 그리고...! | battle_message.c:318-319 |
| 비전머신 망각 불가 | 지금은 비전머신을 잊을 수 없다. | WS core[24] `HM moves can't be forgotten now.` |
| 진화 | ○○이 진화하려 한다! · 축하합니다! ○○은 △△으로 진화했다! · 어라? ○○의 진화가 멈췄다! | WS core[24] `{1} is evolving!` 외 |

## 9. HP 회복 · 도구 · 기타

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| HP 회복 | ○○의 HP가 회복됐다. | WS core[24] `{1}'s HP was restored.` |
| HP 회복(수치) | ○○의 HP가 △△ 만큼 회복됐다. | WS core[24] `{1}'s HP was restored by {2} points.` |
| 도구로 회복 | ○○의 △△으로 HP가 회복됐다. | WS core[24] `{1}'s {2} restored its HP.` |
| 도구로 상태 회복 | ○○의 △△ 덕분에 독이 나았다! | WS core[24] `{1}'s {2} cured its poisoning!` |
| 도구 사용(3세대) | ○○은 △△를 썼다! | battle_message.c:466 |
| 도구로 피해 무효 | ○○의 △△ 때문에 데미지가 없다! | WS core[24] `{1} avoided damage with {2}!` |
| 특성으로 피해 무효(3세대) | ○○은 △△ 때문에 데미지를 입지 않는다! | battle_message.c:75 |
| 도구/특성으로 피해 | ○○은 △△ 때문에 데미지를 입었다! | WS core[24] `{1} is hurt by its {2}!` |
| 기력 흡수 | ○○으로부터 에너지를 흡수했다! | WS core[24] `{1} had its energy drained!` |
| 유폭 | ○○은 유폭에 휘말렸다! | WS core[24] `{1} was caught in the aftermath!` |
| 길동무 | ○○은 상대를 길동무로 삼았다! | WS core[24] `{1} took its attacker down with it!` |
| 발버둥(기술명) | 발버둥 | WS core[24] `Struggle` |
| 상태이상 이름 | 독 · 화상 · 얼음 · 잠듦 · 모래바람 · 싸라기눈 | WS core[24] `Poison` / `Burn` / `Frozen` / `Sleep` 외 |

---

## 갈리는 자리 — 어느 쪽을 쓸지 정해야 하는 것

| 자리 | pokeemerald-kr (공식 3세대) | Wishing Star (Essentials 팬 번역) |
|---|---|---|
| 날씨 피해 문장 구조 | 모래바람이 ○○를 **덮쳤다!** (날씨가 주어) | ○○은 모래바람에 **데미지를 입었다!** (포켓몬이 주어) |
| 지속 피해 시제 | 데미지를 입고 **있다** (진행) | 데미지를 **입었다** (완료) |
| 효과 별로 | 효과**가** 별로인 듯하다 | 효과**는** 별로인 듯 하다. |
| 실패 | 그러나 실패하고 말았다! | 하지만 실패했다! |
| 풀죽음 | 풀이 죽어 **움직일 수 없었다!** | 풀이 죽어 **기술을 쓸 수 없다!** |
| 능력 상승 | 올라**갔다!** | 올**랐다!** |
| 포획 성공 | 신난다**-!** ○○를 **붙잡았다!** | 신난다! ○○를 **잡았다!** |
| 도둑 | 남의 것에 **손대면** 도둑! | 남의 것에 **손 대면** 도둑! (띄어쓰기) |
| 야생 등장 | 앗! 야생 ○○이 | 앗! 야생**의** ○○이 |
| 조사 처리 | `{B_TXT_EUNNEUN}` 류 전용 토큰 | `\j[은,는]` Essentials 플러그인 문법 |

**사용자가 예로 든 「다른 사람의 것에 손대면 도둑!」은 두 소스 어디에도 없다.**
3세대 공식은 「남의 것에 손대면 도둑!」이고 Wishing Star는 띄어쓰기만 다르다.
후대 세대에서 문구가 바뀌었을 가능성이 있으니, 이 한 줄은 최신 공식판으로 한 번 더 확인하는 편이 좋다.

**표기 통일이 필요한 것 둘.** 「데미지 / 대미지」는 두 소스 다 「데미지」인데 현행 공식은 「대미지」다.
「싸라기눈」은 3세대 표기이고 8세대 이후 공식은 「싸라기눈」을 유지하되 「눈(Snow)」이 따로 생겼다 —
Wishing Star도 `Hail`=싸라기눈, `Snow`=눈밭으로 갈라 놓았다.

## 원본 파일

- 추출 스크립트: `dump_pairs.py` (Marshal → `pairs.json`, 13,377쌍)
- 전체 대응표: `messages_1_core_24.txt` (1,684행) · `messages_1_game_24.txt` (1,090행) — 탭 구분 `인덱스\t영문\t한국어`
- 공식 3세대 원본: `pokeemerald-kr/src/battle_message.c`

## 10. 기초 표현 (배틀 외)

배틀 밖에서 시스템이 찍는 정형 문구다. 수집 방법과 출처 표기는 앞 절과 같다 —
`WS core[24]`는 Wishing Star v1.0.7 `Data/messages_1_core.dat` 인덱스 24의
영문 원문 → 한국어 사전이고, 조회 키는 표에 적힌 영문이다.
이름 자리는 **○○**(첫째)·**△△**(둘째)로 통일했다.

### 10.1 기술 잊기 · 배우기

Essentials v16(Z)은 이 흐름을 짧은 메시지 여러 장으로 쪼개 놓았는데
Wishing Star가 쓰는 v20 계열은 한 장으로 합쳐 놓아서, 쪼개진 자리는 3세대 공식
텍스트에서 해당 절을 잘라 왔다.

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 배우고 싶어 함 | ○○은 새로 △△를 배우고 싶다...! | pokeemerald-kr src/strings.c:414 |
| 기술칸이 꽉 참 | 그러나 ○○은 기술을 네 개 알고 있으므로 더 이상 배울 수 없다! | pokeemerald-kr src/strings.c:414 |
| 무엇을 지울지 물음 | △△ 대신 다른 기술을 잊게 하겠습니까? | pokeemerald-kr src/strings.c:414 |
| 결국 안 배움 | ○○은 △△를 결국 배우지 않았다! | pokeemerald-kr src/strings.c:416 |
| 망각 연출 | 1, 2, ... ... ... 짠! | WS core[24] `1, 2, and... ... ... Ta-da!` |
| 기술 망각 | ○○은 △△를 깨끗이 잊었다! 그리고... | WS core[24] `{1} forgot how to use {2}. And...` |
| 〃 (짧은 판) | ○○은 △△를 잊었다... | WS core[24] `{1} forgot {2}...` |
| 습득 여부 라벨 | 알고있음 / 가능 | WS core[24] `LEARNED` · `ABLE` |

Z는 `¡Puf!`를 「펑!」으로 옮겨 놓았는데 Essentials 원문이 `Ta-da!`이고
Wishing Star가 「짠!」으로 옮긴다. 3세대 공식에서 이 자리를 맡는 인물이
**깜빡할아버지**(`LilycoveCity_MoveDeletersHouse`)다.

### 10.2 진화

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 진화 시작 | 어라?\n○○의 모습이...! | pokeemerald-kr src/battle_message.c:1192 (「...오잉!?\n○○의 모습이...!」) |
| 진화 중단 | 어라?\n○○의 진화가 멈췄다! | WS core[24] `Huh? {1} stopped evolving!` |
| 진화 완료 | 축하합니다! ○○은 △△으로 진화했다! | WS core[24] `Congratulations! Your {1} evolved into {2}!` |

Z는 이 셋을 이미 전통 표현으로 옮겨 놓았다. 다만 판본이 여럿 실려 있어서
같은 자리를 「○○이 진화하고 있다!」·「○○은 진화를 멈췄다!」로 적은 사본이
섞여 있다 — 그 사본들만 위 형태로 맞췄다.

### 10.3 리포트(세이브)

한국 공식판은 세이브를 **리포트**라 부른다. 3세대와 Wishing Star가 일치한다.

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 메뉴 항목 | 리포트 | WS core[24] `Save` / pokeemerald-kr src/strings.c:745 |
| 저장할지 물음 | 여기까지의 모험을 기록하시겠습니까? | WS core[24] `Would you like to save the game?` |
| 저장 완료 | ○○은 리포트를 꼼꼼히 기록했다! | WS core[24] `{1} saved the game.` / pokeemerald-kr src/strings.c:1280 |
| 덮어쓰기 확인 | 정말로 리포트를 작성하고 다른 세이브파일을 덮어쓰겠습니까? | WS core[24] `Are you sure you want to save now and overwrite the other save file?` |

Wishing Star도 이 넷 말고는 「세이브파일」·「게임이 저장되었습니다」로 적는다 —
전통 표현이 걸리는 자리는 위 넷뿐이고 파일 조작 문구까지 리포트로 바꾸지는 않았다.

### 10.4 닉네임

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 닉네임을 붙일지 물음 | ○○에게 닉네임을 붙이겠습니까? | WS core[24] `Would you like to give a nickname to {1}?` |
| 갓 부화한 개체 | 새로 태어난 ○○에게 닉네임을 붙이겠습니까? | WS core[24] `Would you like to nickname the newly hatched {1}?` |
| 입력 프롬프트 | ○○의 닉네임은? | WS core[24] `{1}'s nickname?` |

한국 공식판은 **닉네임**이고 「별명」이 아니다. 3세대도 같다
(`battle_message.c:479` 「잡은 ○○에게\n닉네임을 붙이겠습니까?」).

### 10.5 낚시 · 알

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 입질 | 앗! 입질이 왔다! | WS core[24] `Oh! A bite!` |
| 낚아 올림 | 포켓몬을 낚았다! | pokeemerald-kr src/strings.c:1558 |
| 부화 | 알이 부화해서 ○○이 태어났다! | pokeemerald-kr src/strings.c:1306 |
| 〃 (Essentials 판) | 알에서 ○○이 부화했다! | WS core[24] `{1} hatched from the Egg!` |

3세대는 입질을 「걸렸다 걸렸다!!」로 적는다(`strings.c:1557`). 후대 표현인
「입질이 왔다」 쪽을 Wishing Star가 쓰므로 그쪽을 따랐다.
부화 문구는 두 소스가 「태어났다」와 「부화했다」로 갈리는데 Z가 이미
3세대 쪽(「태어났다」)이라 손대지 않았다.

### 10.6 상점

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 돈 부족 | 손님, 죄송하지만 돈이 부족하시군요. | WS core[24] `You don't have enough money.` |
| 매각 완료 | ○○을 $△△에 매각했다. | WS core[24] `You turned over the {1} and got ${2}.` |
| 매입/매각 메뉴 | 사러 왔다 / 팔러 왔다 | WS core[24] `I'm here to buy` · `I'm here to sell` |
| 매입 제안 | 그거라면 △△원에 매입하겠습니다. 괜찮습니까? | WS core[24] `I can pay ${1}.\nWould that be OK?` |
| 매각 수량 | ○○을 몇 개 매각하시겠습니까? | WS core[24] `How many {1} would you like to sell?` |
| 매입 거절 | 어, ○○은 매입하기 어렵습니다. | WS core[24] `Oh, no. I can't buy {1}.` |
| 인사 | 어서 오세요! 어떻게 도와드릴까요? | WS core[24] `Welcome! How may I help you?` |

Z의 상점 대사는 반말(「괜찮겠어?」)이고 Wishing Star는 존댓말이다. 표에는 전통
표현을 그대로 적었지만 **실제로 바꾼 것은 존댓말/반말 구분이 없는 자리뿐**이다 —
매입 제안·매각 수량·매입 거절은 말투가 뒤섞일 위험이 있어 뺐다.

### 10.7 PC · 박스

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| PC 켜기 | ○○은 PC의 전원을 켰다. | WS core[24] `{1} booted up the PC.` |
| PC 고르기 | 어느 PC에 접속하시겠습니까? | WS core[24] `Which PC should be accessed?` |
| 맡길 박스 고르기 | 어느 박스에 맡깁니까? | WS core[24] `Deposit in which Box?` |
| 박스 이동 | 어느 박스로 점프합니까? | WS core[24] `Jump to which Box?` |
| 박스 나가기 | 박스를 종료하겠습니까? | pokeemerald-kr src/strings.c:873 |

박스 나가기는 Wishing Star가 「박스로부터 나가겠습니까?」로 적는데 번역투라
3세대 쪽을 골랐다. **파티/지닌포켓몬** 용어는 건드리지 않았다 — Wishing Star는
「지닌포켓몬」, Z는 「파티」로 일관돼 있어서 어느 쪽으로 통일할지는 따로 정할
일이다.

### 10.8 전멸 · 도구

| 상황 | 한국 전통 표현 | 출처 |
|---|---|---|
| 전멸 | 불운히 패배한 후, 포켓몬센터로 서둘러 돌아갔다. | WS core[24] `After the unfortunate defeat, you scurry back to a Pokémon Center.` |
| 〃 (긴 판) | 지친 포켓몬들을 다치지 않게 보호하면서 어떻게든 포켓몬센터로 서둘러 돌아갔다... | WS core[24] `You scurry back to a Pokémon Center, protecting your exhausted Pokémon from any further harm...` |
| 가방에 넣음 | ○○을 가방의 △△ 포켓에 넣었다. | WS core[24] `You put the {1} in\nyour Bag's <icon=bagPocket{2}>{3} pocket.` |
| 픽업 특성 | ○○은 △△를 주워왔다! | WS core[24] `{1} found a {2}!` |
| 도구 발견 | ○○을 발견했다! | WS core[24] `You found \c[1]{1}\c[0]!` |
| 도구 수령 | ○○을 받았다! | WS core[24] `You obtained \c[1]{1}\c[0]!` |

도구 수령은 Wishing Star가 「받았다」인데 Z는 「손에 넣었다」이고 3세대도
「손에 넣었다」를 쓴다(`battle_message.c:233`, `mystery_event_msg.c:3`).
양쪽 다 전통 표현이라 손대지 않았다.

### 10.9 대응을 못 찾은 자리

Wishing Star 사전에도 3세대에도 대응하는 문구가 없어 그대로 둔 것들.

- **포켓몬센터 회복 흐름** — 간호사가 회복을 마치고 하는 정형 문구
  (`Bienvenido! ¿En qué puedo ayudarte?` 외)에 해당하는 Essentials 키가 없다.
  Z 3599 「포켓몬 파티가 체력을 회복했다.」·3415 「어서 오세요!\n무엇을 도와드릴까요?」는
  대조 대상 없이 남겨 뒀다.
- **포켓약병(Pokévial)** — Z 고유 도구라 대응 없음(6099·6102).
- **학습장치 켜기/끄기** — Wishing Star는 「학습장치가 꺼졌다/켜졌다」(피동),
  Z는 「학습장치를 껐다/켰다」(능동)인데 스페인어 원문이 2인칭 능동이라 Z가 맞다.
- **자전거** — 「자전거를 탄 채로는 쓸 수 없다」와 Wishing Star의 「자전거를 탄 채로
  쓸 수 없다」 차이가 조사 하나뿐이라 뺐다.
- **레벨 업 · 경험치** — Z가 이미 Wishing Star와 같은 문구를 쓴다
  (「○○은 레벨 △△로 올랐다!」·「○○은 △△ 경험치를 얻었다!」).
