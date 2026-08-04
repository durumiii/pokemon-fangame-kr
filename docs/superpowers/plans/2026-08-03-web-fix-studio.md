# 웹 수정 스튜디오 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 한글패치 유저가 브라우저만으로 korean.dat를 검색→수정→재빌드하고, 고침 파일 공유·원버튼 제보까지 하는 정적 웹앱(GitHub Pages).

**Architecture:** HTML+JS 정적 페이지가 pyodide로 기존 파이썬 직렬화 코드(rubymarshal + rubywrite + 빌드.py의 값-교체 로직)를 그대로 돌린다. 파일 IO는 전부 JS의 File System Access API(폴더 선택→읽기/쓰기)로 하고, 파이썬은 bytes⇄rows 변환·재직렬화만 담당한다. 서버 없음.

**Tech Stack:** pyodide(CDN), rubymarshal(vendored), rubywrite(기존 사본), 순수 JS(프레임워크 없음), localStorage(수정 보존), Google Form no-cors POST(제보).

**스펙:** `docs/superpowers/specs/2026-08-03-web-fix-studio-design.md`

## Global Constraints

- 대상 브라우저: Chrome/Edge (File System Access API). 페이지에 명시.
- 유저 쪽 로그인·계정·설치·설정 일체 없음.
- JS 프레임워크·빌드 도구 금지 — 정적 파일 그대로 배포.
- UI 문구는 한국어, fixgui.py의 다크 테마 CSS를 이식.
- 파이썬 직렬화 코드는 기존 로직 이식 — 새 Marshal 코드 작성 금지.
- 번역표·게임 데이터·조인표는 웹앱 repo에 올리지 않는다(코드만).
- 파일 크기: 800줄 상한(coding-style).
- 커밋은 conventional commits, 한국어 설명.

## File Structure

```
pokemon-z/webapp/
  index.html          # 마크업 + CSS(fixgui 이식) + pyodide 부트 스크립트 로드
  app.js              # UI·파일IO·백업·내보내기/가져오기·제보·pyodide 브리지
  core.py             # pyodide용: load_dat(rows 추출)·build_dat(값 교체+왕복 검증)
  rubywrite.py        # vendor/fanlib/rubywrite.py 사본
  vendor/rubymarshal/ # PyPI wheel에서 푼 순수 파이썬 소스
  tests/test_core.py  # 네이티브 pytest — 실물 korean.dat 대상(없으면 skip)
  publish.sh          # 공개 repo(choneuny/z-kr-studio)로 배포 + Pages
translate/build.py    # 수정: __kr_patch__ 버전 표식 심기
translate/VERSION     # 신규: 현재 패치 버전 문자열 (예: v5)
```

---

### Task 1: core.py — dat 로드(rows 추출) + 메타

**Files:**
- Create: `pokemon-z/webapp/core.py`
- Create: `pokemon-z/webapp/rubywrite.py` (사본)
- Create: `pokemon-z/webapp/vendor/rubymarshal/` (wheel에서 추출)
- Test: `pokemon-z/webapp/tests/test_core.py`

**Interfaces:**
- Produces: `core.load_dat(dat_bytes: bytes, msg_bytes: bytes|None) -> str(JSON)` — `{"meta": str|None, "sha": str, "rows": [{"sec","map"(sec0만),"idx","k"(있으면),"v"}]}`. 로드된 파싱 트리는 모듈 전역 `_state["d"]`에 유지(같은 pyodide 세션의 build가 사용).
- Produces: `SECTION_NAMES: dict[int,str]` (export.py와 동일).

- [ ] **Step 1: rubymarshal vendoring + rubywrite 사본**

```bash
cd /home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z
mkdir -p webapp/vendor webapp/tests
cp vendor/fanlib/rubywrite.py webapp/rubywrite.py
pip download rubymarshal --no-deps -d /tmp/rm-dl
cd /tmp/rm-dl && unzip -o rubymarshal-*.whl 'rubymarshal/*' -d /tmp/rm-src
cp -r /tmp/rm-src/rubymarshal /home/durumii/workspace/claude-native/pokemon-fangame-kr/pokemon-z/webapp/vendor/
```

확인: `ls webapp/vendor/rubymarshal/` 에 `reader.py writer.py classes.py` 등이 있어야 한다.

- [ ] **Step 2: 실패하는 테스트 작성**

`webapp/tests/test_core.py`:

```python
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # core, rubywrite
sys.path.insert(0, str(HERE.parent / "vendor"))  # rubymarshal

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
MESSAGES = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/messages.dat")

pytestmark = pytest.mark.skipif(not STORE.exists(), reason="실물 korean.dat 없음")


@pytest.fixture(scope="module")
def dat_bytes():
    return STORE.read_bytes()


@pytest.fixture(scope="module")
def loaded(dat_bytes):
    import core
    msg = MESSAGES.read_bytes() if MESSAGES.exists() else None
    return json.loads(core.load_dat(dat_bytes, msg))


def test_load_row_count(loaded):
    # 실전 키 2만 행 이상 (build.py 주석의 20,715개 기준 하한)
    assert len(loaded["rows"]) > 20000


def test_load_row_shape(loaded):
    r0 = next(r for r in loaded["rows"] if r["sec"] == 0)
    assert set(r0) >= {"sec", "map", "idx", "k", "v"}
    r5 = next(r for r in loaded["rows"] if r["sec"] == 5)  # 기술 이름(목록 절)
    assert "idx" in r5 and "v" in r5


def test_load_sha_and_meta(loaded):
    assert len(loaded["sha"]) == 12
    # v5 dat엔 표식이 없다 — None 허용, 있으면 문자열
    assert loaded["meta"] is None or isinstance(loaded["meta"], str)
```

- [ ] **Step 3: 실패 확인**

Run: `cd pokemon-z/webapp && python -m pytest tests/test_core.py -x -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'core'`

- [ ] **Step 4: core.py 구현 (로드 절반)**

```python
"""웹 스튜디오 pyodide 코어 — korean.dat ⇄ rows.

export.py·빌드.py의 로직 이식. 파일 IO 없음(bytes in/out) —
브라우저 JS가 File System Access API로 읽고 쓴다.
"""
import hashlib
import io
import json

from rubymarshal.reader import load

import rubywrite

SECTION_NAMES = {
    0: "maps", 1: "species", 2: "kinds", 3: "entries", 4: "forms", 5: "moves",
    6: "move-descs", 7: "items", 8: "item-plurals", 9: "item-descs",
    10: "abilities", 11: "ability-descs", 12: "types", 13: "trainer-classes",
    14: "trainer-names", 15: "begin-speech", 16: "end-speech-win",
    17: "end-speech-lose", 18: "regions", 19: "place-names", 20: "place-descs",
    21: "map-names", 22: "phone", 23: "script-texts",
}
META_KEY = b"__kr_patch__"
META_SEC = 23

_state = {}


def _inner(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def _dec(b):
    return bytes(b).decode("utf-8", "replace")


def load_dat(dat_bytes, msg_bytes=None):
    d = load(io.BytesIO(bytes(dat_bytes)))
    es = load(io.BytesIO(bytes(msg_bytes))) if msg_bytes else []
    rows, meta = [], None
    for sec in range(len(d)):
        obj = d[sec]
        if sec == 0:
            for mi, oh in enumerate(obj):
                keys, values = _inner(oh)
                for j in range(len(keys)):
                    rows.append({"sec": 0, "map": mi, "idx": j,
                                 "k": _dec(keys[j]), "v": _dec(values[j])})
        elif isinstance(obj, list):
            ref = es[sec] if sec < len(es) and isinstance(es[sec], list) else []
            for i, v in enumerate(obj):
                row = {"sec": sec, "idx": i, "v": _dec(v)}
                if i < len(ref) and bytes(ref[i]) != bytes(v):
                    row["k"] = _dec(ref[i])
                rows.append(row)
        elif hasattr(obj, "_private_data"):
            keys, values = _inner(obj)
            for j in range(len(keys)):
                if sec == META_SEC and bytes(keys[j]) == META_KEY:
                    meta = _dec(values[j])
                    continue
                rows.append({"sec": sec, "idx": j,
                             "k": _dec(keys[j]), "v": _dec(values[j])})
    _state["d"] = d
    return json.dumps({"meta": meta,
                       "sha": hashlib.sha256(bytes(dat_bytes)).hexdigest()[:12],
                       "rows": rows}, ensure_ascii=False)
```

- [ ] **Step 5: 통과 확인**

Run: `python -m pytest tests/test_core.py -x -q`
Expected: 3 passed (실물 dat 있는 devbox 기준)

- [ ] **Step 6: Commit**

```bash
git add webapp
git commit -m "feat(webapp): core.py 로드 — korean.dat→rows 추출 + rubymarshal vendoring"
```

---

### Task 2: core.py — build_dat (값 교체 + 왕복 검증)

**Files:**
- Modify: `pokemon-z/webapp/core.py`
- Test: `pokemon-z/webapp/tests/test_core.py`

**Interfaces:**
- Consumes: Task 1의 `_state["d"]`, `_inner`, `rubywrite.dumps`.
- Produces: `core.build_dat(edits_json: str) -> bytes` — edits는 `[{"sec","map"(sec0만),"idx","k"(원문 대조용, 있으면),"v"}]` JSON 문자열. 원문 k 불일치·인덱스 초과 시 `ValueError`. 반환은 왕복 검증 통과한 새 dat bytes. `_state["d"]`는 교체 반영 상태로 남는다.

- [ ] **Step 1: 실패하는 테스트 추가**

`tests/test_core.py`에 추가:

```python
def test_build_noop_roundtrip(dat_bytes):
    import core
    core.load_dat(dat_bytes)
    out = core.build_dat("[]")
    before = json.loads(core.load_dat(dat_bytes))["rows"]
    after = json.loads(core.load_dat(bytes(out)))["rows"]
    assert before == after  # 무수정 빌드 → 내용 동일


def test_build_single_edit(dat_bytes):
    import core
    rows = json.loads(core.load_dat(dat_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 5)  # 기술 이름 하나
    edit = dict(target, v="테스트기술XYZ")
    out = core.build_dat(json.dumps([edit]))
    rows2 = json.loads(core.load_dat(bytes(out)))["rows"]
    hit = [r for r in rows2 if r["sec"] == 5 and r["idx"] == target["idx"]]
    assert hit[0]["v"] == "테스트기술XYZ"
    assert sum(1 for a, b in zip(rows, rows2) if a != b) == 1  # 다른 행 무변화


def test_build_hash_section_edit(dat_bytes):
    import core
    rows = json.loads(core.load_dat(dat_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 23)
    out = core.build_dat(json.dumps([dict(target, v="교체된 값")]))
    rows2 = json.loads(core.load_dat(bytes(out)))["rows"]
    hit = next(r for r in rows2 if r["sec"] == 23 and r["idx"] == target["idx"])
    assert hit["v"] == "교체된 값" and hit["k"] == target["k"]


def test_build_key_mismatch_rejected(dat_bytes):
    import core
    rows = json.loads(core.load_dat(dat_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 23)
    bad = dict(target, k="엉뚱한 원문", v="아무거나")
    with pytest.raises(ValueError):
        core.build_dat(json.dumps([bad]))
```

- [ ] **Step 2: 실패 확인**

Run: `python -m pytest tests/test_core.py -x -q`
Expected: FAIL — `AttributeError: module 'core' has no attribute 'build_dat'`

- [ ] **Step 3: build_dat 구현**

`core.py`에 추가 (빌드.py의 값-교체·왕복 검증 이식):

```python
def build_dat(edits_json):
    d = _state["d"]
    edits = json.loads(edits_json)
    hash_secs, list_edits = {}, []
    for e in edits:
        if e["sec"] != 0 and isinstance(d[e["sec"]], list):
            list_edits.append(e)
        else:
            hash_secs.setdefault((e["sec"], e.get("map")), []).append(e)

    for e in list_edits:
        obj = d[e["sec"]]
        if e["idx"] >= len(obj):
            raise ValueError(f"절{e['sec']}[{e['idx']}]: 범위 밖")
        obj[e["idx"]] = e["v"].encode("utf-8")

    for (sec, mi), es_ in hash_secs.items():
        oh = d[sec][mi] if sec == 0 else d[sec]
        keys, values = _inner(oh)
        for e in es_:
            j = e["idx"]
            if j >= len(keys):
                raise ValueError(f"절{sec}[{j}]: 범위 밖")
            if "k" in e and e["k"] != _dec(keys[j]):
                raise ValueError(f"절{sec}[{j}]: 원문 불일치 — 패치 버전이 다른 고침 파일일 수 있음")
            values[j] = e["v"].encode("utf-8")
        oh._private_data = rubywrite.dumps([keys, values])

    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    if len(r) != len(d):
        raise ValueError("왕복 검증 실패: 절 수 불일치")
    for sec in range(len(d)):
        if isinstance(d[sec], list):
            if r[sec] != d[sec]:
                raise ValueError(f"왕복 검증 실패: 절{sec}")
        elif hasattr(d[sec], "_private_data"):
            pairs = zip(r[sec], d[sec]) if sec == 0 else [(r[sec], d[sec])]
            for a, b in pairs:
                if _inner(a) != _inner(b):
                    raise ValueError(f"왕복 검증 실패: 절{sec}")
    return out
```

- [ ] **Step 4: 통과 확인**

Run: `python -m pytest tests/test_core.py -q`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add webapp
git commit -m "feat(webapp): core.build_dat — 값 교체·원문 대조·왕복 검증"
```

---

### Task 3: translate/build.py — __kr_patch__ 버전 표식

**Files:**
- Create: `pokemon-z/translate/VERSION` (내용: `v5`)
- Modify: `pokemon-z/translate/build.py` (adds 루프 뒤, 최종 dumps 앞)

**Interfaces:**
- Produces: korean.dat 절23 해시에 `__kr_patch__` 키, 값 `"{VERSION}|{YYYY-MM-DD}"`. 게임은 이 키를 조회하지 않으므로 무해. core.load_dat(Task 1)가 이 키를 meta로 읽는다.

- [ ] **Step 1: VERSION 파일 생성**

```bash
echo v5 > translate/VERSION
```

- [ ] **Step 2: build.py에 표식 삽입 코드 추가**

`main()` 안, `added` 집계 print 직전에 추가:

```python
    # 웹 스튜디오 제보용 버전 표식 — 게임은 이 키를 조회하지 않는다
    from datetime import date
    ver = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
    stamp = f"{ver}|{date.today()}".encode()
    obj = d[23]
    keys, values = inner_of(obj)
    kb = b"__kr_patch__"
    kidx = next((i for i, k in enumerate(keys) if bytes(k) == kb), None)
    if kidx is None:
        keys.append(kb)
        values.append(stamp)
    else:
        values[kidx] = stamp
    obj._private_data = rubywrite.dumps([keys, values])
```

- [ ] **Step 3: dry-run으로 검증**

Run: `cd translate && uv run build.py --dry-run`
Expected: `왕복 검증 통과` 출력, assert 없음 (표식 추가가 왕복 검증을 깨지 않음 확인)

- [ ] **Step 4: Commit**

```bash
git add translate/VERSION translate/build.py
git commit -m "feat: 빌드 시 korean.dat에 __kr_patch__ 버전 표식 심기"
```

---

### Task 4: index.html + app.js — 부트·폴더 선택·검색·수정 UI

**Files:**
- Create: `pokemon-z/webapp/index.html`
- Create: `pokemon-z/webapp/app.js`

**Interfaces:**
- Consumes: `core.load_dat`, `SECTION_NAMES`(Task 1).
- Produces: 전역 `S = {dir, rows, sha, meta, edits}` (edits: Map key `"sec:map:idx"` → {row 필드 + v}), `saveEdit(id)`, `persist()`, `toast(msg)`, `pyBuild(editsArr) -> Uint8Array`(Task 5가 사용), `SEC_LABEL` 절 이름표.

- [ ] **Step 1: index.html 작성**

CSS는 fixgui.py PAGE의 `<style>` 블록(translate/fixgui.py 60~100행대)을 그대로 복사하되, 셀렉터 추가 없이 사용. 구조:

```html
<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Z 한글패치 스튜디오</title>
<style>/* fixgui.py PAGE의 <style> 내용 전체 복사 */</style>
</head><body>
<header>
 <div class=logo>Z <b>한글패치 스튜디오</b></div>
 <div class=searchwrap>
  <input type=text id=q placeholder="문구 검색 — 한국어 번역 또는 원문" disabled>
  <select id=secf disabled><option value="">전체 분류</option></select>
  <button class=primary id=searchbtn onclick=search() disabled>검색</button>
 </div>
 <span id=dirty></span>
 <button id=buildbtn onclick=build() disabled>빌드 → 게임 반영</button>
 <button class=ghost id=exportbtn onclick=exportFix() disabled>내보내기</button>
 <button class=ghost id=importbtn onclick=importFix() disabled>가져오기</button>
 <button class=ghost id=restorebtn onclick=restoreMenu() disabled>복원</button>
</header>
<main>
 <div class=meta id=meta>Chrome/Edge에서 열어주세요. 게임 폴더를 선택하면 시작됩니다.</div>
 <div id=out>
  <div class=empty>
   <p>포켓몬 Z 게임 폴더(안에 Data\korean.dat가 있는 폴더)를 선택하세요.</p>
   <button class=primary onclick=openFolder() id=openbtn>게임 폴더 선택</button>
   <p style="font-size:12.5px;color:var(--sub)">로그인·설치 없음 · 첫 로드만 수십 초(엔진 다운로드) ·
   원본은 korean.dat.bak으로 자동 보관됩니다</p>
  </div>
 </div>
</main>
<div id=toast></div>
<input type=file id=importfile accept=".jsonl" style="display:none">
<script src="https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"></script>
<script src="app.js"></script>
</body></html>
```

- [ ] **Step 2: app.js — pyodide 부트 + 폴더 선택 + 로드**

```js
// ─── 설정 (유지자가 채움) ─────────────────────────────
const REPORT_FORM = {
  id: "",          // 구글폼 ID — 비어 있으면 제보 버튼 숨김
  entries: { sec:"", idx:"", k:"", v:"", suggest:"", patch:"" },
};
const APP_VER = "studio-1";
const SEC_LABEL = {0:"맵 대사",1:"포켓몬 이름",2:"분류",3:"도감 설명",4:"폼",
 5:"기술 이름",6:"기술 설명",7:"도구 이름",8:"도구 복수형",9:"도구 설명",
 10:"특성 이름",11:"특성 설명",12:"타입",13:"트레이너 직함",14:"트레이너 이름",
 15:"대전 시작 대사",16:"승리 대사",17:"패배 대사",18:"지방",19:"장소 이름",
 20:"장소 설명",21:"맵 이름",22:"전화",23:"시스템 문구"};

const $ = id => document.getElementById(id);
const S = { dir:null, rows:[], sha:"", meta:null, edits:new Map(), py:null, core:null };
const rid = r => `${r.sec}:${r.map ?? -1}:${r.idx}`;

function toast(m, ms=2600){ const t=$('toast'); t.textContent=m; t.classList.add('show');
  clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove('show'), ms); }
function esc(s){ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

async function bootPy(){
  if (S.py) return S.py;
  $('meta').textContent = '엔진 로드 중... (첫 방문은 수십 초, 이후 캐시)';
  const py = await loadPyodide();
  // 파이썬 소스를 pyodide FS에 심는다
  const files = ["core.py","rubywrite.py",
    ...["__init__.py","reader.py","writer.py","classes.py","constants.py","utils.py"]
      .map(f=>"vendor/rubymarshal/"+f)];
  py.FS.mkdirTree('/app/rubymarshal');
  for (const f of files){
    const src = await (await fetch(f)).text();
    const dst = f.startsWith('vendor/') ? '/app/rubymarshal/'+f.split('/').pop() : '/app/'+f;
    py.FS.writeFile(dst, src);
  }
  py.runPython("import sys; sys.path.insert(0, '/app')");
  S.core = py.pyimport("core");
  S.py = py;
  return py;
}
// 주의: vendor/rubymarshal의 실제 파일 목록은 Task 1에서 확인한 것으로 교체할 것.

async function readFile(dir, path){
  let h = dir;
  const parts = path.split('/');
  for (const p of parts.slice(0,-1)) h = await h.getDirectoryHandle(p);
  const fh = await h.getFileHandle(parts.at(-1));
  return new Uint8Array(await (await fh.getFile()).arrayBuffer());
}
async function writeFile(dir, path, bytes){
  let h = dir;
  const parts = path.split('/');
  for (const p of parts.slice(0,-1)) h = await h.getDirectoryHandle(p);
  const fh = await h.getFileHandle(parts.at(-1), {create:true});
  const w = await fh.createWritable();
  await w.write(bytes); await w.close();
}
async function exists(dir, path){
  try { await readFile(dir, path); return true; } catch { return false; }
}

async function openFolder(){
  if (!window.showDirectoryPicker){ toast('이 브라우저는 지원하지 않아요 — Chrome/Edge로 열어주세요', 5000); return; }
  try { S.dir = await showDirectoryPicker({mode:'readwrite'}); } catch { return; }
  if (!await exists(S.dir, 'Data/korean.dat')){
    toast('선택한 폴더에 Data\\korean.dat가 없어요 — 게임 폴더를 선택해 주세요', 5000); return;
  }
  await bootPy();
  $('meta').textContent = '번역 데이터 읽는 중...';
  const dat = await readFile(S.dir, 'Data/korean.dat');
  // 순정 원본 1회 보존 — 이미 있으면 절대 덮어쓰지 않는다
  if (!await exists(S.dir, 'Data/korean.dat.bak')){
    await writeFile(S.dir, 'Data/korean.dat.bak', dat);
  }
  let msg = null;
  try { msg = await readFile(S.dir, 'Data/messages.dat'); } catch {}
  const res = JSON.parse(S.core.load_dat(S.py.toPy(dat), msg && S.py.toPy(msg)));
  S.rows = res.rows; S.sha = res.sha; S.meta = res.meta;
  restoreEdits();
  for (const id of ['q','secf','searchbtn','buildbtn','exportbtn','importbtn','restorebtn'])
    $(id).disabled = false;
  $('secf').innerHTML = '<option value="">전체 분류</option>' +
    Object.entries(SEC_LABEL).map(([s,l])=>`<option value=${s}>${l}</option>`).join('');
  $('meta').textContent = `${S.rows.length.toLocaleString()}행 로드 · 패치 ${S.meta ?? '(표식 없음 · '+S.sha+')'}` +
    (S.edits.size ? ` · 이어서 작업: 저장 ${S.edits.size}건 복원됨` : '');
  $('out').innerHTML = '<div class=empty>어색한 문구를 검색해 바로 고치세요.</div>';
  updateDirty();
}
```

- [ ] **Step 3: app.js — 검색·수정·localStorage 보존**

```js
let HITS=[], SHOWN=0; const STEP=50;
$('q')?.addEventListener('keydown', e=>{ if(e.key==='Enter') search(); });

function search(){
  const q = $('q').value.trim(); if(!q) return;
  const sec = $('secf').value;
  HITS = S.rows.filter(r =>
    (sec==='' || r.sec===+sec) &&
    ((r.v && r.v.includes(q)) || (r.k && r.k.includes(q))));
  SHOWN = 0;
  $('meta').textContent = `${HITS.length}행 매칭`;
  $('out').innerHTML = HITS.length ? '' : '<div class=empty>매칭되는 행이 없습니다.</div>';
  if (HITS.length) more();
}

function card(r, i){
  const id = rid(r), e = S.edits.get(id);
  const v = e ? e.v : r.v;
  return `<div class="card ${e?'saved':''}" id=card${i}>
    <span class=chip>${SEC_LABEL[r.sec]??('절'+r.sec)}</span>${r.map!=null?`<span class=chip>맵 ${r.map}</span>`:''}
    ${REPORT_FORM.id?`<button class=ghost style="float:right" onclick=report(${i})>🚩 제보</button>`:''}
    ${r.k?`<div class=es>${esc(r.k)}</div>`:''}
    <textarea id=v${i} data-orig="${esc(r.v)}"
      onkeydown="if(event.ctrlKey&&event.key==='Enter')save(${i})">${esc(v)}</textarea>
    <div class=rowbar>
      <button class=primary onclick=save(${i})>저장</button>
      <button class=ghost onclick="$('v'+${i}).value=$('v'+${i}).dataset.orig">원래대로</button>
      <span class=st id=st${i}></span>
    </div></div>`;
}
function more(){
  const frag = HITS.slice(SHOWN, SHOWN+STEP).map((r,k)=>card(r, SHOWN+k)).join('');
  SHOWN = Math.min(SHOWN+STEP, HITS.length);
  $('morebtn')?.remove();
  $('out').insertAdjacentHTML('beforeend', frag);
  if (SHOWN < HITS.length) $('out').insertAdjacentHTML('beforeend',
    `<button class=more id=morebtn onclick=more()>더 보기 (${HITS.length-SHOWN}행 남음)</button>`);
}

const MARKUP = /\\c\[\d+\]|\\[A-Za-z]+|\{\d+\}|<[^>]+>/g;
function save(i){
  const r = HITS[i], v = $('v'+i).value;
  const lost = (r.v.match(MARKUP)||[]).filter(t => !v.includes(t));
  if (lost.length && !confirm(`색·이름 코드가 사라졌어요: ${lost.join(' ')}\n지우면 화면이 깨질 수 있어요. 그래도 저장할까요?`))
    return;
  if (v === r.v) S.edits.delete(rid(r));
  else S.edits.set(rid(r), {sec:r.sec, map:r.map, idx:r.idx, k:r.k, v});
  persist(); updateDirty();
  $('st'+i).className='st ok'; $('st'+i).textContent='저장됨';
  $('card'+i).classList.add('saved');
  toast('저장됨 — [빌드]를 누르면 게임에 반영돼요');
}
function persist(){
  localStorage.setItem('edits:'+S.sha, JSON.stringify([...S.edits.values()]));
}
function restoreEdits(){
  S.edits = new Map();
  for (const e of JSON.parse(localStorage.getItem('edits:'+S.sha) ?? '[]'))
    S.edits.set(rid(e), e);
}
function updateDirty(){
  const d = $('dirty'), n = S.edits.size;
  d.style.display = n ? 'inline-block' : 'none';
  if (n) d.textContent = `저장 ${n}건 — 빌드 필요`;
}
```

- [ ] **Step 4: 수동 확인 (브라우저 스모크)**

```bash
cd pokemon-z/webapp && python3 -m http.server 8788
```

Windows Chrome에서 `http://localhost:8788` 열기(WSL 포트 공유). 확인 항목:
1. 폴더 선택 → 게임 폴더 지정 → 행 수·패치 표식이 meta 줄에 표시
2. `Data/korean.dat.bak` 생성 확인 (탐색기)
3. 검색 → 카드 표시 → 수정 → 저장 → 새로고침 후 같은 검색 시 수정값 유지(localStorage)
4. 마크업 코드(`\c[2]` 등) 삭제 시 confirm 경고

사용자에게 확인 요청하고 결과를 기다린다 (devbox는 headless — 실기 확인은 Windows 쪽).

- [ ] **Step 5: Commit**

```bash
git add webapp/index.html webapp/app.js
git commit -m "feat(webapp): 부트·폴더 선택·검색·수정 UI + localStorage 보존"
```

---

### Task 5: 빌드 버튼 + 이중 백업 + 복원

**Files:**
- Modify: `pokemon-z/webapp/app.js`

**Interfaces:**
- Consumes: `S`, `readFile/writeFile/exists`, `core.build_dat`(Task 2 — `_state`는 openFolder의 load_dat 호출로 채워져 있음).
- Produces: `build()`, `restoreMenu()`.

- [ ] **Step 1: 구현**

```js
async function build(){
  if (!S.edits.size){ toast('저장된 수정이 없어요'); return; }
  const b = $('buildbtn'); b.disabled = true; b.textContent = '빌드 중...';
  try {
    const out = S.core.build_dat(JSON.stringify([...S.edits.values()])).toJs();
    // 직전본 백업 → 본체 기록 (원본 .bak은 openFolder에서 이미 보존)
    const cur = await readFile(S.dir, 'Data/korean.dat');
    await writeFile(S.dir, 'Data/korean.dat.prev', cur);
    await writeFile(S.dir, 'Data/korean.dat', out);
    toast(`빌드 완료 (${S.edits.size}건 반영) — 게임을 재시작하면 보여요`, 4000);
  } catch (err) {
    toast('빌드 실패 — 파일은 그대로예요: ' + err.message, 6000);
  } finally {
    b.disabled = false; b.textContent = '빌드 → 게임 반영';
  }
}

async function restoreMenu(){
  const hasPrev = await exists(S.dir, 'Data/korean.dat.prev');
  const pick = prompt(
    `복원할 대상 번호를 입력하세요:\n 1 = 순정 원본(korean.dat.bak)` +
    (hasPrev ? `\n 2 = 직전 빌드 전(korean.dat.prev)` : ''), '1');
  const src = pick === '1' ? 'Data/korean.dat.bak' : pick === '2' && hasPrev ? 'Data/korean.dat.prev' : null;
  if (!src) return;
  await writeFile(S.dir, 'Data/korean.dat', await readFile(S.dir, src));
  toast('복원 완료 — 페이지를 새로고침해 다시 불러오세요', 5000);
}
```

- [ ] **Step 2: 수동 확인**

Task 4의 스모크 서버로: 1행 수정 → 빌드 → `korean.dat.prev` 생성 및 dat 갱신(수정 시각) 확인 → 게임 실행해 해당 문구 반영 실기 1회 → [복원] 1(원본) → dat가 .bak 내용으로 돌아감(크기 비교). 사용자 확인을 기다린다.

- [ ] **Step 3: Commit**

```bash
git add webapp/app.js
git commit -m "feat(webapp): 원버튼 빌드 + 이중 백업(.bak/.prev)·복원"
```

---

### Task 6: 고침 파일 내보내기 / 가져오기

**Files:**
- Modify: `pokemon-z/webapp/app.js`

**Interfaces:**
- Consumes: `S.edits`, `S.rows`, `persist/updateDirty/toast`.
- Produces: `exportFix()`, `importFix()`. 고침 파일 포맷: 1행 헤더 `{"app":APP_VER,"patch":meta|sha}` + 이후 행마다 `{"sec","map"?,"idx","k"?,"v"}` (S.edits 값 그대로).

- [ ] **Step 1: 구현**

```js
function exportFix(){
  if (!S.edits.size){ toast('내보낼 수정이 없어요'); return; }
  const lines = [JSON.stringify({app:APP_VER, patch:S.meta ?? S.sha}),
    ...[...S.edits.values()].map(e=>JSON.stringify(e))];
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([lines.join('\n')+'\n'], {type:'application/x-ndjson'}));
  a.download = `z-kr-고침-${new Date().toISOString().slice(0,10)}-${S.edits.size}건.jsonl`;
  a.click(); URL.revokeObjectURL(a.href);
  toast('고침 파일을 내려받았어요 — 커뮤니티에 첨부해 공유하세요');
}

function importFix(){
  $('importfile').onchange = async ev => {
    const f = ev.target.files[0]; ev.target.value = ''; if (!f) return;
    const lines = (await f.text()).split('\n').filter(Boolean).map(l=>JSON.parse(l));
    const head = lines[0]?.app ? lines.shift() : null;
    const byId = new Map(S.rows.map(r=>[rid(r), r]));
    let applied = 0, skipped = 0; const conflicts = [];
    for (const e of lines){
      const row = byId.get(rid(e));
      if (!row || (e.k && row.k !== e.k)){ skipped++; continue; }   // 원문 불일치 → 버전 다름
      const mine = S.edits.get(rid(e));
      if (mine && mine.v !== e.v){ conflicts.push({row, mine, theirs:e}); continue; }
      S.edits.set(rid(e), {sec:row.sec, map:row.map, idx:row.idx, k:row.k, v:e.v});
      applied++;
    }
    persist(); updateDirty();
    $('meta').textContent = `가져오기: ${applied}건 병합 · ${skipped}건 건너뜀(원문 불일치)` +
      (head?.patch && head.patch !== (S.meta ?? S.sha) ? ` · 주의: 다른 패치판(${head.patch})의 고침` : '');
    if (conflicts.length) showConflicts(conflicts); 
    else toast(`병합 완료 — ${applied}건. 빌드하면 반영돼요`, 4000);
  };
  $('importfile').click();
}

function showConflicts(cs){
  $('out').innerHTML = `<div class=meta>내 수정과 겹치는 ${cs.length}행 — 남길 쪽을 고르세요</div>` +
    cs.map((c,i)=>`<div class=card id=cf${i}>
      ${c.row.k?`<div class=es>${esc(c.row.k)}</div>`:''}
      <div class=rowbar><button class=primary onclick=pickConflict(${i},0)>내 것: ${esc(c.mine.v)}</button></div>
      <div class=rowbar><button onclick=pickConflict(${i},1)>가져온 것: ${esc(c.theirs.v)}</button></div>
    </div>`).join('');
  window._conflicts = cs;
}
function pickConflict(i, theirs){
  const c = window._conflicts[i];
  if (theirs) S.edits.set(rid(c.row), {sec:c.row.sec, map:c.row.map, idx:c.row.idx, k:c.row.k, v:c.theirs.v});
  persist(); updateDirty();
  $('cf'+i).style.opacity = .4; $('cf'+i).style.pointerEvents = 'none';
}
```

- [ ] **Step 2: 수동 확인**

브라우저에서: 2행 수정 → 내보내기 → localStorage 비우고(새 시크릿 창) 다시 로드 → 가져오기 → 2건 병합 표시·빌드 가능. 같은 행을 다르게 수정한 상태에서 가져오기 → 충돌 카드에서 선택 동작. 사용자 확인을 기다린다.

- [ ] **Step 3: Commit**

```bash
git add webapp/app.js
git commit -m "feat(webapp): 고침 파일 내보내기/가져오기 — 원문 대조 병합 + 충돌 선택"
```

---

### Task 7: 원버튼 제보 (구글폼 백그라운드 전송)

**Files:**
- Modify: `pokemon-z/webapp/app.js` (`report()` 추가 — 카드의 제보 버튼은 Task 4에서 이미 렌더)

**Interfaces:**
- Consumes: `REPORT_FORM`, `S.meta/S.sha`, `HITS`.
- Produces: `report(i)`. 유지자 선행 작업(수동): 구글폼 생성 — 단답 6문항(분류/자리/원문/현재 번역/제안·코멘트/패치 버전 — 전부 "필수 아님", 로그인 수집 끄기), 미리 채워진 링크에서 `entry.<숫자>` ID 6개를 추출해 `REPORT_FORM`에 기입.

- [ ] **Step 1: 구현**

```js
async function report(i){
  const r = HITS[i];
  const suggest = $('v'+i).value !== r.v ? $('v'+i).value
    : (prompt('제안 번역이나 한 줄 코멘트 (그냥 제보만 하려면 비워두세요)') ?? '');
  const fd = new FormData();
  const E = REPORT_FORM.entries;
  fd.append(E.sec, `${r.sec}:${SEC_LABEL[r.sec] ?? ''}`);
  fd.append(E.idx, `${r.map ?? ''}:${r.idx}`);
  fd.append(E.k, r.k ?? '');
  fd.append(E.v, r.v);
  fd.append(E.suggest, suggest);
  fd.append(E.patch, `${S.meta ?? 'hash:'+S.sha} / ${APP_VER}`);
  try {
    await fetch(`https://docs.google.com/forms/d/e/${REPORT_FORM.id}/formResponse`,
      {method:'POST', mode:'no-cors', body:fd});
    toast('제보를 보냈어요 — 고마워요! 다음 판에 반영을 검토합니다', 4000);
  } catch {
    toast('전송이 안 됐어요 — 인터넷 연결을 확인해 주세요', 5000);
  }
}
```

(웹앱 버전은 patch 필드에 합쳐 보낸다 — 별도 문항 불필요.)

- [ ] **Step 2: 폼 개설 + entry ID 기입**

수동: 유지자 구글 계정으로 폼 생성 → 6문항 → 설정에서 "이메일 수집 안 함"·"응답 1회 제한 없음" → 응답을 시트에 연결 → 보내기→미리 채워진 링크로 entry ID 확보 → `REPORT_FORM.id`·`entries` 기입.

- [ ] **Step 3: 실측 검증 (필수 — no-cors는 성공 확인 불가)**

브라우저에서 [제보] 클릭 → 구글 시트에 행 도달을 눈으로 확인. 패치 버전 칸에 `v5|…` 또는 `hash:…`가 실려 있는지 확인. 도달 실패 시 entry ID 재확인.

- [ ] **Step 4: Commit**

```bash
git add webapp/app.js
git commit -m "feat(webapp): 원버튼 제보 — 구글폼 no-cors 전송 + 패치 메타 동봉"
```

---

### Task 8: 배포 (GitHub Pages) + 안내 문서

**Files:**
- Create: `pokemon-z/webapp/publish.sh`
- Modify: `pokemon-z/share/수정법.txt` (웹 스튜디오 안내 추가)

**Interfaces:**
- Consumes: webapp/ 전체(정적 파일).
- Produces: 공개 repo `choneuny/z-kr-studio`, URL `https://choneuny.github.io/z-kr-studio/`.

- [ ] **Step 1: publish.sh 작성**

```bash
#!/usr/bin/env bash
# webapp/ 정적 파일을 공개 repo로 배포 — 번역표·게임 데이터는 절대 포함하지 않는다
set -euo pipefail
cd "$(dirname "$0")"
REPO=choneuny/z-kr-studio
TMP=$(mktemp -d)
gh repo view "$REPO" >/dev/null 2>&1 || gh repo create "$REPO" --public
git clone "https://github.com/$REPO" "$TMP" 2>/dev/null
rsync -a --delete --exclude .git --exclude tests --exclude publish.sh ./ "$TMP/"
cd "$TMP"
git add -A
git diff --cached --quiet || { git commit -m "deploy $(date +%F)"; git push origin HEAD; }
gh api "repos/$REPO/pages" -X POST -f 'source[branch]=main' -f 'source[path]=/' 2>/dev/null || true
echo "https://choneuny.github.io/z-kr-studio/"
rm -rf "$TMP"
```

- [ ] **Step 2: 배포 실행 + 실기 스모크**

```bash
chmod +x webapp/publish.sh && webapp/publish.sh
```

Pages URL을 Windows Chrome에서 열어 전 흐름 1회: 폴더 선택→검색→수정→빌드→게임 확인→제보→시트 도달. (localhost와 달리 https라 File System Access·폼 전송 모두 실환경 검증이 된다.) 사용자 확인을 기다린다.

- [ ] **Step 3: 수정법.txt에 안내 추가**

`share/수정법.txt` 맨 위 제목 블록 아래에 삽입:

```
[ 더 쉬운 길 — 웹 스튜디오 ]

아래 수동 편집 없이도, Chrome/Edge에서 이 주소를 열면 검색→수정→
빌드를 화면에서 바로 할 수 있습니다 (설치·로그인 없음):

    https://choneuny.github.io/z-kr-studio/

게임 폴더를 선택하면 원본이 korean.dat.bak으로 자동 보관되고,
오역을 발견하면 [제보] 버튼 한 번으로 제작자에게 전달됩니다.
```

- [ ] **Step 4: Commit**

```bash
git add webapp/publish.sh share/수정법.txt
git commit -m "feat(webapp): Pages 배포 스크립트 + 수정법 안내에 웹 스튜디오 추가"
```

---

## 남는 리스크 (실행 중 확인)

- rubymarshal wheel의 실제 모듈 파일 목록 — Task 1 Step 1에서 확인한 목록으로 Task 4 `bootPy`의 파일 배열을 맞출 것.
- pyodide `toPy(Uint8Array)` → 파이썬 쪽 `bytes()` 캐스팅은 core.py가 이미 `bytes(dat_bytes)`로 감싸므로 memoryview여도 동작. `build_dat` 반환 bytes는 JS에서 `.toJs()`로 Uint8Array화 — pyodide 버전에 따라 `{create_proxies:false}` 옵션이 필요하면 조정.
- v5 dat에는 표식이 없으므로 제보는 해시로 식별 — Task 3 이후 첫 배포판(v5.1 등)부터 표식이 실린다.

---

# 2차 작업 (실기 스모크 피드백, 2026-08-03)

스펙의 "2차 요구" 절 참조. 공통: 기존 app.js 구조·헬퍼 재사용, node --check + selfcheck 확장, 브라우저 실기는 사용자 대기. 영속 키 전환(Task 10)이 기반이므로 10→11→12 순서 고정, 9·13은 독립.

### Task 9: 폴더 핸들 보존·재연결

**Files:** Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- dirHandle을 IndexedDB(`kv` 오브젝트스토어, 키 `dirHandle`)에 저장(구조화 복제 가능).
- 시작 화면: 저장된 핸들이 있으면 [지난 폴더 다시 연결] 버튼 표시 → `handle.requestPermission({mode:'readwrite'})`가 'granted'면 openFolder의 로드 경로 재사용, 아니면 일반 폴더 선택으로 폴백.
- IndexedDB 헬퍼는 idbGet/idbSet 두 함수(promise 래퍼, ~15줄)로 최소화.

### Task 10: 순정 기준 키 + 이력 기록 + 메모

**Files:** Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- **기준 키 전환**: 로드 시 `Data/korean.dat.bak`이 있으면 그 파일의 sha 앞 12자를 `S.base`로, 없으면(방금 .bak을 만든 경우) 현재 dat sha. 이후 모든 localStorage 키는 `edits:<base>`·`hist:<base>`·`applied:<base>`(11에서 사용). 기존 `edits:<sha>` 키는 발견 시 1회 이전(마이그레이션 3줄).
- **이력 기록**: `hist:<base>`에 append-only JSON 배열. 이벤트: {t:ISO, type:'edit'|'memo'|'build'|'restore'|'import', ...} — edit는 {rid,k,old,new}, memo는 {rid,k,text}, build는 {n}, restore는 {src}. 기록 지점: save()/memo/build 성공/restoreMenu/importFix.
- **메모 UI**: 카드 rowbar에 메모 입력칸+[메모] 버튼(fixgui 스타일). 메모는 이력에만 쌓임(빌드에 안 들어감).
- **[이력] 버튼**(헤더): 최신순 카드 목록 — 시각·종류·내용, edit는 구→신 표시. 데이터는 새로고침·빌드 후에도 유지.

### Task 11: applied 집합 + 내보내기 개선

**Files:** Modify: `pokemon-z/webapp/app.js`

- 빌드 성공 시 edits를 비우는 대신 `applied:<base>`(Map 직렬화)로 병합 이동(같은 rid는 최신 우선).
- exportFix: applied+pending 합집합(같은 rid는 pending 우선)을 내보냄. 비었을 때만 "내보낼 수정이 없어요". 헤더 patch는 순정 표식/베이스 해시.
- 카드 렌더 시 applied 행은 'saved' 테두리 대신 옅은 "반영됨" 칩 표시(구분).
- dirty 표시는 pending만 집계(빌드 필요 여부의 의미 유지).

### Task 12: 제보 재배선 + 일괄 제보 + 아이콘

**Files:** Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- **필드 재정의(사용자 지시)**: 제안=사용자가 바꿔 저장한 번역, 코멘트=사용자 메모(프롬프트 입력 또는 해당 행 메모), 패치 버전=신규 문항(entry는 폼 추가 후 부모가 전달). REPORT_FORM.entries에 comment 추가, report()에서 patch를 새 entry로 이동.
- **빈 제보 차단**: 개별 제보 버튼은 해당 행에 수정(pending/applied) 또는 메모가 있을 때만 활성(없으면 disabled+title 안내). 제보 prompt 취소(null)는 전송 안 함(최종 리뷰 지적 흡수).
- **일괄 제보**: 헤더 [모아서 제보] — applied+pending 수정과 메모를 정리해 한 건 전송: 분류=`일괄 N건`, 제안=수정 덤프(행마다 `[분류] 원문 → 수정값`), 코멘트=메모 덤프, 각 30,000자 절단+"…이하 생략". 보낼 게 없으면 비활성.
- **홈 화면(사용자 지시)**: 검색 전/검색어 비움 시의 거대한 빈 #out을 홈으로 활용 — 로드 후 상태 요약(대기 수정 N건·반영됨 N건·메모 N건), 최근 이력 몇 줄, 그리고 할 수 있는 일 안내([모아서 제보]·[내보내기]·[이력] 각 한 줄 설명+바로가기 버튼). 1회성 토스트 안내는 쓰지 않는다. 검색 결과를 지우면 홈으로 복귀. 시각 디자인은 별도 세션 몫이므로 기존 card/chip 스타일 재사용 수준으로.
- **아이콘**: 🚩 등 이모지를 인라인 SVG 아이콘으로 교체(외부 리소스 금지). 시각 디자인 전반 손질은 별도 세션 몫 — 여기선 기능 배선만.
- 전송 후 토스트. 보낸 뒤에도 데이터는 지우지 않음(제보는 사본).

### Task 13: 복원 선택 카드

**Files:** Modify: `pokemon-z/webapp/app.js`

- restoreMenu()의 prompt() 제거 → `#out`에 선택 카드 2장(순정 원본/직전 빌드 전) + [취소]. .prev 없으면 해당 카드 비활성(회색, 사유 표시). 복원 실행 시 이력 기록(Task 10의 hist) + 완료 카드에서 [다시 불러오기] 버튼(loadCore 재호출로 새로고침 없이 복귀).

### Task 14: 일괄 바꾸기 모드 (사용자 요청 2026-08-03)

**Files:** Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- 헤더 [바꾸기] 버튼 → #out에 바꾸기 화면: 찾을 문구·바꿀 문구 입력(리터럴, 정규식 아님) + [미리보기].
- 미리보기: 매칭 행 목록 — 각 행에 바뀐 결과를 원문과 함께 표시(바뀌는 부분 강조), 행마다 체크박스(기본 체크), [모두 선택/해제], 상단에 "N행 매칭".
- [선택 적용]: 체크된 행만 save()와 같은 경로로 S.edits에 기록(CR 정규화·이력 기록 포함, 마크업 토큰 검사는 치환이 토큰을 건드린 행만 경고 후 제외 여부 확인).
- 배경: 메달→배지 일괄 치환이 '배지을' 같은 조사 오류 21곳을 남긴 사례 — 단순 모두 바꾸기가 아니라 행별 확인이 요구의 핵심.
- 검색 대상은 현재 값(pending 수정 반영된 값) 기준. 매칭 500행 상한(기존 검색과 동일한 감각), 초과 시 안내.

### Task 15: 찾아보기 모드 (맵별·분류별·화자별) + 축약 조인표 동봉 (사용자 승인 2026-08-03)

**Files:** Create: `pokemon-z/translate/make_speakers.py`, `pokemon-z/webapp/speakers.json`(생성물) / Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- **축약 조인표 생성기**(repo 쪽, 배포 안 됨): docs/research/map-speaker-join.jsonl.gz + translate/sprite-groups.json에서 fixgui.py의 ctx()와 같은 규칙(sprite stem→group)으로 {"maps": {"<맵번호>": {"name": 맵이름, "rows": {"<k 원문>": [화자, 분류]}}}} 형태 JSON 산출 → webapp/speakers.json. 원문 k는 이미 배포 dat에 있는 텍스트라 추가 노출 없음. 크기 확인해 필요시 화자·분류 문자열 테이블화로 압축.
- **웹앱 찾아보기**: 헤더 select(fixgui와 같은 「찾아보기…」) — 맵별(dat 0절 맵번호 + 21절 맵 이름, speakers.json 없어도 동작), 분류별(절 단위, 행 수 표시), 화자별/화자분류별(speakers.json 로드 성공 시에만 옵션 노출). 묶음 클릭 → 해당 행 목록(기존 카드 렌더 재사용, 500행 상한).
- speakers.json fetch 실패는 조용히 무시(찾아보기에서 화자 옵션만 사라짐) — 무설정 원칙 유지.
- 카드 칩에 화자 표시(있으면) — fixgui와 동일한 감각.

### Task 16: 내 수정 화면 — 저장분 재수정·취소 (사용자 요청 2026-08-04)

**Files:** Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- 헤더(또는 홈 바로가기) [내 수정]: 대기(pending) 수정 목록 — 행마다 원문(있으면)·수정값 표시, 인라인 편집(textarea+[저장], applyEdit 재사용), [취소](원래대로 = S.edits에서 제거 + hist 기록 + persist).
- 메모 목록 — 행마다 [삭제](hist에 memo-del 기록 또는 기존 memo 이벤트는 두고 목록에서만 제거하는 방식은 구현 판단 — 단, 삭제 후 일괄 제보·제보 코멘트에 다시 실리면 안 됨: 메모 저장 구조가 hist 파생이라면 별도 활성 메모 저장소로 승격 필요 여부 판단).
- 반영됨(applied) 목록 — 표시만(수정값·"반영됨" 칩). 취소 기능 없음(이미 dat에 반영 — 되돌리려면 해당 행을 검색해 재수정하는 안내 한 줄).
- 홈 화면 요약 칩에서 이 화면으로 바로가기.

### Task 17: 일괄 제보 행 단위화 + 제보자 해시 (사용자 지시 2026-08-04)

**Files:** Modify: `pokemon-z/webapp/app.js`

- **일괄 제보 행 단위화**: 한 건 덤프 대신 항목마다 개별 제출(수정 1건=시트 1행: 기존 개별 제보와 같은 필드 구성, 메모 1건=comment만 채운 1행). 분류 칸은 개별 제보와 동일하게 실제 절 이름 유지 — "일괄" 표기는 patch(메타) 칸에 붙인다(사용자 지시: 패치 버전 칸을 메타 칸으로 활용, 시트 문항명도 그쪽에서 변경). 순차 전송(no-cors POST 연발), 진행 토스트("N건 중 M건째..."), 완료 토스트. 실패는 감지 불가(no-cors)이므로 전송 시도 기준.
- **제보자 해시**: 최초 1회 crypto.randomUUID()를 localStorage('reporter')에 저장(로그인·지문 채집 없음 — 순수 난수라 기기·브라우저 단위 익명 식별). 모든 제보(개별·일괄)의 patch(메타) 필드 끝에 " / u:<앞8자>" 부착(일괄이면 " / 일괄"도 함께 — 최종 형태 예: "v5|2026-08-03 / studio-1 / u:ab12cd34 / 일괄") — 폼 문항 추가 없이 시트에서 contains 필터로 악성/고장 제보자 묶음 식별 가능. localStorage 초기화로 재발급되는 한계는 수용(간단함 우선).

### Task 18: 첫 로드 체감 개선 (사용자 피드백 2026-08-04 "너무 느려")

**Files:** Modify: `pokemon-z/webapp/app.js`, `pokemon-z/webapp/index.html`

- **엔진 선시동**: 페이지 로드 직후 bootPy()를 백그라운드로 시작(promise 저장, openFolder는 그 promise를 await — 중복 시동 없음, 기존 S.py 가드 활용). 폴더 고르는 시간 동안 pyodide 다운로드·시동이 겹쳐 체감 대폭 감소.
- **단계별 진행 표시**: meta 줄에 단계 표시 — "엔진 내려받는 중(첫 방문 1회)..." → "엔진 시동..." → "번역 데이터 읽는 중(3만 행)..." 각 단계 소요를 console.time으로도 남겨 다음 진단 재료화.
- **speakers.json 지연 로드 확인**: 부트 경로에서 로드하고 있으면 폴더 열기와 병렬로(await 배치 조정). 
- 측정 우선 — 실기에서 어느 단계가 지배적인지 콘솔 수치로 확인 후 추가 최적화 판단(성급한 최적화 금지).
