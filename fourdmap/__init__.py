"""4DMap — four-axis inspection coordinate frame (4DM-WP-1.0).

Not a truth engine. Not Lumen. Not GIS. Not a Node Gate.
Author: Aziel Eliab only.
"""

from .card import CardError, digest, make_card, verify_card
from .ops import dispatch
from .scope import (
    AUTHOR,
    BUCKET,
    GUARDRAIL,
    LIMITATION,
    LIVE_OPS,
    MASTER33,
    PIPELINE,
    PRODUCT,
    PRODUCT_NAME,
    SPEC,
    ZION_CAP,
    __version__,
)

__all__ = [
    "AUTHOR",
    "BUCKET",
    "CardError",
    "GUARDRAIL",
    "LIMITATION",
    "LIVE_OPS",
    "MASTER33",
    "PIPELINE",
    "PRODUCT",
    "PRODUCT_NAME",
    "SPEC",
    "ZION_CAP",
    "__version__",
    "digest",
    "dispatch",
    "make_card",
    "verify_card",
]
