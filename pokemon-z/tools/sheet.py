#!/usr/bin/env python3
"""제보 스프레드시트 조회·수정 CLI (유지자용, devbox 전용).

인증은 gcloud ADC(spreadsheets scope 포함) — 최초 1회만:
  gcloud auth application-default login \
    --scopes=https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/cloud-platform
(Sheets API는 rclone 기본 클라이언트·gcloud 기본 scope 둘 다에서 403이라 이 조합이 최소 경로.
 API 활성 프로젝트는 golden-tide-361608 — 2026-08-04 sheets.googleapis.com 켜 둠.)

  uv run tools/sheet.py tabs                 # 탭 목록·행수
  uv run tools/sheet.py rows <탭> [-n 20]    # 행 출력(TSV, 최근 n행)
  uv run tools/sheet.py set <탭> <A1> <값>   # 셀 수정(트리아지 표시 등)
"""
import json, os, subprocess, sys, urllib.parse, urllib.request

SHEET_ID = "1Lp1iW1icicc0plhilX3BnPa2k_mico43TNQfkKiMMiY"   # Z 한글패치 제보 시트
QUOTA_PROJECT = "golden-tide-361608"
GCLOUD = os.path.expanduser("~/google-cloud-sdk/bin/gcloud")
API = "https://sheets.googleapis.com/v4/spreadsheets"


def token():
    r = subprocess.run([GCLOUD, "auth", "application-default", "print-access-token"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("ADC 토큰이 없어요 — 위 docstring의 login 명령을 한 번 실행해 주세요.\n" + r.stderr.strip())
    return r.stdout.strip()


def call(path, method="GET", body=None):
    req = urllib.request.Request(
        f"{API}/{SHEET_ID}{path}", method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": "Bearer " + token(),
                 "X-Goog-User-Project": QUOTA_PROJECT,
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
