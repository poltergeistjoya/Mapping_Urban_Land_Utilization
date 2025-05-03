from pydantic import BaseModel


class MarkerPosition(BaseModel):
    lat: float
    lng: float
