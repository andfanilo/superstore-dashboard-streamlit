from datetime import timedelta
from typing import Literal

import pandas as pd
from sqlalchemy import func
from sqlalchemy import select
from streamlit.connections import SQLConnection

from src.dataset import Superstore


def aggregate_per_column(
    st_connection: SQLConnection,
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

    with st_connection.session as session:
        result_period = session.scalar(
            stmt.where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=selected_period),
                    selected_day,
                )
            )
        )
        result_last_period = session.scalar(
            stmt.where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=2 * selected_period),
                    selected_day - timedelta(days=selected_period),
                )
            )
        )
    return result_period, result_last_period


def detail_per_column(
    st_connection: SQLConnection,
    column_stmt,
    aggregate_func: Literal["sum", "count_distinct", "avg"],
    selected_day,
    selected_period,
):
    stmt: str
    match aggregate_func:
        case "sum":
            stmt = select(
                Superstore.order_date,
                func.sum(column_stmt).label("value"),
            )
        case "count_distinct":
            stmt = select(
                Superstore.order_date,
                func.count(func.distinct(column_stmt)).label("value"),
            )
        case "avg":
            stmt = select(
                Superstore.order_date,
                func.avg(column_stmt).label("value"),
            )

    with st_connection.connect() as sql_connection:
        df = pd.read_sql_query(
            stmt.where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=selected_period),
                    selected_day,
                )
            )
            .group_by(Superstore.order_date)
            .order_by(Superstore.order_date),
            sql_connection,
        )

    return df


def compute_delta(metric, metric_previous_period):
    return 100 * (metric - metric_previous_period) / metric


def get_sales_detail(
    st_connection: SQLConnection,
    selected_day,
    selected_period,
):
    with st_connection.connect() as sql_connection:
        df = pd.read_sql_query(
            select(
                Superstore.category,
                Superstore.order_date.label("month_year"),
                func.count(Superstore.order_id).label("number_of_sales"),
            )
            .where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=selected_period), selected_day
                )
            )
            .group_by(Superstore.order_date, Superstore.category)
            .order_by(Superstore.order_date),
            sql_connection,
        )

    return df


def get_fm_scatter(
    st_connection: SQLConnection,
    selected_day,
    selected_period,
):
    with st_connection.connect() as sql_connection:
        df = pd.read_sql_query(
            select(
                func.count().label("number_orders"),
                func.avg(Superstore.profit).label("mean_profit_per_order"),
                Superstore.category,
                Superstore.sub_category,
            )
            .where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=selected_period), selected_day
                )
            )
            .group_by(Superstore.category, Superstore.sub_category),
            sql_connection,
        )

    return df


def get_order_details(
    st_connection: SQLConnection,
    selected_day,
    selected_period,
):
    with st_connection.connect() as sql_connection:
        df = pd.read_sql_query(
            select(Superstore).where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=selected_period), selected_day
                )
            ),
            sql_connection,
        )

    return df
