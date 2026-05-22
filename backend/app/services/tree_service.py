from sqlalchemy.orm import Session
from app.models.person import Person
from app.models.relationship import Relationship, RelationshipType
from app.models.user import User
from app.services.privacy_service import can_view_person


def get_tree_data(db: Session, current_user: User | None) -> dict:
    """Return nodes and edges for the full family tree, filtered by privacy."""
    all_people = db.query(Person).all()
    visible = [p for p in all_people if can_view_person(p, current_user)]
    visible_ids = {p.id for p in visible}

    nodes = []
    for p in visible:
        nodes.append({
            "id": str(p.id),
            "data": {
                "person_id": p.id,
                "full_name": p.full_name,
                "birth_year": p.birth_date.year if p.birth_date else None,
                "death_year": p.death_date.year if p.death_date else None,
                "gender": p.gender.value,
                "is_living": p.is_living,
                "profile_photo_url": p.profile_photo_url,
            },
            "type": "personNode",
            "position": {"x": 0, "y": 0},  # layout computed on frontend
        })

    all_rels = db.query(Relationship).all()
    edges = []
    for r in all_rels:
        if r.person1_id not in visible_ids or r.person2_id not in visible_ids:
            continue
        edges.append({
            "id": f"e{r.id}",
            "source": str(r.person1_id),
            "target": str(r.person2_id),
            "type": "smoothstep",
            "data": {
                "relationship_type": r.relationship_type.value,
                "relationship_id": r.id,
            },
            "animated": r.relationship_type == RelationshipType.spouse,
            "style": _edge_style(r.relationship_type),
        })

    return {"nodes": nodes, "edges": edges}


def _edge_style(rel_type: RelationshipType) -> dict:
    if rel_type == RelationshipType.spouse:
        return {"stroke": "#e91e63", "strokeWidth": 2, "strokeDasharray": "6 3"}
    if rel_type == RelationshipType.parent_child:
        return {"stroke": "#1565c0", "strokeWidth": 2}
    return {"stroke": "#78909c", "strokeWidth": 1}
