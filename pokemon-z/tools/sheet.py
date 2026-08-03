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
"""
import json, os, subprocess, sys, urllib.parse, urllib.request

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
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
