from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from models.locations import Base, Location
from geoalchemy2.functions import ST_AsGeoJSON

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

#Create tables if they don't exist 
Base.metadata.create_all(bind=engine)

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

#TODO make this into a {} so specific locs can be panned to 
@app.get("/locations/")
def get_locations(db: Session = Depends(get_db)):
    locations = db.scalars(select(Location)).all()

    return [
        {
            "id": loc.id,
            "name": loc.name, 
            "geometry": db.scalar(ST_AsGeoJSON(loc.geom)),
        }
        for loc in locations
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000, reload = True)
