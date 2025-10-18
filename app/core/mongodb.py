"""
MongoDB database connection and initialization
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

from app.core.config import settings
from app.mongodb_models import Spreadsheet, SpreadsheetChange


class MongoDB:
    """MongoDB connection manager"""
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB and initialize Beanie"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Initialize Beanie with document models
        await init_beanie(
            database=cls.client[settings.MONGODB_DB_NAME],
            document_models=[
                Spreadsheet,
                SpreadsheetChange,
            ]
        )
        print(f"Connected to MongoDB at {settings.MONGODB_HOST}:{settings.MONGODB_PORT}")
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("Closed MongoDB connection")


# Dependency to get MongoDB client
async def get_mongodb():
    """Get MongoDB client"""
    return MongoDB.client
