# Mapping_Urban_Land_Utilization

make sure db is running first
then do the backend 
then the frontend

## Database 
Postgres + postgis (spatial) + pgrouting (routing)
## Data
~baltimore city limits https://data.baltimorecity.gov/datasets/8007e8f6bf09468ba2e5e68d172b91b1_0/explore?location=39.283657%2C-76.619543%2C10.96~ No good because its a LINESTRING not a POLYGON ? 

Trying census shapefiles, places, maryland https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2024&layergroup=Places 

nyc bouroughs api endpoint: "https://data.ci
tyofnewyork.us/resource/wh2p-dxnf.geojson"

stret vendor data:

baltimore:https://data.baltimorecity.gov/datasets/baltimore::food-vendor-locations-1/about
nyc: Trying to contact someone from the DOHMH to find this data ugh
overpass-turbo, look at wiki tags https://taginfo.openstreetmap.org/

public trash cans:
nyc: https://data.cityofnewyork.us/Environment/DSNY-Litter-Basket-Inventory/8znf-7b2c/about_data

walkable road networks:
osmnx 


potential
nyc: farmers markets
Baltimore: liquor Licenses


## TODO 
-[ ] Config file for all settings (batch size, database url, backend url, etc)
-[ ] add batching to populate functions in `populate_db.py`
-[ ] existence checks (either by row or forget it during insert and add deduping function)
-[ ] fix existence check for edges ON CONFLICT DO NOTHING 
-[ ] Pydantic models for routes 
-[ ] Async routes ?
-[ ] Add spatial partitioning (tiling)
-[ ] strange state stuff happens in frontend
-[ ] staten island/governers island dont have edges cuz they not a part of new york 
-[ ] tab image on frontend/public
-[ ] add intermediate nodes for more accurate isochrone (10-20 meter spacing)
-[ ] add allowed highway types to walkableEdge table (low priority)

## Deployment 
make sure you have pg routing 


WITH reachable AS (
  SELECT edge
  FROM pgr_drivingDistance(
    'SELECT row_number() OVER () AS id, source, target, cost, reverse_cost FROM routable_edges',
    37585185,
    1260
  )
  WHERE edge != -1
),
routable_with_id AS (
  SELECT row_number() OVER () AS id, source, target, key
  FROM routable_edges
),
matched_edges AS (
  SELECT rw.source AS u, rw.target AS v, rw.key
  FROM reachable r
  JOIN routable_with_id rw ON rw.id = r.edge
),
limited_edges AS (
  SELECT we.*
  FROM matched_edges me
  JOIN walkable_edges we
    ON we.u = me.u AND we.v = me.v AND we.key = me.key
  LIMIT 5
)
SELECT jsonb_build_object(
  'type', 'FeatureCollection',
  'features', jsonb_agg(
    jsonb_build_object(
      'type', 'Feature',
      'geometry', ST_AsGeoJSON(geometry)::jsonb,
      'properties', jsonb_build_object(
        'u', u,
        'v', v,
        'key', key,
        'length_m', length_m
      )
    )
  )
)
FROM limited_edges;


limited query to get edges from last night
