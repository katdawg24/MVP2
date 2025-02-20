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
