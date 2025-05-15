# Abstract 
Originally, this project was meant to map underutilized land in Baltimore and NYC through a measure of human activity via social media posts. Due to the lack of available data, underutilized land was instead mapped through available resources in the cities such as grocery stores, trash cans, and street vendors, as well as a function of walkability. The main functionality of the app is to generate isochrones for any point within New York City or Baltimore, find the walkable distance within a user-specified time range, and identify grocery stores, street vendors, or trash cans within that walkable distance. 

## Changes from Original Plan
The app can be used to show underutilized land in a selected city, but not as a metric of human activity; instead as a metric of available city resources. The main way it does so is by mapping specific resources within a city. The more interesting functionality it provides is the walkability isochrone, which can measure how well the land is utilized at a specific point in a city, but not the city itself unless some sampling was done over the whole dataset. The schema has changed to include a `walkable_edges` table to support the isochrone functionality and was made compatible with the `pgrouting` extension. Rather than having separate tables for each place type, all points that represent a `POINT(lat,long)` were fed into a `places` table for simplicity. The `cities` table was renamed to `locations`, and a column for `parent_id` was added to help reduce the size of some queries, though this optimization was not yet implemented. Additionally, my original schema did not show the spatial indexes on all geometry types, nor do my ORM definitions of said tables. However, for these queries to be efficient, there are GIST indexes on all `Polygon`, `Linestring`, and `Point` types through PostGIS. 

## Database and Description
The database has three main [tables](https://github.com/poltergeistjoya/Mapping_Urban_Land_Utilization/blob/main/backend/src/models/tables.py):
- `locations` (7 records)
- `places` (36,009 records)
- `walkable_edges` (1,128,854 records)

These are the three main entities used by the app, each representing distinct geometries used in different ways to query data: `multipolygon`, `point`, and `linestring`. In the future, I would partition the tables by region and Jinja template queries to make the tables smaller (especially for the `walkable_edges` table).

For a complete description of data sourcing, see the [README's Data Sources section](https://github.com/poltergeistjoya/Mapping_Urban_Land_Utilization?tab=readme-ov-file#data-sources). Data was mainly collected from city open data portals such as Open Baltimore and Open NYC, or OpenStreetMap—through the Overpass Turbo API for Baltimore trash cans, or OSMnx for the walkable road networks. The Census Places dataset was also used to find the polygons of counties and cities. All data was cleaned and made to fit the schema by creating an appropriate GeoDataFrame [(see README's Marimo section)](https://github.com/poltergeistjoya/Mapping_Urban_Land_Utilization?tab=readme-ov-file#using-marimo-notebook) and populated using the functions from [`populate_db.py`](https://github.com/poltergeistjoya/Mapping_Urban_Land_Utilization/blob/main/backend/src/populate_db.py).

## Functionality Description
The app can render map data for Baltimore and NYC and generate isochrones for both. Users can:
- Pick the city they are interested in
- View selected place types in their city
- Move a pin around to generate a walkability isochrone

The default walkability time is 15 minutes, but users can go up to about 100 minutes (though the query will be slow) and pick multiple place types to highlight in their returned isochrone. The most interesting queries of the app live in this functionality and can be found in [`isochrone_helpers.py`](https://github.com/poltergeistjoya/Mapping_Urban_Land_Utilization/blob/main/backend/src/isochrone_helpers.py). The queries to the database are driven by an async driver (`asyncpg`), so multiple users can use the app simultaneously; however, this functionality has not been load tested. 

## Known Bugs and Missing Features
There are several known bugs and features that I would have liked to implement given the time:
- There is no score/baseline to compare isochrones to. I would want to sample points in certain tiles (that span a mile or so) to get an idea of what points are above or below average in land utilization and walkability.
- The isochrone does not show all walkable points due to the presence of many widely spaced nodes.
- The frontend state can be buggy if too many requests are made on the UI.
- Street vendor data is not available for NYC (the city does not have enough workers to release it).
- Transit and school data were sourced but have not been populated into the database.
- The counties (boroughs) of NYC are populated in the database but are not being used in any queries—generally, each city was meant to be broken down into smaller polygons.
- The UI is incomplete—each `place_type` should have its own metadata table for better subclassing.
- The backend sends GeoJSON `ORJSONResponse` instead of MVT—geo data is large, so the MVT standard might help with latency on the app.

For a full description of how to run the project, see the README.

## Technical Highlight
The technical highlight of this project is the isochrone functionality. There were many challenges in getting this to work well:
- The network data was, by far, the largest data block on my page and terrible to render on the frontend.
- Since I was using SQL, I needed to use a SQL extension that allows for routing, and setting up the correct image to use `pgrouting` was difficult.
- Additionally, `pg_drivingdistance` requires specific columns. I attempted to make views from an early version of `walkable_edges` to satisfy `pg_drivingdistance`, but it was terribly slow, resulting in a refactor of the table.

Writing the queries in [`isochrone_helpers.py`](https://github.com/poltergeistjoya/Mapping_Urban_Land_Utilization/blob/main/backend/src/isochrone_helpers.py) to be low(ish) latency was the most interesting part. Originally, a 15-minute isochrone could take around 30 seconds to generate and render; now it can be as low as 7 seconds (for Baltimore). The key here was to:
1. Use rough bounding box filters
2. Approximate the polygon of the network returned, rather than trying to unionize each `LINESTRING` in the isochrone together
3. Use the `EXPLAIN ANALYZE` statement 

## Scaling
Right now, this is not very scalable at all. I would definitely:
1. Partition my tables by city and then name them so I can template the table names in my SQL queries easily
2. Due to the automatic spatial indexes on all geometry objects, any typical PostGIS statement is already pretty optimized. However, dividing the tables into smaller subclasses would help a lot, especially for place types since many tuples are returned on each search; it would be better to search a dedicated table for it
3. Create a tile system, keep every point in a tile, and make a tile index

## Conclusion
Overall, I learned a lot about geospatial data analysis, SQL, PostGIS, and `pgrouting`, as well as how to write efficient queries. I do have plans to work on this further because more data would make the experience of using the app more enriching. I would definitely implement:
1. A tiling system
2. Subclassed and Partitioned tables
3. MVT rendering

These changes would improve the app's latency. I would also add a statistical component comparing the resources available in a 15-minute walk of tiles to get an idea of how land is underutilized in whole cities, as opposed to just one point. 
