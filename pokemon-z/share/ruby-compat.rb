# 신구 루비 호환 심 (Z-32) — 없는 API만 채운다. 있으면 한 줄도 안 걸린다.
# 옛 실행기(1.8.7)에는 신형 API를, 신형 실행기(mkxp-z 루비 3.1+ 등)에는 1.8 API를.
# 문법은 1.8.7과 3.x의 공통 부분집합만 쓴다. patch_ruby_compat.py가 코어 맨 앞
# 섹션으로 넣는다. 근거 목록: docs/log/research/2026-08-09-ruby-compat-sweep.md

if ![].respond_to?(:nitems)
  class Array
    def nitems
      count { |x| !x.nil? }
    end
  end
end

if !File.respond_to?(:exists?)
  def File.exists?(path)
    exist?(path)
  end
end

if !Dir.respond_to?(:exists?)
  def Dir.exists?(path)
    exist?(path)
  end
end

if !Thread.respond_to?(:critical)
  # 1.8의 전역 임계 플래그. 신형 루비에 스레드 중단 개념이 없으니 조용히 삼킨다 —
  # 이 게임의 쓰임새(BitmapCache·Audio의 잠금 흉내)에는 그걸로 충분하다.
  def Thread.critical
    false
  end
  def Thread.critical=(value)
    value
  end
end

if !defined?(Fixnum)
  Fixnum = Integer
end
if !defined?(Bignum)
  Bignum = Integer
end

if !"".respond_to?(:getbyte)
  # 일부 모바일 실행기(RPG Player 실측)는 1.9 문자열 의미론인데 getbyte가 없다.
  class String
    def getbyte(i)
      unpack("C*")[i]
    end
  end
end
