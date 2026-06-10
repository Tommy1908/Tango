from typing import NotRequired, TypedDict

# For excel processor or general count
class count_dict(TypedDict):
    name: str
    address: str
    count: int

# For geocoding or adding coordinates to count
class operation_dict(TypedDict):
    name: str
    address: str
    count: int
    coordinates: tuple[float, float] | None
    zone: NotRequired[list[str]]