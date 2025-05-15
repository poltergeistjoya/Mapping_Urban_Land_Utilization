# Mapping Urban Land Utilization

A web application for visualizing and analyzing urban land utilization patterns using geographical data.

## Required Ports

The following ports need to be available on your machine:
- `5173`: Frontend development server
- `8000`: Backend API server
- `5342`: PostgreSQL database (mapped from container port 5432)

If any of these ports are already in use, you'll need to either:
1. Stop the service using the port
2. Or modify the port mappings in `docker-compose.yml`

## Prerequisites

- Docker and Docker Compose
- PostgreSQL dump file (`recent_dump.sql`) for initial data
- Running PostgreSQL database (for Marimo notebook)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Mapping_Urban_Land_Utilization.git
cd Mapping_Urban_Land_Utilization
```

2. Contact joyabutterfly@gmail.com to request:
   - The `recent_dump.sql` file for initial database setup
   - Sample data files for running the Marimo notebook

3. Place the `recent_dump.sql` file in the project root directory

4. Start the application:
```bash
docker compose up
```

5. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Data Sources and Processing

### Using Marimo Notebook

The project includes a Marimo notebook for data exploration and cleaning. To run it:

1. Install the data normalization dependencies using uv (make sure you're in the project root):
```bash
uv pip install --group normalize-data
```

2. Start the notebook:
```bash
marimo edit location_geojsons.py
```

3. The notebook will open in your browser. Use it to:
   - Explore and clean geographical data
   - Generate GeoJSON files
   - Prepare data for database import
   - Access the same database as the Docker setup (using the same environment variables)

Note: This installs all data normalization dependencies including Marimo, geopandas, osmnx, and other required packages.

### Data Sources

| Data Type | Source | Link | Notes |
|-----------|--------|------|-------|
| City Boundaries | Census Bureau | https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2024&layergroup=Places | Maryland places shapefiles |
| NYC Boroughs | NYC Open Data | https://data.cityofnewyork.us/resource/wh2p-dxnf.geojson | Borough boundaries |
| Street Vendors (Baltimore) | Baltimore Open Data | https://data.baltimorecity.gov/datasets/baltimore::food-vendor-locations-1/about | Food vendor locations |
| Street Vendors (NYC) | NYC DOHMH | - | Contact required |
| Public Trash Cans (NYC) | NYC Open Data | https://data.cityofnewyork.us/Environment/DSNY-Litter-Basket-Inventory/8znf-7b2c/about_data | DSNY inventory |
| Public Trash Cans (Baltimore) | OpenStreetMap | - | Via Overpass Turbo |
| Grocery Stores (Baltimore) | Baltimore Open Data | https://data.baltimorecity.gov/maps/baltimore::grocery-stores | Store locations |
| Grocery Stores (NYC) | NY State Data | https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj/about_data | Retail food stores |
| Schools (Baltimore) | Baltimore Open Data | https://data.baltimorecity.gov/datasets/baltimore::baltimore-city-schools/explore | City schools |
| Schools (NYC) | NYC Open Data | https://data.cityofnewyork.us/Education/2019-2020-School-Locations/wg9x-4ke6/about_data | Public school locations |
| Public Transit (Baltimore) | MTA Maryland | https://www.mta.maryland.gov/developer-resources | GTFS data available |
| Public Transit (NYC) | MTA | https://www.mta.info/developers | GTFS for subway, LIRR, Metro North, Bus |
| Road Networks | OSMnx | - | Walkable road networks |
| Farmers Markets (NYC) | - | - | To be added |
| Liquor Licenses (Baltimore) | - | - | To be added |

## TODO

1. Configuration
   - [ ] Create config file for all settings (batch size, database url, backend url, etc)
   - [ ] Add batching to populate functions


2. Backend Improvements
   - [ ] Add Pydantic models for routes
   - [ ] Add spatial partitioning (tiling)
   - [ ] Add intermediate nodes for more accurate isochrones (10-20 meter spacing)

3. Frontend Enhancements
   - [ ] Fix state management issues
   - [ ] Add favicon in frontend/public
   - [ ] Move styling to CSS
   - [ ] Fix Staten Island/Governors Island edge cases

4. Data Processing
   - [ ] Add private schools data
   - [ ] Integrate ferry service data for NYC
   - [ ] Add farmers markets data for NYC
   - [ ] Add liquor licenses data for Baltimore
   - [ ] Add street vendor data

## Development

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + PostGIS
- Database: PostgreSQL with PostGIS extension

## Project Structure

```
.
├── backend/           # FastAPI backend
│   └── src/          # Backend source code
├── frontend/         # React frontend
├── location_geojsons.py  # Marimo notebook for data processing
├── docker-compose.yml    # Docker services configuration
└── recent_dump.sql   # Initial database data
```

## Troubleshooting

- If the frontend can't connect to the backend, ensure both services are running:
  ```bash
  docker compose ps
  ```
- Check backend logs:
  ```bash
  docker compose logs backend
  ```
- Check frontend logs:
  ```bash
  docker compose logs frontend
  ```

## Database 
Postgres + postgis (spatial) + pgrouting (routing)
## Data
~baltimore city limits 

Trying census shapefiles, places, maryland https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2024&layergroup=Places 

nyc bouroughs api endpoint: "https://data.ci
tyofnewyork.us/resource/wh2p-dxnf.geojson"

stret vendor data:

baltimore:https://data.baltimorecity.gov/datasets/baltimore::food-vendor-locations-1/about
nyc: Trying to contact someone from the DOHMH to find this data ugh
overpass-turbo, look at wiki tags https://taginfo.openstreetmap.org/

public trash cans:
nyc: https://data.cityofnewyork.us/Environment/DSNY-Litter-Basket-Inventory/8znf-7b2c/about_data
baltimore: from overpass turbo 

grocery stores:
baltimore: https://data.baltimorecity.gov/maps/baltimore::grocery-stores 
nyc: https://data.ny.gov/Economic-Development/Retail-Food-Stores/9a8c-vfzj/about_data 

schools:
baltimore: https://data.baltimorecity.gov/datasets/baltimore::baltimore-city-schools/explore?location=39.296028%2C-76.620343%2C11.38 
nyc: https://data.cityofnewyork.us/Education/2019-2020-School-Locations/wg9x-4ke6/about_data 

https://data.cityofnewyork.us/Education/NYC-DOE-Public-School-Location-Information/3bkj-34v2/about_data outdated? Has less schools? but maybe that means its more up to date?

public_transit 
baltimore: https://data.baltimorecity.gov/datasets/2272d1a39c214ae8a1ac3807b1108ba9_0/explore?location=39.285736%2C-76.612584%2C11.34 ... https://www.mta.maryland.gov/developer-resources 
nyc: https://www.mta.info/developers (all GTFS for subway, LIRR, Metro North, Bus) No ferry service though

neither include private schools? 
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
-[ ] add node table for more accurate isochrone + figure out how to optimize that and make it fast
-[ ] move styling to css 

## Deployment 
make sure you have pg routing 


