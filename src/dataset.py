import pandas as pd
import streamlit as st
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass


class Superstore(Base):
    __tablename__ = "superstore"

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False)
    order_date = Column(DateTime, nullable=False)
    ship_date = Column(DateTime, nullable=False)
    ship_mode = Column(String, nullable=True)
    customer_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    segment = Column(String, nullable=True)
    country_region = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state_province = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    region = Column(String, nullable=True)
    product_id = Column(String, nullable=False)
    category = Column(String, nullable=True)
    sub_category = Column(String, nullable=True)
    product_name = Column(String, nullable=False)
    sales = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=False)
    discount = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, customer_name={self.customer_name}, product_name={self.product_name})>"


@st.cache_resource
def load_db():
    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
    )
    return engine


def query_df(statement):
    engine = load_db()
    return pd.read_sql_query(statement, engine)


def query_scalar(statement):
    engine = load_db()
    with Session(engine) as session:
        return session.scalar(statement)
