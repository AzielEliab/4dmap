from fourdmap.ops import cap
from fourdmap.scope import ZION_CAP


def test_zion_cap() -> None:
    out = cap({"score": 0.99})
    assert out["score"] == ZION_CAP
    assert out["capped"] is True
    assert cap({"score": 0.2})["score"] == 0.2
