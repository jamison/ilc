from typing import Set
from ilc_core.types import LinkType

VALID_LINK_TYPES: Set[LinkType] = {
    "supports",
    "refutes",
    "equivalent",
    "depends_on",
}

SYMMETRIC_LINK_TYPES: Set[LinkType] = {
    "equivalent",
}

def validate_link_type(link_type: str) -> LinkType:
    if link_type not in VALID_LINK_TYPES:
        raise ValueError(f"Invalid link_type: {link_type}")
    return link_type  # type: ignore[return-value]

def is_symmetric(link_type: LinkType) -> bool:
    return link_type in SYMMETRIC_LINK_TYPES
