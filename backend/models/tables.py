from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey, Boolean, Index, text
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

    ## Attempt to put index on geom, but getting (psycopg2.errors.DuplicateTable) relation "idx_locations_geom" already exists
    # __table_args__ = (
    #     Index("idx_locations_geom", "geom", postgresql_using="gist"),
    #     )
    
    def __init__(self, **kwargs):
        types = kwargs.get("location_type", [])
        types = list(dict.fromkeys(types)) #dedupe
        
        if not set(types).issubset(ALLOWED_LOCATION_TYPES):
            name = kwargs.get("name", [])
            state = kwargs.get("state", [])
            raise ValueError(f"Invalid location types: {types} in location {name}, {state}")
        
        kwargs["location_type"] = types 
        super().__init__(**kwargs)

ALLOWED_PLACE_TYPES = {"street_vendor"}
class Place(Base):
    __tablename__ ="places"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    place_type = Column(String, nullable=False)
    active=Column(Boolean, default=True)
    year_added = Column(Integer)
    year_removed = Column(Integer, nullable=True)

    location_id = Column(Integer,ForeignKey("locations.id")) #smallest location it is contained in
    geom = Column(Geometry("POINT"))

    ## Attempt to put index on geom, but getting (psycopg2.errors.DuplicateTable) relation "idx_places_geom" already exists 
    # __table_args__ = (
    #     Index("idx_places_geom", "geom", postgresql_using="gist"),
    #     #rows with place_type are unique if more than a meter apart
    #     Index("uq_place_type_geom", "place_type", text("ST_AsText(ST_SnaptoGrid(geom, 0.00001))"), unique=True) 
    # )
    
