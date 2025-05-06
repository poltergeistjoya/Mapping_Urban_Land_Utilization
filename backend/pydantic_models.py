from pydantic import BaseModel
from typing import List

class MarkerPosition(BaseModel):
    lat: float
    lng: float
    walkMinutes: int
    placeTypes: List[str]
