import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, select, inspect, func, tuple_
from geoalchemy2.functions import (
    ST_GeomFromText,
    ST_DWithin,
    ST_Contains,
    ST_Buffer,
    ST_Intersects,
)
from geoalchemy2.shape import from_shape
import structlog
from sqlalchemy_utils import database_exists, create_database
from shapely.geometry import shape, Polygon, MultiPolygon, Point, LineString
from shapely.geometry.base import BaseGeometry
from backend.models.tables import Location, Place, WalkableEdge


log = structlog.get_logger()
DATABASE_URL = "postgresql://postgres:password@localhost:5432/urban_utilization"
BATCH_SIZE = 5000

# set up the database connection
engine = create_engine(DATABASE_URL)
# if not database_exists(engine.url):
#     log.warning("Database not found, attempting creation ...")
#     create_database(engine.url)
#     log.info("Database created sucessfully")

# Base.metadata.create_all(bind=engine)


def ensure_all_tables(engine, Base):
    inspector = inspect(engine)

    existing_tables = set(inspector.get_table_names())
    declared_tables = set(Base.metadata.tables.keys())
    missing_tables = declared_tables - existing_tables

    if missing_tables:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info(f"Created missing tables: {sorted(missing_tables)}")
    else:

        log.info("All declared tables already exist. Nothing created.")


def populate_locations(session, rows, verbose=True):
    added = []
    skipped = []

    to_add = []
    for row in rows:
        name = row["name"]
        location_type = row["location_type"]
        state = row["state"]
        geom = row["geometry"]
        parent_id = row.get("parent_location_id")  # default is None

        # normalize geometry
        if isinstance(geom, dict):
            geom = shape(geom)

        if not isinstance(geom, BaseGeometry):
            log.warning(
                f"Invalid geometry for {name}, {state}. Recheck geometry, skipping"
            )
            skipped.append(name)
            continue

        if not isinstance(geom, (Polygon, MultiPolygon)):
            log.warning(
                f"Skipping{name}, {state}, geometry is {geom.geom_type}, not Polygon/Multipolygon"
            )
            skipped.append(name)
            continue

        geo_obj = from_shape(geom, srid=4326)

        # check for existence by name + state
        exists = session.scalar(
            select(Location).where(Location.name == name, Location.state == state)
        )

        if exists:
            skipped.append(name)
            if verbose:
                log.info(f"Skipped existing location:{name}, {state}")
            continue

        loc = Location(
            name=name,
            location_type=location_type,
            state=state,
            geom=geo_obj,
            parent_location_id=parent_id,
        )
        to_add.append(loc)
        added.append(name)

    session.add_all(to_add)
    session.commit()
    log.info(
        "Added the following locations:\n"
        + "\n".join(f"• {loc.name}, {loc.state}" for loc in to_add)
    )
    return added, skipped


def spatial_populate_parent_location_ids(session):
    # only memory safe if small amount of locations
    all_locations = session.scalars(select(Location)).all()

    for child in all_locations:
        if child.parent_location_id:
            log.info(f"{child.name} has parent already {child.parent_location_id}")
            continue

        # find parent candidates
        parent = session.scalar(
            select(Location)
            .where(Location.id != child.id)
            .where(ST_Contains(Location.geom, ST_Buffer(child.geom, -0.0000001)))
            .order_by(func.ST_AREA(Location.geom))
            .limit(1)
        )
        if parent:
            child.parent_location_id = parent.id
            log.info(
                f"found parent for {child.name}, {child.state}: {parent.name}, {parent.state}"
            )

    session.commit()
    log.info("Updated parents")


def populate_places(session, rows, verbose=True):
    added = []
    skipped = []

    to_add = []
    for row in rows:
        name = row["name"]
        desc = row["desc"]
        place_type = row["place_type"]
        active = row["active"]
        year_added = row["year_added"]
        year_removed = row["year_removed"]

        location_id = row["location_id"]
        geom = row["geom"]

        # normalize geometry
        if not isinstance(geom, Point):
            log.warning(
                f"Skipping{name}, {desc}, geometry is {geom.geom_type}, not Point"
            )
            skipped.append(name)
            continue

        geo_obj = from_shape(geom, srid=4326)

        # check for existence by place_type + geom to the nearest meter
        exists = session.scalar(
            select(Place)
            .where(Place.place_type == place_type)
            .where(ST_DWithin(Place.geom, geo_obj, 0.00001))
        )

        if exists:
            skipped.append(name)
            if verbose:
                log.info(f"Skipped existing place:{name}, {place_type}, {geom}")
            continue

        place = Place(
            name=name,
            desc=desc,
            place_type=place_type,
            active=active,
            year_added=year_added,
            year_removed=year_removed,
            location_id=location_id,
            geom=geo_obj,
        )
        to_add.append(place)
        added.append(name)

    session.add_all(to_add)
    session.commit()
    log.info(
        "Added the following places:\n"
        + "\n".join(f"• {place.name}, {place.place_type}" for place in to_add)
    )
    return added, skipped


def populate_edges(session, rows, verbose=True):
    added = []
    skipped = []

    for batch_start in range(0, len(rows), BATCH_SIZE):
        batch_rows = rows[batch_start : batch_start + BATCH_SIZE]

        batch_keys = [(r["u"], r["v"], r["key"]) for r in batch_rows]

        existing = session.execute(
            select(WalkableEdge.u, WalkableEdge.v, WalkableEdge.key).where(
                tuple_(WalkableEdge.u, WalkableEdge.v, WalkableEdge.key).in_(batch_keys)
            )
        ).fetchall()

        existing_set = set(existing)

        batch_to_insert = []

        for row in batch_rows:
            u = row["u"]
            v = row["v"]
            key = row.get("key", 0)
            length_m = row["length_m"]
            highway = row["highway"]
            geom = row["geometry"]

            if not isinstance(geom, LineString):
                skipped.append((u, v, key))
                continue

            if (u, v, key) in existing_set:
                skipped.append((u, v, key))
                continue

            geo_obj = from_shape(geom, srid=4326)

            edge = {
                "u": u,
                "v": v,
                "key": key,
                "length_m": length_m,
                "highway": highway if isinstance(highway, list) else [highway],
                "geometry": geo_obj,
                "location_id": None,
            }
            batch_to_insert.append(edge)
            added.append((u, v, key))

        if batch_to_insert:
            session.bulk_insert_mappings(WalkableEdge, batch_to_insert)
            session.commit()
            log.info(f"Batch inserted, rows: {len(batch_to_insert)}")

    if verbose:
        log.info(f"Inserted {len(added)} edges total.")
        log.info(f"Skipped {len(skipped)} edges total.")

    return added, skipped


# def populate_location_id_edges(session):
#     offset = 0
#     total_updated = 0
#     while True:
#         # fetch batch of edges where location_id is NULL
#         edges = session.scalars(
#             select(WalkableEdge)
#             .where(WalkableEdge.location_id.is_(None))
#             .limit(BATCH_SIZE)
#             .offset(offset)
#         ).all()

#         if not edges:
#             log.info("All edges have a location_id set")
#             break
#         for edge in edges:
#             city_location = session.scalar(
#                 select(Location)
#                 .where(Location.location_type.any("city"))
#                 .where(ST_Intersects(edge.geometry, Location.geom))
#                 .order_by(func.ST_Area(Location.geom))
#                 .limit(1)
#             )

#             if city_location:
#                 edge.location_id = city_location.id
#                 total_updated += 1

#         session.commit()
#         offset += BATCH_SIZE
#         log.info(f"Commited batch, total edges updated so far: {total_updated}")

#     log.info(f"Added location_id to {total_updated} edges")

def populate_location_id_edges(session):
    cities = session.scalars(
        select(Location).where(Location.location_type.any("city"))
    ).all()

    total_updated = 0

    for city in cities:
        # Bulk update all edges that intersect this city
        updated = session.execute(
            sqlalchemy.update(WalkableEdge)
            .where(WalkableEdge.location_id.is_(None))
            .where(ST_Intersects(WalkableEdge.geometry, city.geom))
            .values(location_id=city.id)
        )
        session.commit()
        updated_count = updated.rowcount or 0
        total_updated += updated_count
        log.info(f"Updated {updated_count} edges for city {city.name}")

    log.info(f"Added location_id to {total_updated} edges.")


if __name__ == "__main__":
    SessionLocal = sessionmaker(bind=engine) #where to import sessionmaker?
    session = SessionLocal()
    populate_location_id_edges(session)
    session.close()
    # log.info("Run some functions to populate database")
