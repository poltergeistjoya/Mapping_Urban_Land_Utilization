from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2 import Geometry
from jinja2 import Template
from geoalchemy2.elements import WKTElement
import structlog 
from shapely.geometry import mapping
from shapely.geometry import shape, MultiLineString, mapping
from shapely.ops import unary_union

from models.tables import ALLOWED_PLACE_TYPES

log = structlog.get_logger()

# snapped_point = snap_point_to_edge(pt.lat, pt.lng, db)
def snap_point_to_edge(lat: float, lng: float, db: Session):
    # get closest pt on graph (a start or end of existing linestrings in walkable_edges)
    q = text(
        """
    WITH snapped AS (
        SELECT *,
            ST_LineLocatePoint(geometry, ST_SetSRID(ST_Point(:lng, :lat), 4326)) AS pos
        FROM walkable_edges
        ORDER BY geometry <-> ST_SetSRID(ST_Point(:lng, :lat), 4326)
        LIMIT 1
    )
    SELECT 
        ST_AsEWKB(ST_LineInterpolatePoint(geometry, pos)) AS interpolated_pt,
        u as source,
        v as target,
        CASE 
            WHEN ST_Distance(ST_StartPoint(geometry), ST_LineInterpolatePoint(geometry, pos)) < 
            ST_Distance(ST_EndPoint(geometry), ST_LineInterpolatePoint(geometry, pos)) 
            THEN u ELSE v 
        END AS nearest_node,
        ST_AsEWKB(
             CASE 
             WHEN ST_Distance(ST_StartPoint(geometry), ST_LineInterpolatePoint(geometry, pos))< 
             ST_Distance(ST_EndPoint(geometry), ST_LineInterpolatePoint(geometry, pos))
             THEN ST_StartPoint(geometry)
             ELSE ST_EndPoint(geometry)
             END
        ) AS nearest_node_geom
        FROM snapped;
    """
    ).columns(
        interpolated_pt=Geometry(geometry_type="POINT", srid=4326),
        nearest_node_geom=Geometry(geometry_type="POINT", srid=4326),
    )
    snapped_point = db.execute(q, {"lat": lat, "lng": lng}).first()
    return snapped_point

# def get_isochrone_edges(snapped_point, db: Session, cost_limit: float = 1260):
#     query = text("""
#         WITH reachable AS (
#             SELECT edge
#             FROM pgr_drivingDistance(
#                 'SELECT id, u AS source, v AS target, length_m AS cost, length_m AS reverse_cost FROM walkable_edges',
#                 :start_vid,
#                 :cost_limit
#             )
#             WHERE edge != -1
#         ),
#         limited_edges AS (
#             SELECT we.*
#             FROM reachable r
#             JOIN walkable_edges we ON we.id = r.edge
#         )
#         SELECT 
#             jsonb_build_object(
#                 'type', 'FeatureCollection',
#                 'features', jsonb_agg(
#                     jsonb_build_object(
#                         'type', 'Feature',
#                         'geometry', ST_AsGeoJSON(geometry)::jsonb,
#                         'properties', jsonb_build_object(
#                             'id', id,
#                             'u', u,
#                             'v', v,
#                             'key', key,
#                             'length_m', length_m
#                         )
#                     )
#                 )
#             ) AS geojson,
#             array_agg(geometry) AS geoms
#         FROM limited_edges;
#     """)

#     result = db.execute(query, {
#         "start_vid": snapped_point.nearest_node,
#         "cost_limit": cost_limit
#     }).first()

#     return {
#         "geojson": result.geojson,
#         "geoms": result.geoms
#     }

# def get_polygon_and_places(edge_geojson: dict, db: Session, place_types: list[str], buffer_m: float = 25.0):
#     # Validate place types
#     invalid = set(place_types) - ALLOWED_PLACE_TYPES
#     if invalid:
#         raise ValueError(f"Invalid place types: {invalid}")

#     lines = [shape(f["geometry"]) for f in edge_geojson["features"] if f["geometry"]["type"] == "LineString"]
#     if not lines:
#         return {
#             "polygon": None,
#             "places": {
#                 "type": "FeatureCollection",
#                 "features": []
#             }
#         }

#     merged = unary_union(lines)
#     buffered = merged.buffer(buffer_m)
#     buffered_wkt = WKTElement(buffered.wkt, srid=4326)

#     query = text("""
#         SELECT jsonb_agg(jsonb_build_object(
#             'type', 'Feature',
#             'geometry', ST_AsGeoJSON(p.geom)::json,
#             'properties', jsonb_build_object(
#                 'id', p.id,
#                 'name', p.name,
#                 'type', p.place_type
#             )
#         )) AS places
#         FROM places p
#         WHERE p.place_type = ANY(:types)
#           AND ST_Within(p.geom, :buffered_geom)
#     """)

#     result = db.execute(query, {
#         "types": place_types,
#         "buffered_geom": buffered_wkt
#     }).first()

#     return {
#         "polygon": {
#             "type": "Feature",
#             "geometry": mapping(buffered),
#             "properties": {
#                 "description": f"{buffer_m}m isochrone buffer"
#             }
#         },
#         "places": {
#             "type": "FeatureCollection",
#             "features": result.places or []
#         }
#     }

def get_isochrone_edges(snapped_point, db: Session, cost_limit: float = 1260):
    query = text("""
        WITH reachable AS (
            SELECT edge
            FROM pgr_drivingDistance(
                'SELECT id, u AS source, v AS target, length_m AS cost, length_m AS reverse_cost FROM walkable_edges',
                :start_vid,
                :cost_limit
            )
            WHERE edge != -1
        ),
        limited_edges AS (
            SELECT we.*
            FROM reachable r
            JOIN walkable_edges we ON we.id = r.edge
        )
        SELECT 
            jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(geometry)::jsonb,
                        'properties', jsonb_build_object(
                            'id', id,
                            'u', u,
                            'v', v,
                            'key', key,
                            'length_m', length_m
                        )
                    )
                )
            ) AS geojson,
            array_agg(id) AS edge_ids
        FROM limited_edges;
    """)

    result = db.execute(query, {
        "start_vid": snapped_point.nearest_node,
        "cost_limit": cost_limit
    }).first()

    return {
        "geojson": result.geojson,
        "edge_ids": result.edge_ids
    }

def get_polygon_and_places(edge_ids: list[int], db: Session, place_types: list[str], buffer_m: float =  0.000405):
    # Validate place types
    invalid = set(place_types) - ALLOWED_PLACE_TYPES
    if invalid:
        raise ValueError(f"Invalid place types: {invalid}")

    if not edge_ids:
        return {
            "polygon": None,
            "places": {
                "type": "FeatureCollection",
                "features": []
            }
        }

    query = text("""
        WITH edge_geom AS (
            SELECT geometry
            FROM walkable_edges
            WHERE id = ANY(:edge_ids)
        ),
        geom_union AS (
            SELECT ST_Buffer(ST_Union(geometry), :buffer_m) AS geom
            FROM edge_geom
        )
        SELECT 
            ST_AsGeoJSON(geom_union.geom)::json AS polygon,
            (
                SELECT jsonb_agg(jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(p.geom)::json,
                    'properties', jsonb_build_object(
                        'id', p.id,
                        'name', p.name,
                        'type', p.place_type
                    )
                ))
                FROM places p
                WHERE p.place_type = ANY(:types)
                  AND ST_Within(p.geom, geom_union.geom)
            ) AS places
        FROM geom_union;
    """)
    log.info("getting polygon and places ...")
    result = db.execute(query, {
        "edge_ids": edge_ids,
        "types": place_types,
        "buffer_m": buffer_m
    }).first()

    return {
        "polygon": result.polygon,
        "places": {
            "type": "FeatureCollection",
            "features": result.places or []
        }
    }
