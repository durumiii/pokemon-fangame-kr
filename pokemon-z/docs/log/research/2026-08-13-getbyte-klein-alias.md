# 굵은 한글 튕김의 뿌리 — 원작이 getbyte를 첨자에 별칭으로 걸어 둔다 (2026-08-13)

[2026-08-09 호환 감사](2026-08-09-ruby-compat-sweep.md)가 미해결로 남긴 모순
(「루나는 루비 3.1이라 `getbyte`가 있는데 왜 난이도 선택에서 터지나」)의 답. 계기는
유저가 배포한 루나 수정본(디시 229306) 대조.

## 답 (실측)

게임 원작 `Map - Klein` 섹션이 구판 흉내를 내려고 **조건 없이** 별칭을 건다:

```ruby
class String
  alias getbyte  []
  alias setbyte  []=
  alias bytesize size
end
```

그래서 신형 루비에서도 `"가".respond_to?(:getbyte)`는 참이고, `getbyte(0)`은 정수가
아니라 **한 글자짜리 문자열**을 돌려준다. `003_BoldHangul.rb`의
`b = s.respond_to?(:getbyte) ? s.getbyte(0) : …`가 그 값을 192와 비교해
`comparison of String with 192 failed`로 죽는다 — 2026-08-08 제보의 그 문구다.

**우리 수리가 실제로 막는 자리는 글꼴 모드가 아니라 코어다.**
`share/patch_ruby_compat.py`가 이 별칭을 `if !"".respond_to?(:getbyte)` 안에 넣는다
(설치본 `Map - Klein` 97~101줄). 별칭이 꺼지면 3.1의 진짜 `getbyte`가 살아나 정상 동작한다.

## 그래서 글꼴 모드는 혼자 못 선다 (실측)

루비 3.1.4 실물로 여섯 조합을 돌린 결과:

| 실행기 | Klein 별칭 | 우리 판 대 유저 판(`unpack("C")[0]`) |
|---|---|---|
| getbyte 있음 | 가드 있음(우리 코어) | 입력 11개 전부 일치 |
| getbyte 없음 | 가드 있음 | 전부 일치 |
| getbyte 없음 | 별칭 없음 | 전부 일치 |
| getbyte 있음 | **가드 없음** | **10/11 우리 판만 ArgumentError** |
| getbyte 없음 | **가드 없음** | **10/11 우리 판만 ArgumentError** |

즉 **코어 수술이 안 실린 게임에 글꼴 모드만 얹으면 모든 글자에서 죽는다.** 모드킷
채널로 글꼴 모드를 따로 배포하는 경로가 여기 걸린다 — 모드 쪽 폴백을 `unpack`
우선으로 바꾸거나 모드 안에 같은 가드를 심어야 단독으로 선다.

## 곁가지 — `nitems` 심은 전 자리를 덮는다 (실측)

설치본 274섹션 전수 grep에서 `Array#nitems` 호출은 `PScreen_Storage` 여섯 자리뿐이고,
심(`Z-32 Ruby Compat`)이 0번 섹션이라 모든 호출보다 먼저 실린다. 유저가 호출부를
`compact.length`로 고친 것과 값이 갈리는지 무작위 7,000건으로 대조해 불일치 0.
수신자가 해시일 때만 갈리는데(심은 `NoMethodError`, `compact.length`는 0) 그런 호출은
코어에 없다.

부수 관측: 1.8.7에서는 심이 `getbyte`를 먼저 채워 Klein의 가드가 거짓이 되므로
`alias setbyte []=`가 영영 안 걸린다. 호출자가 없어 무해하지만
`share/patch_ruby_compat.py`의 주석은 이 점에서 사실과 다르다.

## 한계

- 루비 1.8.7 실물은 못 구했다(portable-ruby 최소가 2.6.3). 그 경로는 의미론 흉내로만 봤다.
- mkxp-z 실기 미실행 — 순수 루비 의미론만 봤다. 엔진이 String을 네이티브로 덮는
  부분이 있으면 이 시험에 안 잡힌다.
- 감사 범위는 `getbyte`·`nitems` 둘뿐이다. `patch_ruby_compat.py`의 나머지 수술 열둘은 안 봤다.

## 재현

```
cd /tmp/.../scratchpad/compat-verify   # 시험 스크립트·portable-ruby 3.1.4
./rb/portable-ruby/3.1.4/bin/ruby t_getbyte.rb have unguarded
```
별칭 대조는 설치본 `Map - Klein` 97~101줄과 유저본의 같은 자리를 나란히 보면 된다.
