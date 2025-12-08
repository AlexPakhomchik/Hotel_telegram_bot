import asyncpg

async def create_pool():
    pool = await asyncpg.create_pool(
        user='postgres',
        password='3327',
        database='hotel_bot',
        host='localhost'
    )
    return pool
