#!/usr/bin/env python3
"""제보 스프레드시트 조회·수정 CLI (유지자용, devbox 전용).

인증: 서비스 계정 z-sheet@golden-tide-361608 impersonation.
gcloud 사용자 토큰(cloud-platform)으로 IAM Credentials API에서 spreadsheets scope
SA 토큰을 발급받는다 — 브라우저·키 파일 불요. 전제(2026-08-04 세팅 완료):
  · golden-tide-361608에 sheets/iamcredentials API 활성
  · Token Creator: durumi0020(폼·시트 소유, GitHub durumiii 연동)·choneunyw1(devbox gcloud 로그인) 둘 다
  · 제보 시트가 SA 이메일에 편집자로 공유돼 있어야 함(시트 소유 계정에서 1회)
(막다른 길 기록: rclone 기본 클라이언트=Sheets API 미활성 403,
 gcloud ADC 기본 클라이언트=spreadsheets scope 차단 — 실측.)

  uv run tools/sheet.py tabs                 # 탭 목록·행수
  uv run tools/sheet.py rows <탭> [-n 20]    # 행 출력(TSV, 최근 n행)
  uv run tools/sheet.py set <탭> <A1> <값>   # 셀 수정(트리아지 표시 등)
  uv run tools/sheet.py archive <탭> [--yes] # 내려받아 보관하고 시트를 비운다
  uv run tools/sheet.py upload <탭> <jsonl>  # jsonl을 새 탭으로 올린다(있으면 갈아엎음)

archive는 머리행만 남기고 응답행을 **삭제**한다(내용 지우기가 아니라 행 삭제).
지우기로 비우면 빈 행이 남아 폼이 그 아래에 이어 쓰고, 그래서 다음 응답이
7행부터 시작하는 일이 생긴다 — 행을 없애면 다시 2행부터 채워진다.
보관본은 docs/log/reports/<탭>.jsonl에 덧붙는다(머리행을 열쇠로 쓴 사전 + 보관 시각).
"""
import datetime, json, os, subprocess, sys, urllib.parse, urllib.request

SHEET_ID = "1Lp1iW1icicc0plhilX3BnPa2k_mico43TNQfkKiMMiY"   # Z 한글패치 제보 시트
SA = "z-sheet@golden-tide-361608.iam.gserviceaccount.com"
GCLOUD = os.path.expanduser("~/google-cloud-sdk/bin/gcloud")
API = "https://sheets.googleapis.com/v4/spreadsheets"


def token():
    r = subprocess.run([GCLOUD, "auth", "print-access-token"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("gcloud 로그인이 없어요 — gcloud auth login 후 다시요.\n" + r.stderr.strip())
    req = urllib.request.Request(
        f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{SA}:generateAccessToken",
        method="POST",
        data=json.dumps({"scope": ["https://www.googleapis.com/auth/spreadsheets"]}).encode(),
        headers={"Authorization": "Bearer " + r.stdout.strip(),
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["accessToken"]


def call(path, method="GET", body=None):
    req = urllib.request.Request(
        f"{API}/{SHEET_ID}{path}", method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + token(),
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"API 오류 {e.code}: {e.read().decode()[:500]}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tabs"
    if cmd == "tabs":
        meta = call("?fields=sheets.properties")
        for s in meta["sheets"]:
            p = s["properties"]
            print(f'{p["title"]}\t{p["gridProperties"]["rowCount"]}행\tgid={p["sheetId"]}')
    elif cmd == "rows":
        tab = sys.argv[2]
        n = int(sys.argv[sys.argv.index("-n") + 1]) if "-n" in sys.argv else 20
        vals = call(f"/values/{urllib.parse.quote(tab)}").get("values", [])
        head, rows = (vals[0], vals[1:]) if vals else ([], [])
        print("\t".join(head))
        for row in rows[-n:]:
            print("\t".join(c.replace("\n", "⏎") for c in row))
        print(f"— 총 {len(rows)}행 (머리행 제외)", file=sys.stderr)
    elif cmd == "set":
        tab, a1, value = sys.argv[2], sys.argv[3], sys.argv[4]
        rng = f"{tab}!{a1}"
        call(f"/values/{urllib.parse.quote(rng)}?valueInputOption=RAW",
             "PUT", {"range": rng, "values": [[value]]})
        print(f"{rng} ← {value}")
    elif cmd == "archive":
        tab = sys.argv[2]
        meta = call("?fields=sheets.properties")
        gid = next((s["properties"]["sheetId"] for s in meta["sheets"]
                    if s["properties"]["title"] == tab), None)
        if gid is None:
            sys.exit(f"그런 탭이 없어요: {tab}")
        vals = call(f"/values/{urllib.parse.quote(tab)}").get("values", [])
        head, rows = (vals[0], vals[1:]) if vals else ([], [])
        if not rows:
            sys.exit("보관할 응답행이 없어요")
        out = os.path.join(os.path.dirname(__file__), "..", "docs", "reports", tab + ".jsonl")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        stamp = datetime.datetime.now().isoformat(timespec="seconds")
        # 이미 보관한 것과 겹치면 건너뛴다 — 스튜디오 일괄 제보가 저장분 전체를
        # 다시 보내는 판(2026-08-05 이전)의 제보자가 있으면 같은 건이 또 올라온다
        # 겹침 판정 칸: 시각·「현재 번역」·패치 버전은 뺀다. 앞 제보를 반영해 빌드하면
        # 같은 자리의 「현재 번역」이 달라져서, 그걸 넣으면 같은 건이 겹침으로 안 잡힌다.
        KEYCOLS = ("분류", "자리", "원문", "제안", "코멘트")
        # 탭마다 칸이 다르다 — 행 단위 제보 탭엔 KEYCOLS가 있고, 일반 문제 제보 탭엔
        # (타임스탬프·종류·내용·패치 버전)뿐이다. 겹침 칸이 하나도 없으면 열쇠가
        # 빈 튜플이 되어 모든 행이 겹침으로 잡힌다(2026-08-05 실측: 새 제보 2행이
        # 보관 없이 시트에서만 지워졌다). 없으면 시각·판 표시만 뺀 전 칸으로 센다.
        keycols = [c for c in KEYCOLS if c in head] or \
                  [c for c in head if c not in ("타임스탬프", "패치 버전")]
        def key(rec):
            return tuple(rec.get(c, "") for c in keycols)
        seen = set()
        if os.path.exists(out):
            with open(out, encoding="utf-8") as f:
                seen = {key(json.loads(l)) for l in f if l.strip()}
        # 보관이 먼저 땅에 닿아야 지운다 — 파일을 닫은 뒤에 삭제를 부른다
        kept = dup = 0
        with open(out, "a", encoding="utf-8") as f:
            for row in rows:
                if not any(c.strip() for c in row):
                    continue          # 예전 「내용 지우기」가 남긴 빈 행 — 보관할 것이 없다
                rec = dict(zip(head, row + [""] * (len(head) - len(row))))
                if key(rec) in seen:
                    dup += 1
                    continue
                seen.add(key(rec))
                rec["_archived"] = stamp
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                kept += 1
        print(f"{kept}행을 {os.path.relpath(out)}에 보관했어요"
              + (f" (이미 보관한 {dup}행 건너뜀)" if dup else "")
              + (f" (빈 행 {len(rows) - kept - dup}개는 버림)" if kept + dup < len(rows) else ""))
        if "--yes" not in sys.argv:
            if input(f"시트 '{tab}'의 {len(rows)}행을 삭제할까요? [y/N] ").strip().lower() != "y":
                sys.exit("보관만 하고 시트는 그대로 뒀어요")
        call(":batchUpdate", "POST", {"requests": [{"deleteDimension": {"range": {
            "sheetId": gid, "dimension": "ROWS",
            "startIndex": 1, "endIndex": 1 + len(rows)}}}]})
        print(f"시트에서 {len(rows)}행을 지웠어요 — 다음 응답은 2행부터 쌓여요")
    elif cmd == "upload":
        tab, path = sys.argv[2], sys.argv[3]
        recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        if not recs:
            sys.exit("올릴 줄이 없어요")
        head = list(recs[0])
        values = [head] + [[str(r.get(c, "")) for c in head] for r in recs]
        meta = call("?fields=sheets.properties")
        gid = next((s["properties"]["sheetId"] for s in meta["sheets"]
                    if s["properties"]["title"] == tab), None)
        if gid is None:      # 새 탭
            call(":batchUpdate", "POST", {"requests": [{"addSheet": {"properties": {
                "title": tab, "gridProperties": {
                    "rowCount": len(values) + 10, "columnCount": len(head),
                    "frozenRowCount": 1}}}}]})
        else:                # 있으면 통째로 비우고 다시 쓴다
            call(f"/values/{urllib.parse.quote(tab)}:clear", "POST", {})
        call(f"/values/{urllib.parse.quote(tab)}!A1?valueInputOption=RAW", "PUT",
             {"range": f"{tab}!A1", "values": values})
        print(f"{len(recs)}행 × {len(head)}칸을 '{tab}' 탭에 올렸어요"
              f" ({'새 탭' if gid is None else '기존 탭 갈아엎음'})")
        print(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
