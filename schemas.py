from typing import TypedDict

# For excel processor or general count
class count_dict(TypedDict):
    hotel: str
    address: str
    count: int

# For geocoding or adding coordinates to count
class operation_dict(TypedDict):
    hotel: str
    address: str
    count: int
    coordinates: tuple[float, float] | None