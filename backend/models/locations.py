from sqlalchemy import Column, Integer, String 
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False, unique=True)
    geom = Column(Geometry("POLYGON", srid=4326), nullable =False, index = True)
