# qa-trainerloc.rb 전용 러너 — 예외가 나도 거기까지의 기록을 남긴다.
#
# 돌리는 법(구판 루비 시험대는 packaging 지침 「구판 루비에서 한 줄 재는 법」):
#   1. 이 파일과 qa-trainerloc.rb 를 D:/ztest/ 에 ztrloc-runner.rb·ztrloc.rb 이름으로 둔다.
#   2. D:/ztest/rundir/mkxp.json 의 customScript 를 러너 쪽으로 바꾼다.
#   3. powershell.exe -NoProfile -Command "Start-Process -FilePath 'D:\ztest\rundir\Game.exe'
#      -WorkingDirectory 'D:\ztest\rundir' -Wait"
#   4. 결과는 D:/ztest/ztrloc_out.txt. **customScript 를 syntax.rb 로 되돌려 놓는다.**
$out = []
def log(s); $out << s.to_s; end
def flush!
  fp = File.open("D:/ztest/ztrloc_out.txt", "wb")
  fp.write($out.join("\n") + "\n"); fp.flush; fp.close
end
begin
  src = File.open("D:/ztest/ztrloc.rb", "rb") { |f| f.read }
  eval(src, TOPLEVEL_BINDING, "ztrloc.rb")
rescue Exception => e
  log "!! #{e.class}: #{e.message}"
  (e.backtrace || [])[0, 12].each { |b| log "   #{b}" }
end
flush!
Kernel.exit!
