# Controller UX Z — 이름 입력(키보드 타이핑 화면)에 패드 확인·취소 (Ruby 1.8.7)
# 원본(TextEntry, PokemonEntryScene#pbEntry1)은 완료가 키보드 RETURN 직독뿐이라
# 패드 확인 버튼(가상 C = JS0 = 패드 A)이 안 닿는다. 메서드 재정의(나중 정의가
# 이긴다)로 가상 C 확인·가상 B 취소를 더한다. RETURN·ESC 경로는 원문 그대로.
#
# 가드: 같은 프레임에 입력창 텍스트가 변했으면 가상 버튼을 무시한다 — 가상 C의
# 키보드 바인딩(Space·C)과 가상 B의 바인딩(X)이 이름에 들어가는 글쇠라, 가드가
# 없으면 그 글자를 치는 순간이 곧 확정·취소가 된다(F1 기본 바인딩 표 실측).
class PokemonEntryScene
  def pbEntry1
    ret = ""
    loop do
      Graphics.update
      Input.update
      if Input.triggerex?(:ESCAPE) && @minlength == 0
        ret = ""
        break
      end
      if Input.triggerex?(:RETURN) && @sprites["entry"].text.length >= @minlength
        ret = @sprites["entry"].text
        break
      end
      before = @sprites["entry"].text
      @sprites["helpwindow"].update
      @sprites["entry"].update
      @sprites["subject"].update if @sprites["subject"]
      if @sprites["entry"].text == before
        if Input.trigger?(Input::C) && before.length >= @minlength
          ret = before
          break
        end
        if Input.trigger?(Input::B) && @minlength == 0
          ret = ""
          break
        end
      end
    end
    Input.update
    return ret
  end
end
