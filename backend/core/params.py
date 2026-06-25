"""
Shared, reusable FastAPI query-parameter dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends, Query


@dataclass
class HistoryParams:
    """Common pagination + date-range filters used by every `/history` endpoint."""

    start_date: Optional[datetime]
    end_date: Optional[datetime]
    limit: int
    offset: int


def get_history_params(
    start_date: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records to skip"),
) -> HistoryParams:
    return HistoryParams(
        start_date=start_date, end_date=end_date, limit=limit, offset=offset
    )


HistoryParamsDep = Annotated[HistoryParams, Depends(get_history_params)]
