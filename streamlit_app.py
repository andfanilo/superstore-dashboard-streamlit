from datetime import timedelta

import streamlit as st
from sqlalchemy import func

from src.dataset import load_db
from src.dataset import Superstore
from src.plots import plot_fm_scatter
from src.plots import plot_sales_detail
from src.plots import plot_sparkline
from src.queries import aggregate_per_column
from src.queries import compute_delta
from src.queries import detail_per_column
from src.queries import get_fm_scatter
from src.queries import get_order_details
from src.queries import get_sales_detail

st.set_page_config(page_icon="📈", page_title="Sales Dashboard", layout="wide")
pg_connection = load_db()


st.title("Superstore Analytics")


################################################
### Row 1 - Configuration
################################################

## Precompute data

with pg_connection.session as session:
    min_date = session.scalar(func.min(Superstore.order_date))
    max_date = session.scalar(func.max(Superstore.order_date))

### Build Row

with st.expander("**Configuration**", icon="⚙"):
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

## Precompute data

n_orders, n_orders_previous_period = aggregate_per_column(
    pg_connection, Superstore.order_id, "count_distinct", selected_day, selected_period
)
n_customers, n_customers_previous_period = aggregate_per_column(
    pg_connection,
    Superstore.customer_id,
    "count_distinct",
    selected_day,
    selected_period,
)
sales, sales_previous_period = aggregate_per_column(
    pg_connection, Superstore.sales, "sum", selected_day, selected_period
)
profit, profit_previous_period = aggregate_per_column(
    pg_connection, Superstore.profit, "sum", selected_day, selected_period
)
profit_ratio = 100 * profit / sales
profit_ratio_previous_period = 100 * profit_previous_period / sales_previous_period

### Build Row

st.subheader("Overview")

cards_row = st.container(key="cards_row")

with cards_row:
    cards_columns = st.columns(4)

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
    cards_columns,
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
            data = detail_per_column(
                pg_connection, query, aggregate_func, selected_day, selected_period
            )
            fig = plot_sparkline(data)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config=dict(displayModeBar=False),
                key=f"sparkline_{label}",
            )


################################################
### Row 3 - Period detail
################################################

## Precompute data

data_sales_detail = get_sales_detail(pg_connection, selected_day, selected_period)
data_fm_scatter = get_fm_scatter(pg_connection, selected_day, selected_period)

### Build Row

chart_row = st.columns(2)

with chart_row[0]:
    fig_sales_detail = plot_sales_detail(data_sales_detail)
    st.plotly_chart(
        fig_sales_detail,
        use_container_width=True,
        key="sales_detail",
    )

with chart_row[1]:
    fig_fm_scatter = plot_fm_scatter(data_fm_scatter)
    st.plotly_chart(
        fig_fm_scatter,
        use_container_width=True,
        key="fm_scatter",
    )


################################################
### Row 4 - Order details
################################################

## Precompute data

data_orders = get_order_details(pg_connection, selected_day, selected_period)

### Build Row

with st.container(border=True):
    st.markdown("Order Details")
    st.dataframe(
        data_orders,
        hide_index=True,
        key="order_details",
    )


################################################
### Styling
################################################

st.html("""<style>
    .st-key-cards_row > .stHorizontalBlock > .stColumn {
        box-shadow: 2px 2px rgba(23, 76, 79, 0.2);
        border-radius: 12px;
    }
    .st-key-cards_row div[data-testid="stMetricValue"] {
        font-size: 1.4em;
        font-weight: 700;
        color: #174C4F;
        padding-top: 0.2rem;
        padding-bottom: 0.7rem;
    }
</style>""")
