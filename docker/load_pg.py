import pandas as pd

from sqlalchemy import create_engine

df = pd.read_excel("./docker/Superstore 2024.xls")
df.columns = (
    df.columns.str.lower()
    .str.replace(" ", "_")
    .str.replace("/", "_")
    .str.replace("-", "_")
)

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)
df.to_sql("superstore", engine, if_exists="replace", index=False)
