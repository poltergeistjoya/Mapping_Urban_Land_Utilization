import marimo

__generated_with = "0.12.10"
app = marimo.App(width="medium")


@app.cell
def _(__file__):
    import geopandas as gpd
    import pandas as pd
    import matplotlib.pyplot as plt
    import re
    from pathlib import Path
    from shapely.geometry import mapping, Point
    from geoalchemy2.shape import from_shape
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    import sys
    import pathlib 
    import osmnx as ox

    #to import other packages
    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
    from backend.models import Base
    from backend.models.tables import Location, ALLOWED_PLACE_TYPES
    from backend.populate_db import engine, ensure_all_tables, populate_locations, populate_places, populate_edges

    ox.settings.use_cache = True
    ox.settings.log_console = True
    return (
        ALLOWED_PLACE_TYPES,
        Base,
        Location,
        Path,
        Point,
        Session,
        create_engine,
        engine,
        ensure_all_tables,
        from_shape,
        gpd,
        mapping,
        ox,
        pathlib,
        pd,
        plt,
        populate_edges,
        populate_locations,
        populate_places,
        re,
        sys,
    )


@app.cell
def _():
    GEOJSON_DIR = "../random_data/geojsons/"
    SHPFILE_DIR = "../random_data/shapefiles/"
    GRAPHML_DIR = "../random_data/graphml/"
    CSV_DIR = "../random_data/csvs/"
    TXT_DIR = "../random_data/txt"
    return CSV_DIR, GEOJSON_DIR, GRAPHML_DIR, SHPFILE_DIR, TXT_DIR


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
            "geom": row[col_map.get("geom", None)],

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
def _(bmore_trash_cans_OSM, nyc_trash_cans):
    nyc_trash_cans["geometry"].apply(lambda g: g.geom_type).unique()
    bmore_trash_cans_OSM["geometry"].apply(lambda g: g.geom_type).unique()

    return


@app.cell
def _(GEOJSON_DIR, gpd, normalize_to_place):
    bmore_trash_cans_OSM = gpd.read_file(GEOJSON_DIR + "baltimore_trash_cans_OSM.geojson")
    bmore_trash_cans_OSM["name"] = "Trash Can"
    bmore_trash_cans_OSM["desc"] = None
    bmore_trash_cans_OSM["year_added"] = None

    bmore_trash_OSM_col_map = {
        "name": "name",
        "desc": "desc",
        "geom": "geometry",
        "year_added": "year_added"
    }

    bmore_trash_cans_OSM_normalized = gpd.GeoDataFrame(
        bmore_trash_cans_OSM.apply(
            lambda row: normalize_to_place(
                row=row,
                col_map=bmore_trash_OSM_col_map,
                place_type="trash_can"
            ),
            axis=1
        ).tolist(),
        geometry="geom",
        crs="EPSG:4326"
    )

    bmore_trash_cans_OSM_normalized
    return (
        bmore_trash_OSM_col_map,
        bmore_trash_cans_OSM,
        bmore_trash_cans_OSM_normalized,
    )


@app.cell
def _(GEOJSON_DIR, gpd, normalize_to_place):
    nyc_trash_cans = gpd.read_file(GEOJSON_DIR + "NYC_trash_cans_2025.geojson")
    nyc_trash_cans["name"] = nyc_trash_cans["streetname1"].fillna("").astype(str) + "&" + nyc_trash_cans["streetname2"].fillna("").astype(str)
    nyc_trash_cans["desc"] = nyc_trash_cans["location_description"]
    nyc_trash_cans["year_added"] = 2025

    nyc_trash_can_map = {
        "name": "name",
        "desc": "desc",
        "geom": "geometry",
        "year_added": "year_added"
    }

    nyc_trash_cans_normalized = gpd.GeoDataFrame(
        nyc_trash_cans.apply(
            lambda row: normalize_to_place(
                row=row,
                col_map=nyc_trash_can_map,
                place_type="trash_can"
            ),
            axis=1
        ).tolist(),
        geometry="geom",
        crs="EPSG:4326"
    )

    nyc_trash_cans_normalized
    return nyc_trash_can_map, nyc_trash_cans, nyc_trash_cans_normalized


@app.cell
def _(bmore_trash_cans_OSM_normalized, gpd, nyc_trash_cans_normalized, pd):
    all_trash_cans_df = gpd.GeoDataFrame(
        pd.concat([bmore_trash_cans_OSM_normalized, nyc_trash_cans_normalized], ignore_index=True, verify_integrity =True), 
        geometry="geom", 
        crs="EPSG:4326"
    )
    all_trash_cans_df
    return (all_trash_cans_df,)


@app.cell
def _():
    # #ONLY WHEN YOU WANT TO CREATE ALL TABLES
    # ensure_all_tables(engine, Base)

    # with Session(engine) as session:
    #     added, skipped = populate_locations(session, all_locations_df.to_dict("records"))
    #     added_bmore_st, skipped_bmore_st = populate_places(session, bmore_st_vend_normalized.to_dict("records"))
    #     added_trash, skipped_trash = populate_places(session, all_trash_cans_df.to_dict("records"))
    return


@app.cell
def _():
    # baltimore_graph_path = Path(GRAPHML_DIR + "baltimore_walk.graphml")
    # nyc_graph_path = Path(GRAPHML_DIR + "nyc_walk.graphml")

    # if baltimore_graph_path.exists():
    #     print("Loading cached baltimore graph")
    #     G_baltimore = ox.load_graphml(baltimore_graph_path)
    # else:
    #     G_baltimore = ox.graph_from_place("Baltimore, Maryland, USA", network_type="walk")
    #     ox.save_graphml(G_baltimore, baltimore_graph_path)

    # if nyc_graph_path.exists():
    #     print("Loading cached nyc graph")
    #     G_nyc = ox.load_graphml(nyc_graph_path)
    # else:
    #     G_nyc = ox.graph_from_place("New York City, New York, USA", network_type="walk")
    #     ox.save_graphml(G_nyc, nyc_graph_path)

    return


@app.cell
def _():
    # # Convert to GeoDataFrame (edges = walkable segments)
    # baltimore_edges = ox.graph_to_gdfs(G_baltimore, nodes=False, edges=True)
    # baltimore_edges.plot()
    return


@app.cell
def _():
    # # Convert to GeoDataFrame (edges = walkable segments)
    # nyc_edges = ox.graph_to_gdfs(G_nyc, nodes=False, edges=True)
    # fig,ax =plt.subplots(figsize=(12,12))
    # nyc_edges.plot(ax=ax)
    return


@app.cell
def _():
    # from itertools import chain

    # set(chain.from_iterable(
    #     v if isinstance(v, list) else [v]
    #     for v in baltimore_edges["highway"]
    # ))
    return


@app.cell
def _():
    # common_walk_cols = list(set(baltimore_edges.columns) & set(nyc_edges.columns))
    # common_walk_cols
    return


@app.cell
def _():
    keep_walkable_edges_cols = ["u", "v", "key", "length", "highway", "geometry"]
    def clean_osmnx_edges_df(gdf):
        gdf = gdf.reset_index()  
        gdf = gdf[keep_walkable_edges_cols].copy()  # Keep only needed columns
        gdf = gdf.rename(columns={"length": "length_m"})  # Rename 'length' -> 'length_m'
        return gdf
    return clean_osmnx_edges_df, keep_walkable_edges_cols


@app.cell
def _():
    # clean_baltimore_edges = clean_osmnx_edges_df(baltimore_edges)
    # clean_nyc_edges = clean_osmnx_edges_df(nyc_edges)
    return


@app.cell
def _():
    # combined_edges = pd.concat([clean_baltimore_edges, clean_nyc_edges], ignore_index=True)
    # combined_edges
    return


@app.cell
def _():
    # with Session(engine) as session:
    #     added_edges, skipped_edges = populate_edges(session, combined_edges.to_dict("records"))
    return


@app.cell
def _(GEOJSON_DIR, gpd, nyc_boroughs_normalized):
    # Start grocery store processing
    nyc_borough_names = list(nyc_boroughs_normalized["name"].str.replace(" ", "").str.lower().unique()) + ["kings"]
    nys_food_retailer = gpd.read_file(GEOJSON_DIR + "NY_Retail_Food_Stores_20250504.geojson")
    nyc_food_retailer = nys_food_retailer[nys_food_retailer["county"].str.replace(" ", "").str.lower().isin(nyc_borough_names)].copy()
    nyc_food_retailer
    return nyc_borough_names, nyc_food_retailer, nys_food_retailer


@app.cell
def _(nyc_food_retailer):
    nyc_food_retailer["estab_type"].unique()
    nyc_food_retailer["name"] = nyc_food_retailer["dba_name"]
    nyc_food_retailer["desc"] = (
        nyc_food_retailer["street_number"].astype(str)
        + " "
        + nyc_food_retailer["street_name"].astype(str)
        + ", "
        + nyc_food_retailer["city"].astype(str)
        + ", "
        + nyc_food_retailer["zip_code"].astype(str)
    )
    nyc_food_retailer["zip_code"]
    nyc_food_retailer["year_added"] = 2025
    nyc_food_retailer["year_removed"] = None
    nyc_food_retailer
    return


@app.cell
def _(gpd, normalize_to_place, nyc_food_retailer):
    nyc_food_retailer_normalized = gpd.GeoDataFrame(
        nyc_food_retailer.apply(
            lambda row: normalize_to_place(
                row=row,
                col_map={
                    "name": "name",
                    "desc": "desc",
                    "geom": "geometry",
                    "year_added": "year_added",
                    "year_removed": "year_removed"
                },
                place_type="grocery_store"
            ),
            axis=1
        ).tolist(),
        geometry="geom",
        crs="EPSG:4326"
    )
    nyc_food_retailer_normalized_dedup = nyc_food_retailer_normalized.drop_duplicates(
        subset=["name", "place_type", nyc_food_retailer_normalized.geometry.name],
        keep="first"
    )
    nyc_food_retailer_normalized_dedup
    return nyc_food_retailer_normalized, nyc_food_retailer_normalized_dedup


@app.cell
def _(nyc_food_retailer_normalized_dedup):
    nyc_groc_dupes = nyc_food_retailer_normalized_dedup[nyc_food_retailer_normalized_dedup.duplicated(subset=["name", "place_type", "geom"], keep=False)]
    nyc_groc_dupes
    return (nyc_groc_dupes,)


@app.cell
def _(GEOJSON_DIR, gpd):
    baltimore_grocery_stores = gpd.read_file(GEOJSON_DIR + "bmore_opendata_Grocery_Stores.geojson")
    baltimore_grocery_stores
    return (baltimore_grocery_stores,)


@app.cell
def _(baltimore_grocery_stores, gpd, normalize_to_place):
    baltimore_grocery_stores["name"] = baltimore_grocery_stores["storename"]
    baltimore_grocery_stores["desc"] = baltimore_grocery_stores["address"]
    baltimore_grocery_stores["year_added"]= 2025
    baltimore_grocery_stores["year_removed"] = None

    baltimore_grocery_stores_normalized = gpd.GeoDataFrame(
        baltimore_grocery_stores.apply(
            lambda row: normalize_to_place(
                row=row,
                col_map={
                    "name": "name",
                    "desc": "desc",
                    "geom": "geometry",
                    "year_added": "year_added",
                    "year_removed": "year_removed"
                },
                place_type="grocery_store"
            ),
            axis=1
        ).tolist(),
        geometry="geom",
        crs="EPSG:4326"
    )
    baltimore_grocery_stores_normalized_dedup = baltimore_grocery_stores_normalized.drop_duplicates(
        subset=["name", "place_type", baltimore_grocery_stores_normalized.geometry.name],
        keep="first"
    )
    baltimore_grocery_stores_normalized_dedup
    return (
        baltimore_grocery_stores_normalized,
        baltimore_grocery_stores_normalized_dedup,
    )


@app.cell
def _(baltimore_grocery_stores_normalized_dedup):
    bmore_groc_dupes = baltimore_grocery_stores_normalized_dedup[baltimore_grocery_stores_normalized_dedup.duplicated(subset=["name", "place_type", "geom"], keep=False)]
    bmore_groc_dupes
    return (bmore_groc_dupes,)


@app.cell
def _(
    Session,
    baltimore_grocery_stores_normalized_dedup,
    engine,
    nyc_food_retailer_normalized_dedup,
    populate_places,
):
    # #ONLY WHEN YOU WANT TO CREATE ALL TABLES
    # ensure_all_tables(engine, Base)

    with Session(engine) as session:
        added_nyc_groc, skipped_nyc_groc = populate_places(session, nyc_food_retailer_normalized_dedup.to_dict("records"))
        added_bmore_groc, skipped_bmore_groc = populate_places(session, baltimore_grocery_stores_normalized_dedup.to_dict("records"))
    return (
        added_bmore_groc,
        added_nyc_groc,
        session,
        skipped_bmore_groc,
        skipped_nyc_groc,
    )


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
