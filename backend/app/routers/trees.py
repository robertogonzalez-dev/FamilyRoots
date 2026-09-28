from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import graph
from app.db import get_db
from app.models import Person, RelationKind, Relationship, Tree, User
from app.schemas import (
    Ancestor,
    PersonIn,
    PersonOut,
    RelationshipIn,
    RelationshipOut,
    TreeGraph,
    TreeIn,
    TreeOut,
)
from app.security import current_user

router = APIRouter(prefix="/trees", tags=["trees"])


def owned_tree(
    tree_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Tree:
    tree = db.get(Tree, tree_id)
    # 404 rather than 403 so tree IDs belonging to other users aren't discoverable.
    if tree is None or tree.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tree not found")
    return tree


def tree_person(db: Session, tree: Tree, person_id: int) -> Person:
    person = db.get(Person, person_id)
    if person is None or person.tree_id != tree.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Person {person_id} not found in this tree")
    return person


# --- trees -------------------------------------------------------------------------------


@router.get("", response_model=list[TreeOut])
def list_trees(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Tree]:
    return list(db.scalars(select(Tree).where(Tree.owner_id == user.id).order_by(Tree.id)))


@router.post("", response_model=TreeOut, status_code=status.HTTP_201_CREATED)
def create_tree(
    body: TreeIn, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Tree:
    tree = Tree(owner_id=user.id, **body.model_dump())
    db.add(tree)
    db.commit()
    return tree


@router.get("/{tree_id}", response_model=TreeOut)
def get_tree(tree: Tree = Depends(owned_tree)) -> Tree:
    return tree


@router.put("/{tree_id}", response_model=TreeOut)
def update_tree(
    body: TreeIn, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Tree:
    for key, value in body.model_dump().items():
        setattr(tree, key, value)
    db.commit()
    return tree


@router.delete("/{tree_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tree(tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)) -> Response:
    db.delete(tree)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{tree_id}/graph", response_model=TreeGraph)
def tree_graph(tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)) -> TreeGraph:
    people = db.scalars(select(Person).where(Person.tree_id == tree.id).order_by(Person.id))
    rels = db.scalars(select(Relationship).where(Relationship.tree_id == tree.id))
    return TreeGraph(
        people=[PersonOut.model_validate(p) for p in people],
        relationships=[RelationshipOut.model_validate(r) for r in rels],
    )


# --- people ------------------------------------------------------------------------------


@router.post("/{tree_id}/people", response_model=PersonOut, status_code=status.HTTP_201_CREATED)
def create_person(
    body: PersonIn, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Person:
    person = Person(tree_id=tree.id, **body.model_dump())
    db.add(person)
    db.commit()
    return person


@router.get("/{tree_id}/people/{person_id}", response_model=PersonOut)
def get_person(
    person_id: int, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Person:
    return tree_person(db, tree, person_id)


@router.put("/{tree_id}/people/{person_id}", response_model=PersonOut)
def update_person(
    person_id: int, body: PersonIn, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Person:
    person = tree_person(db, tree, person_id)
    for key, value in body.model_dump().items():
        setattr(person, key, value)
    db.commit()
    return person


@router.delete("/{tree_id}/people/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: int, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Response:
    db.delete(tree_person(db, tree, person_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{tree_id}/people/{person_id}/ancestors", response_model=list[Ancestor])
def get_ancestors(
    person_id: int,
    generations: int = Query(default=4, ge=1, le=20),
    tree: Tree = Depends(owned_tree),
    db: Session = Depends(get_db),
) -> list[Ancestor]:
    tree_person(db, tree, person_id)
    return [
        Ancestor(person=PersonOut.model_validate(db.get(Person, pid)), generation=gen)
        for pid, gen in graph.ancestors(db, person_id, generations)
    ]


# --- relationships -----------------------------------------------------------------------


@router.post(
    "/{tree_id}/relationships", response_model=RelationshipOut, status_code=status.HTTP_201_CREATED
)
def create_relationship(
    body: RelationshipIn, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Relationship:
    a, b = body.person_a_id, body.person_b_id
    if a == b:
        raise HTTPException(422, "A person can't relate to themself")
    tree_person(db, tree, a)
    tree_person(db, tree, b)

    if body.kind is RelationKind.spouse:
        a, b = sorted((a, b))  # store symmetric links once
    elif error := graph.validate_parent_link(db, parent_id=a, child_id=b):
        raise HTTPException(422, error)

    rel = Relationship(tree_id=tree.id, person_a_id=a, person_b_id=b, kind=body.kind)
    db.add(rel)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Relationship already exists") from None
    return rel


@router.delete("/{tree_id}/relationships/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    rel_id: int, tree: Tree = Depends(owned_tree), db: Session = Depends(get_db)
) -> Response:
    rel = db.get(Relationship, rel_id)
    if rel is None or rel.tree_id != tree.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Relationship not found")
    db.delete(rel)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
