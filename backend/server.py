from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class StationInfo(BaseModel):
    name: str
    description: str
    streamUrl: str
    currentShow: Optional[str] = None
    genre: Optional[str] = None
    location: Optional[str] = None
    frequency: Optional[str] = None

class RadioStation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    streamUrl: str
    currentShow: Optional[str] = None
    genre: Optional[str] = None
    location: Optional[str] = None
    frequency: Optional[str] = None
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class RadioStationCreate(BaseModel):
    name: str
    description: str
    streamUrl: str
    currentShow: Optional[str] = None
    genre: Optional[str] = None
    location: Optional[str] = None
    frequency: Optional[str] = None

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Kagema FM API"}

@api_router.get("/station-info", response_model=StationInfo)
async def get_station_info():
    """Get current station information for Kagema FM"""
    try:
        # Try to get station info from database
        station = await db.radio_stations.find_one({"name": "Kagema FM", "isActive": True})
        
        if station:
            return StationInfo(
                name=station["name"],
                description=station["description"],
                streamUrl=station["streamUrl"],
                currentShow=station.get("currentShow"),
                genre=station.get("genre"),
                location=station.get("location"),
                frequency=station.get("frequency")
            )
        else:
            # Return default Kagema FM info if not found in database
            return StationInfo(
                name="Kagema FM",
                description="Your favorite local radio station broadcasting live from Kenya",
                streamUrl="https://radio.garden/api/ara/content/listen/bSFmehrX/channel.mp3",
                currentShow="Live Radio",
                genre="Talk & Music",
                location="Kenya",
                frequency="FM 103.5"
            )
    except Exception as e:
        logging.error(f"Error fetching station info: {e}")
        # Fallback response
        return StationInfo(
            name="Kagema FM",
            description="Your favorite local radio station",
            streamUrl="https://radio.garden/api/ara/content/listen/bSFmehrX/channel.mp3",
            currentShow="Live Radio"
        )

@api_router.post("/station", response_model=RadioStation)
async def create_station(station: RadioStationCreate):
    """Create or update radio station information"""
    try:
        # Check if station already exists
        existing_station = await db.radio_stations.find_one({"name": station.name})
        
        if existing_station:
            # Update existing station
            update_data = station.dict()
            update_data["updatedAt"] = datetime.utcnow()
            
            await db.radio_stations.update_one(
                {"_id": existing_station["_id"]},
                {"$set": update_data}
            )
            
            updated_station = await db.radio_stations.find_one({"_id": existing_station["_id"]})
            return RadioStation(**updated_station)
        else:
            # Create new station
            station_dict = station.dict()
            station_obj = RadioStation(**station_dict)
            
            await db.radio_stations.insert_one(station_obj.dict())
            return station_obj
            
    except Exception as e:
        logging.error(f"Error creating/updating station: {e}")
        raise HTTPException(status_code=500, detail="Failed to create/update station")

@api_router.get("/stations", response_model=List[RadioStation])
async def get_all_stations():
    """Get all active radio stations"""
    try:
        stations = await db.radio_stations.find({"isActive": True}).to_list(100)
        return [RadioStation(**station) for station in stations]
    except Exception as e:
        logging.error(f"Error fetching stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stations")

@api_router.put("/station/{station_id}/current-show")
async def update_current_show(station_id: str, show_info: dict):
    """Update the current show for a specific station"""
    try:
        current_show = show_info.get("currentShow")
        if not current_show:
            raise HTTPException(status_code=400, detail="currentShow is required")
            
        result = await db.radio_stations.update_one(
            {"id": station_id, "isActive": True},
            {
                "$set": {
                    "currentShow": current_show,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Station not found")
            
        return {"message": "Current show updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating current show: {e}")
        raise HTTPException(status_code=500, detail="Failed to update current show")

# Original status endpoints
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()