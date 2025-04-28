# Mapping_Urban_Land_Utilization

make sure db is running first
then do the backend 
then the frontend


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
-[ ] add allowed highway types to walkableEdge table
-[ ] existence checks (either by row or forget it during insert and add deduping function)
-[ ] fix existence check for edges ON CONFLICT DO NOTHING 
-[ ] Pydantic models for routes 
-[ ] Async routes 
-[ ] Add time for response in routes
-[ ] Add spatial partitioning (tiling)
