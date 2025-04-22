import marimo

__generated_with = "0.12.10"
app = marimo.App(width="medium")


@app.cell
def _(__file__):
    import geopandas as gpd
    import pandas as pd
    import re
    from shapely.geometry import mapping, Point
    from geoalchemy2.shape import from_shape
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    import sys
    import pathlib 

    #to import other packages
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
    from backend.models.tables import Location, Base, ALLOWED_PLACE_TYPES
    from backend.populate_db import engine, ensure_all_tables, populate_locations, populate_places
    return (
        ALLOWED_PLACE_TYPES,
        Base,
        Location,
        Point,
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
        populate_places,
        re,
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
def _(GEOJSON_DIR, gpd):
    baltimore_street_vendor = gpd.read_file(GEOJSON_DIR + "Baltimore_Street_Food_Vendor_Locations.geojson")
    baltimore_street_vendor.columns
    return (baltimore_street_vendor,)


@app.cell
def _(ALLOWED_PLACE_TYPES, Point, re):
    def extract_point_from_string(regex_string, loc_str):
        match = re.search(regex_string, loc_str)
        if match: 
            lat, lon = float(match.group(1)), float(match.group(2))
            return Point(lon,lat)
        return None

    def normalize_to_place(row, col_map, place_type):
        if place_type not in ALLOWED_PLACE_TYPES:
            print(f"[normalize_to_place] Skipping row — invalid place_type: '{place_type}'")
            return None

        return{
            "name": row[col_map.get("name", None)],
            "desc": row[col_map.get("desc", None)],
            "place_type": place_type, 
            "active": True, 
            "year_added": row[col_map.get("year_added",None)],
            "year_removed": None, 
            "location_id": None,
            "geom": row[col_map.get("geom")],

        }
    return extract_point_from_string, normalize_to_place


@app.cell
def _(
    baltimore_street_vendor,
    extract_point_from_string,
    gpd,
    normalize_to_place,
):
    regex_bmore_point_street_vendor = r"\(([-\d\.]+), ([-\d\.]+)\)"
    baltimore_street_vendor["geom"] = baltimore_street_vendor["Location_1"].apply(lambda val: extract_point_from_string(regex_bmore_point_street_vendor, val)
                                                                    )
    baltimore_street_vendor["year_added"] = 2023
    bmore_street_vendor_col_map = {
        "name": "Cart_Descr",
        "desc": "ItemsSold",
        "geom": "geom",
        "year_added": "year_added"
    }
    bmore_st_vend_normalized = gpd.GeoDataFrame(
        baltimore_street_vendor.apply(
            lambda row: normalize_to_place(
                row=row,
                col_map=bmore_street_vendor_col_map,
                place_type="street_vendor"
            ),
            axis=1
        ).tolist(),
        geometry="geom",
        crs="EPSG:4326"
    )

    bmore_st_vend_normalized

    return (
        bmore_st_vend_normalized,
        bmore_street_vendor_col_map,
        regex_bmore_point_street_vendor,
    )


@app.cell
def _(
    Base,
    Session,
    all_locations_df,
    bmore_st_vend_normalized,
    engine,
    ensure_all_tables,
    populate_locations,
    populate_places,
):
    #ONLY WHEN YOU WANT TO CREATE ALL TABLES
    ensure_all_tables(engine, Base)

    with Session(engine) as session:
        added, skipped = populate_locations(session, all_locations_df.to_dict("records"))
        added_bmore_st, skipped_bmore_st = populate_places(session, bmore_st_vend_normalized.to_dict("records"))
    return added, added_bmore_st, session, skipped, skipped_bmore_st


if __name__ == "__main__":
    app.run()
