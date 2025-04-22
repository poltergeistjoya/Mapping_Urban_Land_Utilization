import structlog
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from models.tables import Base, Location, Place
from geoalchemy2.functions import ST_AsGeoJSON, ST_Within

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
#Connect tp PostGIS database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind = engine)

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
    cities = [
        loc.name
        for loc in locations
        if "city" in loc.location_type
    ]
    return sorted(set(cities))

#TODO should this only give one location ... i dont know ....
@app.get("/locations/")
def get_locations(name: str = Query(None), db: Session = Depends(get_db)):
    query = select(Location).where(Location.name == name)
    locations = db.scalars(query).all()

    return [
        {
            "id": loc.id,
            "name": loc.name, 
            "geometry": db.scalar(ST_AsGeoJSON(loc.geom)),
        }
        for loc in locations
    ]

@app.get("/place_types/")
def get_place_types(db: Session = Depends(get_db)):
    place_types = db.scalars(select(Place.place_type).distinct())
    log.info(f"got place types {place_types}")
    return sorted(set(place_types))

@app.get("/places/")
def get_places(
    place_type:str, 
    location_name: str, 
    db: Session = Depends(get_db)
):
    #Get location polygon
    location = db.scalar(
        select(Location).where(Location.name==location_name)
    )
    if not location:
        raise HTTPException(status_code=404, detail=f"{location_name} not found")
    # Find all places within that polygon
    places = db.scalars(
        select(Place)
        .where(Place.place_type == place_type)
        .where(ST_Within(Place.geom, location.geom))
    ).all()

    return [
        {
            "id": place.id, 
            "name": place.name, 
            "desc": place.desc,
            "geometry": db.scalar(ST_AsGeoJSON(place.geom))
        }
        for place in places
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000, reload = True)
