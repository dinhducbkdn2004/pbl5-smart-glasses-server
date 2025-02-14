from fastapi import APIRouter, HTTPException
from app.models.route_model import NavigationRequest, NavigationResponse, TextDestinationRequest
from app.services.openstreetmap_service import OpenStreetMapService

router = APIRouter(prefix="/api/v1")

# Initialize OpenStreetMap service
osm_service = OpenStreetMapService()

@router.post("/navigation", response_model=NavigationResponse, tags=["Navigation"])
async def get_navigation(request: NavigationRequest):
    """Get navigation instructions from current location to destination coordinates.

    This endpoint provides detailed navigation instructions specifically designed 
    for visually impaired users, including:
    - Step-by-step directions with specific landmarks
    - Distance information for each step
    - Estimated total time
    - Clear turning instructions
    """
    try:
        navigation = osm_service.get_navigation(
            current=request.current_location,
            destination=request.destination
        )
        return navigation
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get navigation instructions: {str(e)}"
        )


@router.post("/navigation/by-text", response_model=NavigationResponse, tags=["Navigation"])
async def get_navigation_by_text(request: TextDestinationRequest):
    """Get navigation instructions from current location to a text-based destination.

    This endpoint converts a text address into coordinates and then provides 
    detailed navigation instructions for visually impaired users.
    """
    try:
        # Convert text address to coordinates
        destination_coords = osm_service.geocode_address(request.destination_text)
        
        # Get navigation with converted coordinates
        navigation = osm_service.get_navigation(
            current=request.current_location,
            destination=destination_coords
        )
        return navigation
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get navigation instructions: {str(e)}"
        )