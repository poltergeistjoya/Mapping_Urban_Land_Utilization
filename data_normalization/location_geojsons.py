import marimo

__generated_with = "0.12.10"
app = marimo.App(width="medium")


@app.cell
def _(__file__):
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import mapping 
    from geoalchemy2.shape import from_shape
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    import sys
    import pathlib 

    #to import other packages
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
    from backend.models.locations import Location, Base
    from backend.populate_db import engine, ensure_all_tables, populate_locations
    return (
        Base,
        Location,
        Session,
        create_engine,
        engine,
        ensure_all_tables,
        from_shape,
        gpd,
        mapping,
        pathlib,
        pd,
        populate_locations,
        sys,
    )


@app.cell
def _():
    GEOJSON_DIR = "../random_data/geojsons/"
    SHPFILE_DIR = "../random_data/shapefiles/"
    return GEOJSON_DIR, SHPFILE_DIR


@app.cell
def _(GEOJSON_DIR, SHPFILE_DIR, gpd):
    maryland_census_places = gpd.read_file(SHPFILE_DIR + "maryland_places_2024_census.shp")
    nyc_boroughs = gpd.read_file(GEOJSON_DIR + "nyc_boroughs.geojson")
    nyc_boroughs.head()
    return maryland_census_places, nyc_boroughs


@app.cell
def _(maryland_census_places):
    baltimore = maryland_census_places[maryland_census_places["NAME"].str.lower() == "baltimore"]
    baltimore.plot()
    return (baltimore,)


@app.cell
def _(nyc_boroughs):
    nyc_city_geom = nyc_boroughs.geometry.union_all()
    nyc_city_geom
    return (nyc_city_geom,)


@app.cell
def _(baltimore, gpd, nyc_city_geom):
    cities_df = gpd.GeoDataFrame(
        [{
            "name": "New York City",
            "location_type": ["city"],
            "state": "NY",
            "parent_location_id": None,
            "geometry": nyc_city_geom
        },
         {
            "name": "Baltimore",
            "location_type": ["city"],
            "state": "MD",
            "parent_location_id": None,
            "geometry": baltimore.geometry.iloc[0]
        }],
        geometry="geometry",
        crs="EPSG:4326"
    )

    return (cities_df,)


@app.cell
def _(nyc_boroughs):
    nyc_boroughs_normalized = nyc_boroughs[["geometry"]].copy()
    nyc_boroughs_normalized["name"] = nyc_boroughs["boroname"]
    nyc_boroughs_normalized["location_type"] = [["county"]] * len(nyc_boroughs_normalized)
    nyc_boroughs_normalized["state"] = "NY"
    nyc_boroughs_normalized["parent_location_id"] = None  # no parent yet
    return (nyc_boroughs_normalized,)


@app.cell
def _(cities_df, gpd, nyc_boroughs_normalized, pd):
    all_locations_df = gpd.GeoDataFrame(
        pd.concat([cities_df, nyc_boroughs_normalized], ignore_index=True, verify_integrity =True), 
        geometry="geometry", 
        crs="EPSG:4326"
    )
    all_locations_df["name"]
    return (all_locations_df,)


@app.cell
def _(Base, engine, ensure_all_tables):
    ensure_all_tables(engine, Base)
    return


@app.cell
def _(Session, all_locations_df, engine, populate_locations):
    with Session(engine) as session:
        added, skipped = populate_locations(session, all_locations_df.to_dict("records"))
    return added, session, skipped


if __name__ == "__main__":
    app.run()
