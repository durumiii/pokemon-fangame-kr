# Essentials 번역층 조사 (Z-38) — 2026-08-09

서브 조사(스크립트 실물 + 웹). 확정도 태그: 실측 / 웹1소스 / 추정 / 미발견.

## 판본 — v16.2 (실측)

`Scripts.rxdata`의 `Acentos` 섹션 헤더에 「Compatible : Essentials 16.2 / Autor :
Bezier」. `Scene_Credits`는 표준 코어 크레딧(Flameguru · Poccil(Peter O.) · Maruno)
까지만 있어 v16 계열과 정합. 재현: probe.py 상수 경로의 Scripts.rxdata를
rubymarshal+zlib로 해제해 해당 섹션을 읽으면 된다.

스페인어 번역층은 PokéLiberty 계열 v16.2 킷으로 보이나(웹1소스:
https://archive.org/details/PokmonEssentialsV16.2EBSHalfTranslatedToSpanish.7z —
「partially translated to Spanish… 'PokéLiberty'」, Public Domain Mark 1.0),
게임 파일 안에 「PokéLiberty」 문자열은 0건이라 연결은 정황 일치(추정)다.

## 절23 키 기원 (실측 휴리스틱 1회)

6,849키를 스페인어 특수문자(áéíóúñ¿¡ 등) 유무로 이분: 스페인어 2,439(35.6%) ·
ASCII 4,398(64.2%) · 그 외 12. ASCII 다수는 플레이어 비노출 오류·디버그 문자열
(「Expected a section at…」류)이고 일부만 메뉴 카테고리명. Scripts.rxdata의 `_INTL(`
호출은 5,005건으로 절23 키 수보다 적다 — dat가 스크립트 외 출처도 흡수했을 가능성
(추정, 빌드 로직 미추적).

## 한국어 Essentials 번역층 — 미발견 (검색 침묵, 부재 증명 아님)

검색 5종(디시 레쿠쟈 갤러리·GitHub·Eevee Expo 등)에서 나온 것은 전부 번역 **도구·
가이드**(intl.txt 추출 튜토리얼, Essential-Translation-Helper, QuEIT 등)이고 완성
번역층은 없다. 검색에 걸린 「포켓몬 Z 팬게임 개인번역」 글은 이 저장소 자신의 공지라
증거에서 제외(순환 참조).

## 결론 → reuse-playbook 등재

「기존 한국어 층을 가져다 붙이는」 부트스트랩은 소스가 없어 불성립. 대신 **이 저장소의
절23 정본 자체가 다음 스페인어 팬게임(같은 킷 계열)의 한국어 번역층**이다 — 본가 자구
정렬까지 스며 있어 어떤 커뮤니티 층보다 낫다. 순서는
[reuse-playbook](../../guides/reuse-playbook.md)의 「시스템 문구는 이식부터」 절에 등재.
