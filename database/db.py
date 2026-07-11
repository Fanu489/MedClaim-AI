from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

DB_USER = "postgres"
DB_PASSWORD = quote_plus("Fanu@001.")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "medclaim_ai_db"

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

def run_query(query):
    return pd.read_sql(query, engine)