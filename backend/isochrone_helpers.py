from sqlalchemy.orm import Session
from sqlalchemy import text
from geoalchemy2 import Geometry
# snapped_point = snap_point_to_edge(pt.lat, pt.lng, db)
def snap_point_to_edge(lat:float, lng:float, db:Session):
    #get closest pt on graph (a start or end of existing linestrings in walkable_edges)
    q = text("""
    WITH snapped AS (
        SELECT *,
            ST_LineLocatePoint(geometry, ST_SetSRID(ST_Point(:lng, :lat), 4326)) AS pos
        FROM walkable_edges
        ORDER BY geometry <-> ST_SetSRID(ST_Point(:lng, :lat), 4326)
        LIMIT 1
    )
    SELECT 
        ST_AsEWKB(ST_LineInterpolatePoint(geometry, pos)) AS snapped_geom,
        u as source,
        v as target,
        CASE 
            WHEN ST_Distance(ST_StartPoint(geometry), ST_LineInterpolatePoint(geometry, pos)) < 
            ST_Distance(ST_EndPoint(geometry), ST_LineInterpolatePoint(geometry, pos)) 
            THEN u ELSE v 
        END AS nearest_node
        FROM snapped;
    """).columns(snapped_geom=Geometry(geometry_type="POINT", srid=4326))
    snapped_point = db.execute(q, {"lat":lat, "lng":lng}).first()
    return snapped_point

# nearest_node = find_nearest_node(snapped_point, db)
def find_nearest_node(pt, db):
    # return nearest_node
    pass

# reachable = run_pgr_driving_distance(nearest_node, db)
def run_pgr_driving_distance(node, db):
    # return reachable
    pass 

# geojson = convert_edges_to_geojson(reachable, db)
def convert_edges_to_geojson(reachable, db):
    # return geojson
    pass
