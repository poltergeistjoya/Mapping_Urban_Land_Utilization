from sqlalchemy import (
    Column,
    Integer,
    String,
    ARRAY,
    ForeignKey,
    Boolean,
    BigInteger,
    Float,
    PrimaryKeyConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from . import Base

ALLOWED_LOCATION_TYPES = {"city", "county", "district", "neighborhood"}


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location_type = Column(ARRAY(String), nullable=False)
    state = Column(String(2), nullable=False)
    parent_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)

    parent = relationship("Location", remote_side=[id])

    def __init__(self, **kwargs):
        types = kwargs.get("location_type", [])
        types = list(dict.fromkeys(types))  # dedupe

        if not set(types).issubset(ALLOWED_LOCATION_TYPES):
            name = kwargs.get("name", [])
            state = kwargs.get("state", [])
            raise ValueError(
                f"Invalid location types: {types} in location {name}, {state}"
            )

        kwargs["location_type"] = types
        super().__init__(**kwargs)


ALLOWED_PLACE_TYPES = {
    "street_vendor",
    "trash_can",
    "grocery_store",
    "public_transit",
    "school",
}


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=True)
    place_type = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    year_added = Column(Integer)
    year_removed = Column(Integer, nullable=True)

    location_id = Column(
        Integer, ForeignKey("locations.id")
    )  # smallest location it is contained in
    geom = Column(Geometry("POINT"), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "place_type", "geom", name="uq_place_name_type_geom"),
    )

    def __init__(self, **kwargs):
        type = kwargs.get("place_type")

        if type not in ALLOWED_PLACE_TYPES:
            name = kwargs.get("name", "unknown")
            geom = kwargs.get("geom", "unknown")
            raise ValueError(f"Invalid place type: {type} in place {name}, {geom}")

        kwargs["place_type"] = type
        super().__init__(**kwargs)


class WalkableEdge(Base):
    __tablename__ = "walkable_edges"

    id = Column(
        Integer, primary_key=True, autoincrement=True, unique=True
    )

    u = Column(BigInteger, nullable=False)
    v = Column(BigInteger, nullable=False)
    key = Column(Integer, nullable=False, default=0)
    length_m = Column(Float, nullable=False)
    highway = Column(ARRAY(String), nullable=True)
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)

    location_id = Column(Integer, ForeignKey("locations.id"))

    __table_args__ = (
        UniqueConstraint("u", "v", "key", name="uq_u_v_key"),
        Index("idx_walkable_edges_geom", "geom", postgresql_using="gist"),
    )
