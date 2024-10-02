from datetime import timedelta

import streamlit as st
from sqlalchemy import func
from sqlalchemy import select

from src.components import plot_fm_scatter
from src.components import plot_sales_detail
from src.components import plot_sparkline
from src.components import plot_top_products
from src.components import preview_orders
from src.constants import ALL_CATEGORIES
from src.dataset import query_df
from src.dataset import query_scalar
from src.dataset import Superstore
from src.features import compute_delta
from src.features import count_aggregate_per_column


st.set_page_config(page_icon="📈", page_title="Sales Dashboard", layout="wide")


st.title("Superstore Analytics")


################################################
### Row 1 - Configuration
################################################

with st.expander("**Configuration**", icon="⚙"):
    min_date = query_scalar(func.min(Superstore.order_date))
    max_date = query_scalar(func.max(Superstore.order_date))
    configuration_row = st.columns(
        [1, 1, 0.5, 1.5], gap="large", vertical_alignment="bottom"
    )
    selected_day = configuration_row[0].date_input(
        "End date", min_value=min_date, max_value=max_date
    )
    selected_period = configuration_row[1].selectbox(
        "Analysis Period", [7, 28, 90, 365], index=1, format_func=lambda n: f"{n} days"
    )
    configuration_row[3].subheader(
        f"Period: {selected_day - timedelta(days=selected_period)} -> {selected_day}"
    )

################################################
### Row 2 - Row Card KPIs
################################################

### Precompute KPIs

st.subheader("Overview")

n_orders, n_orders_previous_period = count_aggregate_per_column(
    Superstore.order_id, "count_distinct", selected_day, selected_period
)
n_customers, n_customers_previous_period = count_aggregate_per_column(
    Superstore.customer_id, "count_distinct", selected_day, selected_period
)
sales, sales_previous_period = count_aggregate_per_column(
    Superstore.sales, "sum", selected_day, selected_period
)
profit, profit_previous_period = count_aggregate_per_column(
    Superstore.profit, "sum", selected_day, selected_period
)
profit_ratio = 100 * profit / sales
profit_ratio_previous_period = 100 * profit_previous_period / sales_previous_period

### Build Row

cards_row = st.columns(4)

for (label, value, previous_value, query, aggregate_func, format_str), column in zip(
    [
        (
            "Number Orders",
            n_orders,
            n_orders_previous_period,
            Superstore.order_id,
            "count_distinct",
            str,
        ),
        (
            "Total Sales",
            sales,
            sales_previous_period,
            Superstore.sales,
            "sum",
            lambda value: f"{value:,.2f} $".replace(",", " "),
        ),
        (
            "Total Profit",
            profit,
            profit_previous_period,
            Superstore.profit,
            "sum",
            lambda value: f"{value:,.2f} $".replace(",", " "),
        ),
        (
            "Profit Ratio",
            profit_ratio,
            profit_ratio_previous_period,
            (100 * Superstore.profit / Superstore.sales),
            "avg",
            lambda value: f"{value:,.2f}".replace(",", " "),
        ),
    ],
    cards_row,
):
    with column.container(border=True):
        card = st.columns((1, 1), vertical_alignment="bottom")
        with card[0]:
            st.metric(
                label=label,
                value=format_str(value) if isinstance(value, float) else value,
                delta=f"{compute_delta(value, previous_value):.2f} %",
            )
        with card[1]:
            plot_sparkline(query, aggregate_func, selected_day, selected_period)


################################################
### Row 3 - Period detail
################################################

chart_row = st.columns(2)

with chart_row[0]:
    plot_sales_detail(selected_day, selected_period)

with chart_row[1]:
    plot_fm_scatter(selected_day, selected_period)


################################################
### Row 4 - Top Products
################################################

st.subheader("Top Products per sub-category")

filter_row = st.columns((1, 1, 2), gap="large")
selected_category = filter_row[0].selectbox("Select Category", ALL_CATEGORIES)
selected_sub_category = filter_row[1].selectbox(
    "Select Sub Category",
    query_df(
        select(Superstore.sub_category)
        .where(Superstore.category == selected_category)
        .distinct()
    ),
)

plot_top_products(selected_day, selected_period, selected_sub_category)

################################################
### Row 5 - Order details
################################################

with st.container(border=True):
    st.markdown("Order Details")
    preview_orders(selected_day, selected_period)
