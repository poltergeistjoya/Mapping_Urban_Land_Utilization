from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, inspect
from geoalchemy2.functions import ST_GeomFromText
from geoalchemy2.shape import from_shape
from backend.models.locations import Base, Location
import structlog 
from sqlalchemy_utils import database_exists, create_database
from shapely.geometry import shape, Polygon, MultiPolygon
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
        Base.metadata.create_all(bind=engine)
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
    
    
if __name__ == "__main__":
    # populate_db()
    pass
