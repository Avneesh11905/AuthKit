from sqlmodel import create_engine, Session, SQLModel
import redis

# --- SQLite Setup ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Redis Setup ---
# Assumes Redis is running on localhost:6379
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
