from sqlalchemy import select, row_number, func
from .tables import WalkableEdge, Base
from .views_utils import view

metadata = Base.metadata

routable_eges = view(
    name="routable_edges",
    metadata=metadata,
    selectable=select(
        WalkableEdge.u.label("source"),
        WalkableEdge.v.label("target"),
        WalkableEdge.key,
        WalkableEdge.length_m.label("cost"),
        WalkableEdge.length_m.label("reverse_cost"),
    ),
)


class RoutableEdge(Base):
    __table__ = "routable_edges"

    """
    Routable edge view to be used with pgrouting
    """
