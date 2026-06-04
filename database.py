from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import redis.asyncio as redis
import os

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
redis_host = os.getenv("REDIS_HOST", "localhost")

Base = declarative_base()

DATABASE_URL = f"postgresql+asyncpg://postgres:{db_password}@{db_host}:5432/test"

engine = create_async_engine(
    DATABASE_URL,
    echo = True)

cache = redis.Redis(host = redis_host, port = 6379, decode_responses = True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with AsyncSession(engine) as session:
        yield session