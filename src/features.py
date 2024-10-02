from datetime import timedelta
from typing import Literal

from sqlalchemy import func
from sqlalchemy import select

from src.dataset import query_scalar
from src.dataset import Superstore


def count_aggregate_per_column(
    column_stmt,
    aggregate_func: Literal["sum", "count_distinct", "avg"],
    selected_day,
    selected_period,
):
    stmt: str
    match aggregate_func:
        case "sum":
            stmt = select(func.sum(column_stmt))
        case "count_distinct":
            stmt = select(func.count(func.distinct(column_stmt)))

    result_period = query_scalar(
        stmt.where(
            Superstore.order_date.between(
                selected_day - timedelta(days=selected_period),
                selected_day,
            )
        )
    )
    result_last_period = query_scalar(
        stmt.where(
            Superstore.order_date.between(
                selected_day - timedelta(days=2 * selected_period),
                selected_day - timedelta(days=selected_period),
            )
        )
    )
    return result_period, result_last_period


def compute_delta(metric, metric_previous_period):
    return 100 * (metric - metric_previous_period) / metric
