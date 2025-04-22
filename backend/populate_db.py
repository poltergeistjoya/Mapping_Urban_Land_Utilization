from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, inspect
from geoalchemy2.functions import ST_GeomFromText, ST_DWithin
from geoalchemy2.shape import from_shape
from backend.models.tables import Base, Location, Place
import structlog 
from sqlalchemy_utils import database_exists, create_database
from shapely.geometry import shape, Polygon, MultiPolygon, Point
from shapely.geometry.base import BaseGeometry

log = structlog.get_logger()
DATABASE_URL = "postgresql://postgres:password@localhost:5432/urban_utilization"

#set up the database connection
engine = create_engine(DATABASE_URL)
# if not database_exists(engine.url):
#     log.warning("Database not found, attempting creation ...")
#     create_database(engine.url)
#     log.info("Database created sucessfully")
    
# Base.metadata.create_all(bind=engine)

def ensure_all_tables(engine, Base):
    inspector = inspect(engine)

    existing_tables = set(inspector.get_table_names())
    declared_tables = set(Base.metadata.tables.keys())
    missing_tables = declared_tables - existing_tables

    if missing_tables:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info(f"Created missing tables: {sorted(missing_tables)}")
    else:

        log.info("All declared tables already exist. Nothing created.")


def populate_locations(session, rows, verbose=True):
    added = []
    skipped = []

    to_add = []
    for row in rows:
        name = row["name"]
        location_type = row["location_type"]
        state = row["state"]
        geom = row["geometry"]
        parent_id = row.get("parent_location_id") #default is None

        #normalize geometry
        if isinstance(geom,dict):
            geom = shape(geom)

        if not isinstance(geom, BaseGeometry):
            log.warning(f"Invalid geometry for {name}, {state}. Recheck geometry, skipping") 
            skipped.append(name)
            continue

        if not isinstance(geom, (Polygon, MultiPolygon)):
            log.warning(f"Skipping{name}, {state}, geometry is {geom.geom_type}, not Polygon/Multipolygon")
            skipped.append(name)
            continue

        geo_obj = from_shape(geom, srid=4326)

        #check for existence by name + state
        exists = session.scalar(select(Location).where(Location.name== name, Location.state ==state)) 

        if exists:
            skipped.append(name)
            if verbose:
                log.info(f"Skipped existing location:{name}, {state}")
            continue

        loc = Location(
            name = name, 
            location_type = location_type, 
            state = state,
            geom = geo_obj, 
            parent_location_id = parent_id
        )
        to_add.append(loc)
        added.append(name)

    session.add_all(to_add)
    session.commit()
    log.info("Added the following locations:\n" + "\n".join(f"• {loc.name}, {loc.state}" for loc in to_add))
    return added,skipped


def populate_places(session, rows, verbose=True):
    added = []
    skipped = []

    to_add = []
    for row in rows:
        name = row["name"]
        desc = row["desc"]
        place_type = row["place_type"]
        active = row["active"]
        year_added = row["year_added"]
        year_removed = row["year_removed"]

        location_id = row["location_id"]
        geom = row["geom"]

        #normalize geometry
        

        if not isinstance(geom, Point):
            log.warning(f"Skipping{name}, {desc}, geometry is {geom.geom_type}, not Point")
            skipped.append(name)
            continue

        geo_obj = from_shape(geom, srid=4326)

        #check for existence by place_type + geom
        exists = session.scalar(
            select(Place)
            .where(Place.place_type == place_type)
            .where(ST_DWithin(Place.geom, geo_obj, 0.00001))
        )

        if exists:
            skipped.append(name)
            if verbose:
                log.info(f"Skipped existing place:{name}, {place_type}, {geom}")
            continue

        place = Place(
            name = name, 
            desc = desc, 
            place_type = place_type, 
            active = active, 
            year_added = year_added, 
            year_removed = year_removed, 
            location_id = location_id, 
            geom = geo_obj
        )
        to_add.append(place)
        added.append(name)

    session.add_all(to_add)
    session.commit()
    log.info("Added the following places:\n" + "\n".join(f"• {place.name}, {place.place_type}" for place in to_add))
    return added,skipped

    
    
if __name__ == "__main__":
    # populate_db()
    pass
