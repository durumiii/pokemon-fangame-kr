"""딱지를 뗀 마샬 판독 — 도구들이 예전처럼 바이트열을 받게 한다.

korean.dat의 문자열에는 UTF-8 인코딩 딱지(마샬 ivar `:E`)가 붙어 있다. 딱지가 붙으면
rubymarshal이 파이썬 `str`(또는 RubyString)을 돌려주는데, 도구들은 딱지 없던 시절에
쓰여 전부 `bytes(k)`로 감싼다 — 그 자리에서 TypeError로 죽는다(20파일 66자리).

읽는 자리 하나에서 딱지를 떼면 그 66자리를 한 글자도 고치지 않아도 된다. 쓰기는
`build.py`가 저장 직전에 `tag_utf8()`로 전체에 다시 붙이므로 산출물은 그대로 딱지판이다.

    from datread import load       # rubymarshal.reader의 load 자리에 그대로 넣는다

⚠ 딱지가 붙어 있었다는 사실 자체는 이 판독으로 알 수 없다. 그것이 필요한 자리는
rubymarshal을 직접 쓰고 스스로 판정한다(webapp/core.py의 `_looks_tagged`가 그 예다).
"""

from rubymarshal.reader import load as _load

__all__ = ["load"]


def _untag(o):
    if isinstance(o, list):
        return [_untag(x) for x in o]
    if isinstance(o, str):
        return o.encode("utf-8")
    # 딱지 붙은 문자열 객체(RubyString) — 속의 문자열만 꺼낸다
    text = getattr(o, "text", None)
    if isinstance(text, str):
        return text.encode("utf-8")
    return o


def load(fp, *a, **kw):
    """rubymarshal.reader.load와 같되, 문자열을 바이트열로 되돌려 돌려준다.

    해시 절(OrderedHash)의 속은 건드리지 않는다 — 도구들이 `_private_data`를
    이 load로 다시 파싱하므로 그때 같은 처리를 받는다.
    """
    return _untag(_load(fp, *a, **kw))


if __name__ == "__main__":                       # 자체검증: 실물 dat로 왕복
    import io
    from pathlib import Path

    DAT = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
    d = load(open(DAT, "rb"))
    keys, values = load(io.BytesIO(bytes(d[23]._private_data)))
    assert all(isinstance(k, (bytes, bytearray)) for k in keys[:200]), "절23 키가 바이트열이 아니다"
    sec = {bytes(k).decode("utf-8"): bytes(v).decode("utf-8") for k, v in zip(keys, values)}
    assert sec.get("Salir") == "나가기", f"조회 실패: {sec.get('Salir')!r}"
    assert isinstance(d[5][0], (bytes, bytearray)), "목록 절이 바이트열이 아니다"
    print(f"OK — 절23 {len(keys)}키 · 절5 {len(d[5])}행")
