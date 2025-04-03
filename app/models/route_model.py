from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class LocationPoint(BaseModel):
    latitude: float = Field(..., description="Latitude of the point")
    longitude: float = Field(..., description="Longitude of the point")

class NavigationRequest(BaseModel):
    current_location: LocationPoint = Field(..., description="Current GPS location")
    destination: LocationPoint = Field(..., description="Destination location")

class TextDestinationRequest(BaseModel):
    current_location: LocationPoint = Field(..., description="Current GPS location")
    destination_text: str = Field(..., description="Text description of destination location")

class NavigationStep(BaseModel):
    instruction: str = Field(..., description="Detailed navigation instruction for visually impaired")
    distance: float = Field(..., description="Distance for this step in meters")
    direction: str = Field(..., description="Direction to turn (left/right/straight)")

class NavigationResponse(BaseModel):
    total_distance: float = Field(..., description="Total distance in meters")
    estimated_time: int = Field(..., description="Estimated time in minutes")
    steps: List[NavigationStep] = Field(..., description="List of navigation steps")