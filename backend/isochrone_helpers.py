from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2 import Geometry


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
        SELECT jsonb_build_object(
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
        ) AS geojson
        FROM limited_edges;
    """)

    result = db.execute(query, {
        "start_vid": snapped_point.nearest_node,
        "cost_limit": cost_limit
    }).scalar()

    return result  # already a Python dict thanks to jsonb → ORJSONResponse

# # nearest_node = find_nearest_node(snapped_point, db)
# def find_nearest_node(pt, db):
#     # return nearest_node
#     pass


# reachable = run_pgr_driving_distance(nearest_node, db)
def run_pgr_driving_distance(node, db):
    # return reachable
    pass


# geojson = convert_edges_to_geojson(reachable, db)
def convert_edges_to_geojson(reachable, db):
    # return geojson
    pass
