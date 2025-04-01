import pytest
from app.services.openstreetmap_service import OpenStreetMapService
from app.models.route_model import LocationPoint

@pytest.fixture
def osm_service():
    return OpenStreetMapService()

def test_calculate_bearing(osm_service):
    # Test bearing calculation
    point1 = (10.762622, 106.660172)  # Ho Chi Minh City
    point2 = (10.762622, 106.660172)  # Same point
    bearing = osm_service._calculate_bearing(point1, point2)
    assert isinstance(bearing, float)
    assert 0 <= bearing <= 360

def test_get_direction(osm_service):
    # Test direction calculation
    assert osm_service._get_direction(0, 0) == "Continue straight"
    assert osm_service._get_direction(0, 45) == "Turn right"
    assert osm_service._get_direction(0, -45) == "Turn left"

def test_geocode_address(osm_service):
    # Test geocoding
    address = "Ben Thanh Market, Ho Chi Minh City"
    location = osm_service.geocode_address(address)
    assert isinstance(location, LocationPoint)
    assert -90 <= location.latitude <= 90
    assert -180 <= location.longitude <= 180

@pytest.mark.integration
def test_get_navigation(osm_service):
    # Test navigation service
    current = LocationPoint(latitude=10.762622, longitude=106.660172)
    destination = LocationPoint(latitude=10.762622, longitude=106.660172)
    navigation = osm_service.get_navigation(current, destination)
    assert navigation.total_distance >= 0
    assert navigation.estimated_time >= 0
    assert len(navigation.steps) > 0 