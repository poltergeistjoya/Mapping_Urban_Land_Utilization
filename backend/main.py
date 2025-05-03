import structlog
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session
from models.tables import Base, Location, Place, WalkableEdge
from geoalchemy2.functions import ST_AsGeoJSON, ST_Within, ST_Intersects
from time import time
from shapely.geometry import mapping
import json
from pydantic_models import MarkerPosition

log = structlog.get_logger()
DATABASE_URL = "postgresql://postgres:password@localhost:5432/urban_utilization"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Connect tp PostGIS database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = Session(bind=engine)


# Dependancy to get a database session
# TODO Make dependancies.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root(db: Session = Depends(get_db)):
    locations = db.scalars(select(Location)).all()
    cities = [loc.name for loc in locations if "city" in loc.location_type]
    log.info("Sending cities to render homepage")
    return sorted(set(cities))


# TODO should this only give one location ... i dont know ....
@app.get("/locations/", response_class=ORJSONResponse)
def get_locations(name: str = Query(None), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Location.name, func.ST_AsGeoJSON(Location.geom)).where(
            Location.name == name
        )
    ).all()

    log.info(f"Retrieved locations from db", count=len(rows))

    return [
        {
            "name": row[0],
            "geometry": json.loads(row[1]),  # this will now be a parsed dict via orjson
        }
        for row in rows
    ]


@app.get("/place_types/")
def get_place_types(db: Session = Depends(get_db)):
    place_types = db.scalars(select(Place.place_type).distinct()).all()
    log.info(f"got place types {place_types}")
    return sorted(set(place_types))


@app.get("/places/", response_class=ORJSONResponse)
def get_places(place_type: str, location_name: str, db: Session = Depends(get_db)):
    t0 = time()
    # Get location polygon
    location = db.scalar(select(Location).where(Location.name == location_name))
    if not location:
        raise HTTPException(status_code=404, detail=f"{location_name} not found")
    # Find all places within that polygon
    places = db.execute(
        select(Place.name, Place.desc, ST_AsGeoJSON(Place.geom))
        .where(Place.place_type == place_type)
        .where(ST_Within(Place.geom, location.geom))
    ).all()
    log.info(f"Got {place_type} for {location_name}", duration=f"{time() - t0:.3f}s")
    return [
        {
            "name": place[0],
            "desc": place[1],
            "geometry": json.loads(place[2]),
        }
        for place in places
    ]


@app.get("/edges/", response_class=ORJSONResponse)
def get_edges(location_name: str, db: Session = Depends(get_db)):
    t0 = time()
    log.info("Received request", location_name=location_name)

    location = db.scalar(select(Location).where(Location.name == location_name))
    log.info("Fetched location", duration=f"{time() - t0:.3f}s")

    if not location:
        raise HTTPException(status_code=404, detail=f"{location_name} not found")

    current = location
    while "city" not in current.location_type:
        if not current.parent_location_id:
            log.error(
                error=ValueError,
                detail=f"No city parent found for {location.name}, {location.state}, with location types {location.location_type}",
            )
        current = db.scalar(
            select(Location).where(Location.id == current.parent_location_id)
        )
        if not current:
            log.error(
                error=ValueError,
                detail=f"Parent location id: {current.parent_location_id} not found for {current.name}, {current.state} ",
            )

    city = current
    city_id = city.id
    log.info("Resolved city", city_name=city.name, duration=f"{time() - t0:.3f}s")

    edges = db.scalars(
        select(func.ST_AsGeoJSON(WalkableEdge.geometry))
        .where(WalkableEdge.location_id == city_id)
        .where(func.ST_Intersects(WalkableEdge.geometry, location.geom))
    ).all()
    log.info(
        "Queried and serialized GeoJSON",
        count=len(edges),
        duration=f"{time() - t0:.3f}s",
    )

    return [
        {
            "type": "Feature",
            "geometry": json.loads(geojson),
            "properties": {},
        }
        for geojson in edges
    ]

@app.post("/isochrone-pt/")
def isochrone_pt(pos: MarkerPosition):
    log.info(f"Recieved isochrone center point: ({pos.lat}, {pos.lng})")

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
