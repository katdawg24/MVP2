import datetime
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

# Database connection parameters
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mvp2"

# Create database connection URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create an engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Load the existing table schema
metadata = MetaData()
readings_table = Table("readings", metadata, autoload_with=engine)
temp_arrays_table = Table("temp_arrays", metadata, autoload_with=engine)

# Function to get a new session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def store_data(data: pd.DataFrame):
        db = next(get_db())
    
        last_row = data.iloc[-1]

        time = datetime.strptime(last_row["Time"], "%Y-%m-%d %H:%M:%S")

        insert_data = {
            "time": time,
            "distance": float(last_row["Distance"]),
            "max_temp": float(last_row["Max Temp"]),
            "avg_temp": float(last_row["Avg Temp"])
        }
    
        # Insert into table
        insert_query = readings_table.insert().values(insert_data).returning(readings_table.c.id)
        reading_id = db.execute(insert_query).scalar()
        
        insert_data.clear()

        for row_index, row in enumerate(last_row["Temp"], start=1):
            insert_data = {"row_index": row_index,
                           "reading_id": reading_id}  # Start with row_index
            for col_index, value in enumerate(row):
                insert_data[f"column_{col_index + 1}"] = float(value)  # column_1 to column_32

            db.execute(temp_arrays_table.insert().values(insert_data))

        db.commit()
