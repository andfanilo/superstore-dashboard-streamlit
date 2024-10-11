from datetime import timedelta
from typing import Literal

import plotly.express as px
import streamlit as st
from sqlalchemy import func
from sqlalchemy import select

from src.constants import ALL_CATEGORIES
from src.dataset import query_df
from src.dataset import Superstore


def plot_sparkline(
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

    df = query_df(
        stmt.where(
            Superstore.order_date.between(
                selected_day - timedelta(days=selected_period),
                selected_day,
            )
        )
        .group_by(Superstore.order_date)
        .order_by(Superstore.order_date)
    )

    fig = px.area(
        df,
        x="order_date",
        y="value",
    )
    fig.update_xaxes(visible=False, fixedrange=True, showgrid=False)
    fig.update_yaxes(visible=False, fixedrange=True, showgrid=False)
    fig.update_layout(
        height=80,
        annotations=[],
        overwrite=True,
        showlegend=False,
        hovermode=False,
        plot_bgcolor="white",
        autosize=True,
        margin=dict(t=30, l=0, b=0, r=10),
    )

    return st.plotly_chart(
        fig,
        use_container_width=True,
        config=dict(displayModeBar=False),
    )


def plot_sales_detail(selected_day, selected_period):
    data = query_df(
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
        .order_by(Superstore.order_date)
    )
    fig = px.line(
        data,
        x="month_year",
        y="number_of_sales",
        color="category",
        category_orders={
            "category": ALL_CATEGORIES,
        },
        title=f"Last {selected_period} Days Sales",
        labels={
            "month_year": "Month of Year",
            "number_of_sales": "Number of Sales"
        }
    )
    return st.plotly_chart(
        fig,
        use_container_width=True,
    )


def plot_fm_scatter(selected_day, selected_period):
    data = query_df(
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
        .group_by(Superstore.category, Superstore.sub_category)
    )
    fig = px.scatter(
        data,
        x="number_orders",
        y="mean_profit_per_order",
        color="category",
        text="sub_category",
        hover_data=["sub_category"],
        category_orders={
            "category": ALL_CATEGORIES,
        },
        title=f"FM Matrix per sub category",
        labels={
            "number_orders": "Number or Orders",
            "mean_profit_per_order": "Mean Profit Per Order"
        }
    ).update_traces(textposition="bottom center", marker=dict(size=14))
    return st.plotly_chart(
        fig,
        use_container_width=True,
    )


def preview_orders(selected_day, selected_period):
    return st.dataframe(
        query_df(
            select(Superstore).where(
                Superstore.order_date.between(
                    selected_day - timedelta(days=selected_period), selected_day
                )
            )
        ),
        hide_index=True,
    )
