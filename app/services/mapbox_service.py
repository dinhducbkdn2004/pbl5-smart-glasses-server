import requests
from math import radians, sin, cos, sqrt, atan2
from typing import List, Tuple
from app.models.route_model import Coordinates, NavigationStep, RouteResponse

from config import MAPBOX_ACCESS_TOKEN

MAPBOX_API_URL = f'https://api.mapbox.com/directions/v5/mapbox/walking/{{coordinates}}?alternatives=false&continue_straight=true&geometries=geojson&language=vi&overview=full&steps=true&access_token={MAPBOX_ACCESS_TOKEN}'

def calculate_distance(point1: Coordinates, point2: Coordinates) -> float:
    """Tính khoảng cách giữa hai điểm theo công thức Haversine."""
    R = 6371  # Bán kính trái đất (km)
    
    lat1, lon1 = radians(point1.latitude), radians(point1.longitude)
    lat2, lon2 = radians(point2.latitude), radians(point2.longitude)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def get_bearing_direction(bearing: float) -> str:
    """Chuyển đổi góc (bearing) thành hướng dẫn bằng tiếng Việt."""
    if 337.5 <= bearing <= 360 or 0 <= bearing < 22.5:
        return "hướng Bắc"
    elif 22.5 <= bearing < 67.5:
        return "hướng Đông Bắc"
    elif 67.5 <= bearing < 112.5:
        return "hướng Đông"
    elif 112.5 <= bearing < 157.5:
        return "hướng Đông Nam"
    elif 157.5 <= bearing < 202.5:
        return "hướng Nam"
    elif 202.5 <= bearing < 247.5:
        return "hướng Tây Nam"
    elif 247.5 <= bearing < 292.5:
        return "hướng Tây"
    else:
        return "hướng Tây Bắc"

def format_distance(distance: float) -> str:
    """Định dạng khoảng cách thành văn bản tiếng Việt."""
    if distance < 1:
        return f"{int(distance * 1000)} mét"
    return f"{distance:.1f} ki-lô-mét"

def format_duration(duration: float) -> str:
    """Định dạng thời gian thành văn bản tiếng Việt."""
    minutes = int(duration / 60)
    if minutes < 1:
        return "khoảng một phút"
    return f"khoảng {minutes} phút"

def enhance_instruction(instruction: str, distance: float, bearing: float) -> str:
    """Tạo hướng dẫn chi tiết bằng tiếng Việt."""
    direction = get_bearing_direction(bearing)
    distance_text = format_distance(distance/1000)  # Convert to km
    
    # Cải thiện hướng dẫn
    instruction = instruction.replace("Turn right", "Rẽ phải")
    instruction = instruction.replace("Turn left", "Rẽ trái")
    instruction = instruction.replace("Continue straight", "Đi thẳng")
    
    # Thêm thông tin chi tiết
    enhanced = f"{instruction} và đi {distance_text} theo {direction}"
    if "Rẽ" in instruction:
        steps = int((distance/1000) * 1250)  # Ước tính số bước (trung bình 1.25 bước/mét)
        enhanced += f" (khoảng {steps} bước)"
        
    return enhanced

async def get_route(current_location: Coordinates, destination_name: str) -> RouteResponse:
    """Lấy thông tin chỉ đường từ Mapbox API và tạo hướng dẫn chi tiết."""
    # Trước tiên, chuyển đổi tên địa điểm thành tọa độ
    geocoding_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{destination_name}.json?access_token={MAPBOX_ACCESS_TOKEN}"
    geocoding_response = requests.get(geocoding_url)
    geocoding_data = geocoding_response.json()
    
    if not geocoding_data["features"]:
        raise ValueError("Không tìm thấy địa điểm này")
        
    destination_coords = geocoding_data["features"][0]["center"]
    coordinates = f"{current_location.longitude},{current_location.latitude};{destination_coords[0]},{destination_coords[1]}"
    
    # Lấy chỉ đường từ Mapbox
    response = requests.get(MAPBOX_API_URL.format(coordinates=coordinates))
    data = response.json()
    
    if "routes" not in data or not data["routes"]:
        raise ValueError("Không thể tìm được đường đi")
        
    route = data["routes"][0]
    steps: List[NavigationStep] = []
    
    for leg in route["legs"]:
        for step in leg["steps"]:
            enhanced_instruction = enhance_instruction(
                step["maneuver"]["instruction"],
                step["distance"],
                step["maneuver"]["bearing_after"]
            )
            
            steps.append(NavigationStep(
                instruction=enhanced_instruction,
                distance=step["distance"],
                duration=step["duration"],
                bearing=step["maneuver"]["bearing_after"]
            ))
    
    return RouteResponse(
        total_distance=route["distance"] / 1000,  # Convert to km
        total_duration=route["duration"] / 60,    # Convert to minutes
        steps=steps
    )
