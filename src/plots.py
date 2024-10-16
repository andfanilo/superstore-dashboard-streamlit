import plotly.express as px

from src.constants import ALL_CATEGORIES


def plot_sparkline(data):
    fig = px.line(
        data,
        x="order_date",
        y="value",
        color_discrete_sequence=["#174C4F"],
    )
    fig.update_traces(line=dict(width=1.2))
    fig.update_xaxes(visible=False, fixedrange=True, showgrid=False)
    fig.update_yaxes(visible=False, fixedrange=True, showgrid=False)
    fig.update_layout(
        height=80,
        annotations=[],
        overwrite=True,
        showlegend=False,
        hovermode=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        autosize=True,
        margin=dict(t=30, l=0, b=0, r=10),
    )
    return fig


def plot_sales_detail(data):
    fig = px.line(
        data,
        x="month_year",
        y="number_of_sales",
        color="category",
        category_orders={
            "category": ALL_CATEGORIES,
        },
        title=f"Sales per selected period",
        labels={"month_year": "Month of Year", "number_of_sales": "Number of Sales"},
    )
    return fig


def plot_fm_scatter(data):
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
            "mean_profit_per_order": "Mean Profit Per Order",
        },
    ).update_traces(textposition="bottom center", marker=dict(size=14))
    return fig
