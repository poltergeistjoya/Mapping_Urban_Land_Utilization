from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

ALLOWED_LOCATION_TYPES = {"city", "county", "district", "neighborhood"}
class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    location_type = Column(ARRAY(String), nullable=False)
    state = Column(String(2), nullable=False)
    parent_location_id = Column(Integer, ForeignKey("locations.id"), nullable = True)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326), nullable =False)

    parent = relationship("Location", remote_side = [id])

    def __init__(self, **kwargs):
        types = kwargs.get("location_type", [])
        types = list(dict.fromkeys(types)) #dedupe
        
        if not set(types).issubset(ALLOWED_LOCATION_TYPES):
            name = kwargs.get("name", [])
            state = kwargs.get("state", [])
            raise ValueError(f"Invalid location types: {types} in location {name}, {state}")
        
        kwargs["location_type"] = types 
        super().__init__(**kwargs)
