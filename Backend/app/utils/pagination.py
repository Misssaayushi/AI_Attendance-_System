from __future__ import annotations

"""Utility helpers for pagination and filtering of student queries.

- `paginate(query, page: int = 1, page_size: int = 20) -> Tuple[List[Model], int]`
  Executes the given SQLAlchemy query with limit/offset and returns the list of items
  along with the total count of matching rows (without pagination).

- `apply_student_filters(query, *, search: str | None = None, department: str | None = None,
  year: int | None = None)`
  Adds dynamic ``WHERE`` clauses based on optional parameters.
"""

from typing import List, Tuple

from sqlalchemy.orm import Query


def paginate(query: Query, page: int = 1, page_size: int = 20) -> Tuple[List, int]:
    """Apply limit/offset pagination.

    Args:
        query: The base SQLAlchemy query.
        page: 1‑based page number.
        page_size: Number of items per page (capped at 100).
    Returns:
        A tuple ``(items, total)`` where ``items`` is the sliced list and ``total``
        is the total number of rows matching the un‑paginated query.
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100

    total = query.order_by(None).count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return items, total


def apply_student_filters(
    query: Query,
    *,
    search: str | None = None,
    department: str | None = None,
    year: int | None = None,
) -> Query:
    """Add optional filter criteria to a student query.

    ``search`` performs a case‑insensitive partial match on first_name,
    last_name or roll_number.
    ``department`` and ``year`` are exact matches.
    """
    if search:
        pattern = f"%{search.lower()}%"
        model = query._entity_zero().entity_zero.class_
        query = query.filter(
            model.first_name.ilike(pattern)
            | model.last_name.ilike(pattern)
            | model.roll_number.ilike(pattern)
        )
    if department:
        model = query._entity_zero().entity_zero.class_
        query = query.filter(model.department == department)
    if year:
        model = query._entity_zero().entity_zero.class_
        query = query.filter(model.year_batch == str(year))
    return query
