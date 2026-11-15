"""Explicit data partitions, independent of account preferences and Auth session."""

from typing import Literal
from uuid import UUID
from fastapi import HTTPException
from backend.app.db.client import database_call

Workspace = Literal["personal", "simulation", "legacy_unclassified"]


def owned_source(session, source_id):
    if not source_id:
        raise HTTPException(422, "Choose an explicit simulation session")
    rows = database_call(session, f"source_sessions?id=eq.{UUID(str(source_id))}&select=*")
    if not rows:
        raise HTTPException(404, "Simulation session not found")
    return rows[0]


def meal_partition(session, workspace: Workspace, source_id=None):
    if source_id and workspace != "simulation":
        raise HTTPException(422, "A virtual source belongs only to the simulation workspace")
    result = f"workspace=eq.{workspace}"
    if source_id:
        owned_source(session, source_id)
        result += f"&source_session_id=eq.{source_id}"
    return result
