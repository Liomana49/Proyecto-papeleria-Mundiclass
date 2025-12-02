import asyncio
import os
from dotenv import load_dotenv
from database import engine

load_dotenv()

async def run_migration():
    async with engine.begin() as conn:
        await conn.execute("ALTER TABLE productos ADD COLUMN IF NOT EXISTS imagen_url VARCHAR(255);")
        print("Migration completed: Added imagen_url column to productos table.")

if __name__ == "__main__":
    asyncio.run(run_migration())
