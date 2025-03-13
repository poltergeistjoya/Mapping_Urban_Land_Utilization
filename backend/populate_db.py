from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from geoalchemy2.functions import ST_GeomFromText
from models.locations import Base, Location
import structlog 
from sqlalchemy_utils import database_exists, create_database

log = structlog.get_logger()
DATABASE_URL = "postgresql://postgres:password@localhost:5432/urban_utilization"

#set up the database connection
engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    log.warning("Database not found, attempting creation ...")
    create_database(engine.url)
    log.info("Database created sucessfully")
    
Base.metadata.create_all(bind=engine)


def populate_db():
    session = Session(bind=engine)

    locations = [
        {
            "name": "Baltimore City",
            "geom": "POLYGON((-76.711 39.372, -76.529 39.372, -76.529 39.290, -76.711 39.290, -76.711 39.372))"
        },
        {
            "name": "Baltimore County",
            "geom": "POLYGON((-76.880 39.450, -76.400 39.450, -76.400 39.150, -76.880 39.150, -76.880 39.450))"
        }
    ]

    for loc in locations:
        #TODO check for unique polygon, not by city name
        exists  = session.scalar(select(Location).where(Location.name == loc["name"]))
        added = 0
        if not exists:
            new_location = Location(
                name = loc["name"],
                geom = ST_GeomFromText(loc["geom"], 4326)
            )
            session.add(new_location)
            added +=1
            log.info(f"Added: {loc['name']}")

    session.commit()
    session.close()
    log.info(f"added {added} new locations to locations table")
    
    
if __name__ == "__main__":
    populate_db()
