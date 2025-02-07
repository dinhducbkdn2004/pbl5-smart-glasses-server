from pydantic import BaseModel
from typing import List, Optional

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class RouteRequest(BaseModel):
    current_location: Coordinates
    destination_name: str

class NavigationStep(BaseModel):
    instruction: str
    distance: float  # in meters
    duration: float  # in seconds
    bearing: float   # direction in degrees
    
class RouteResponse(BaseModel):
    total_distance: float    # in kilometers
    total_duration: float    # in minutes
    steps: List[NavigationStep]
    current_step_index: Optional[int] = 0
