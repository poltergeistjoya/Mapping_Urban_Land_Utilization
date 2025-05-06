from dotenv import load_dotenv
import os
import structlog
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_AsGeoJSON, ST_Within
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from shapely.geometry import mapping
from time import time
import json
from pydantic_models import MarkerPosition
from isochrone_helpers import (
    snap_point_to_edge,
    get_isochrone_edges,
    get_polygon_and_places,
)

from models.tables import Location, Place, WalkableEdge

log = structlog.get_logger()
load_dotenv(dotenv_path=".env")
LOCAL_IP = os.getenv("LOCAL_IP")
DATABASE_URL = (
    "postgresql+asyncpg://postgres:yourpassword@localhost:5342/urban_utilization"
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{LOCAL_IP}:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Connect tp PostGIS database
engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, class_=AsyncSession, autoflush=False, bind=engine
)


# Dependancy to get a database session
# TODO Make dependancies.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    result = await db.scalars(select(Location))
    locations = result.all()
    cities = [loc.name for loc in locations if "city" in loc.location_type]
    log.info("Sending cities to render homepage")
    return sorted(set(cities))


# TODO should this only give one location ... i dont know ....
@app.get("/locations/", response_class=ORJSONResponse)
async def get_locations(name: str = Query(None), db: Session = Depends(get_db)):
    result = await db.execute(
        select(Location.name, func.ST_AsGeoJSON(Location.geom)).where(
            Location.name == name
        )
    )

    rows = result.all()

    log.info(f"Retrieved locations from db", count=len(rows))

    return [
        {
            "name": row[0],
            "geometry": json.loads(row[1]),  # this will now be a parsed dict via orjson
        }
        for row in rows
    ]


@app.get("/place_types/")
async def get_place_types(db: Session = Depends(get_db)):
    result = await db.scalars(select(Place.place_type).distinct())
    place_types = result.all()
    log.info(f"got place types {place_types}")
    return sorted(set(place_types))


@app.get("/places/", response_class=ORJSONResponse)
async def get_places(
    place_type: str, location_name: str, db: Session = Depends(get_db)
):
    t0 = time()
    # Get location polygon
    location = await db.scalar(select(Location).where(Location.name == location_name))
    if not location:
        raise HTTPException(status_code=404, detail=f"{location_name} not found")
    # Find all places within that polygon
    result = await db.execute(
        select(Place.name, Place.desc, ST_AsGeoJSON(Place.geom))
        .where(Place.place_type == place_type)
        .where(ST_Within(Place.geom, location.geom))
    )
    places = result.all()
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
async def get_edges(location_name: str, db: Session = Depends(get_db)):
    t0 = time()
    log.info("Received request", location_name=location_name)

    location = await db.scalar(select(Location).where(Location.name == location_name))
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
        current = await db.scalar(
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

    result = await db.scalars(
        select(func.ST_AsGeoJSON(WalkableEdge.geometry))
        .where(WalkableEdge.location_id == city_id)
        .where(func.ST_Intersects(WalkableEdge.geometry, location.geom))
    )
    edges = result.all()
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


@app.post("/isochrone-pt/", response_class=ORJSONResponse)
async def compute_isochrone_pt(pt: MarkerPosition, db=Depends(get_db)):
    time_limit_min = 15
    m_walked_min = 85
    cost_limit = time_limit_min * m_walked_min
    t0 = time()
    log.info("isochrone.request.received", lat=pt.lat, lng=pt.lng)

    snapped_point = await snap_point_to_edge(pt.lat, pt.lng, db)
    log.info(
        "isochrone.snap.complete",
        node_id=snapped_point.nearest_node,
        duration=f"{time() - t0:.3f}s",
    )

    snapped_point_geom = to_shape(snapped_point.interpolated_pt)
    log.info("Snapped Point", coordinates=snapped_point_geom.coords[:])
    node_geom = to_shape(snapped_point.nearest_node_geom)
    log.info("Nearest Node", coordinates=node_geom.coords[:])

    edges_result = await get_isochrone_edges(snapped_point, db, cost_limit=cost_limit)
    edges_geojson = edges_result.get("geojson")
    edges_geom = edges_result.get("geoms")
    if not edges_geom or all(g is None for g in edges_geom):
        log.error("No usable edge geometries returned")

    edge_ids = edges_result.get("edge_ids")

    log.info(
        "isochrone.edges.query.complete",
        feature_count=len(edges_geojson["features"]),
        duration=f"{time() - t0:.3f}s",
    )

    polygon_result = await get_polygon_and_places(
        edge_ids=edge_ids, db=db, place_types=["grocery_store"]
    )

    log.info(polygon_result)

    total_time = time() - t0
    log.info("isochrone.response.ready", total_duration=f"{total_time:.3f}s")

    return {
        "snapped_point": {
            "type": "Feature",
            "geometry": mapping(snapped_point_geom),
            "properties": {
                "start_vid": snapped_point.nearest_node,
                "description": "Point snapped to nearest edge",
            },
        },
        "nearest_node": {
            "type": "Feature",
            "geometry": mapping(node_geom),
            "properties": {
                "id": snapped_point.nearest_node,
                "description": "Closest graph node (for routing)",
            },
        },
        "edges": edges_geojson,
        "polygon": polygon_result["polygon"],
        "places": polygon_result["places"],
    }
    # return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
