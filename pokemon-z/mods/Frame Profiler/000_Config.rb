# Frame Profiler — 스터터링·프레임 저하 원인을 잡는 백그라운드 프로파일러.
# 게임 폴더의 profiler.log에 쌓인다. 값을 고치면 주입기를 다시 돌리고 게임 재시작:
#   uv run mod/z/inject.py

module FrameProfiler
  # 이보다 오래 걸린 프레임을 「느린 프레임」으로 한 줄씩 기록한다 (밀리초).
  # RMXP 기대 프레임은 40fps 기준 25ms — 50ms면 두 프레임을 먹은 것이다.
  SLOW_MS = 50

  # 이 프레임 수마다 요약 한 줄(평균·최대·느린 프레임 수)을 남기고 파일로 내보낸다.
  # 200프레임이면 40fps에서 약 5초. 파일 쓰기도 이 주기로만 일어난다.
  SUMMARY_FRAMES = 200

  # 로그 파일. 상대 경로는 게임 폴더(Game.exe 옆)에 떨어진다.
  LOG = "profiler.log"
end
