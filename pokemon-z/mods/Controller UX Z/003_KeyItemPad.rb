# Controller UX Z — 필드에서 등록 아이템을 패드로 (Ruby 1.8.7)
# 원본(Scene_Map#update)은 가상 F5만 읽는데 기본 패드 매핑에 F5가 없다
# (F1 바인딩 표 실측 — JS0~5·9·10이 C·B·X·A·Y·Z·L·R에만 얹혀 있다).
# 필드 문맥에서 노는 가상 X(= 패드 X버튼)를 같은 조건으로 얹는다 — 회복의 X는
# 일시정지 메뉴 화면(Menu Mejorado) 안에서만, 도전과제의 X는 그 화면 안에서만
# 읽혀 충돌하지 않는다(가상 X 사용처 전수 확인). 키보드 F5는 그대로 산다.
class Scene_Map
  alias cux_update_keyitem update
  def update
    if Input.trigger?(Input::X) && $game_temp &&
       !$game_temp.message_window_showing && !$game_temp.transition_processing
      unless pbMapInterpreterRunning? or $game_player.moving?
        $PokemonTemp.keyItemCalling = true if $PokemonTemp
      end
    end
    cux_update_keyitem
  end
end
