import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = os.getenv('MONGO_DB', 'footydb')

client: AsyncIOMotorClient | None = None
db = None

async def connect():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    # create indexes
    await db.plays.create_index([('quiz_id', 1), ('username', 1)], unique=True)
    await db.leaderboard.create_index([('username', 1)], unique=True)

async def close():
    global client
    if client:
        client.close()
