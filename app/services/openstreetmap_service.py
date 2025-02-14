import requests
from typing import List, Tuple, Dict
from app.models.route_model import LocationPoint, NavigationStep, NavigationResponse
import math
import urllib.parse

class OpenStreetMapService:
    def __init__(self):
        self.osrm_url = "http://router.project-osrm.org/route/v1/foot"
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "SmartGlassesNavigationApp/1.0"

    def _calculate_bearing(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate the bearing between two points."""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        d_lon = lon2 - lon1
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360

    def _get_direction(self, prev_bearing: float, next_bearing: float) -> str:
        """Get human-readable direction based on bearing change."""
        angle_diff = ((next_bearing - prev_bearing + 180) % 360) - 180
        
        if abs(angle_diff) < 20:
            return "Continue straight"
        elif angle_diff > 0:
            return "Turn right"
        else:
            return "Turn left"

    def geocode_address(self, address: str) -> LocationPoint:
        """Convert text address to coordinates using Nominatim."""
        params = {
            'q': address,
            'format': 'json',
            'countrycodes': 'vn',  # Bias results to Vietnam
            'limit': 1
        }
        
        headers = {
            'User-Agent': self.user_agent  # Required by Nominatim's terms of use
        }
        
        try:
            response = requests.get(
                self.nominatim_url,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            results = response.json()
            
            if not results:
                raise ValueError(f"No location found for address: {address}")
            
            location = results[0]
            return LocationPoint(
                latitude=float(location['lat']),
                longitude=float(location['lon'])
            )
        except requests.RequestException as e:
            raise Exception(f"Error during geocoding: {str(e)}")

    def get_navigation(self, current: LocationPoint, destination: LocationPoint) -> NavigationResponse:
        """Get navigation instructions from current location to destination."""
        coords = f"{current.longitude},{current.latitude};{destination.longitude},{destination.latitude}"
        url = f"{self.osrm_url}/{coords}?steps=true&annotations=true&overview=full"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "routes" not in data or not data["routes"]:
                raise ValueError("No route found")

            route = data["routes"][0]
            steps = []
            total_distance = 0
            prev_bearing = None
            
            for leg in route["legs"]:
                total_distance += leg["distance"]
                
                for step in leg["steps"]:
                    start_point = (step["maneuver"]["location"][1], step["maneuver"]["location"][0])
                    end_point = None
                    
                    if len(step["intersections"]) > 1:
                        end_loc = step["intersections"][1]["location"]
                        end_point = (end_loc[1], end_loc[0])
                    elif "next" in step:
                        end_point = (step["next"]["location"][1], step["next"]["location"][0])
                    else:
                        end_point = start_point
                    
                    current_bearing = self._calculate_bearing(start_point, end_point)
                    direction = ""
                    if prev_bearing is not None:
                        direction = self._get_direction(prev_bearing, current_bearing)
                    prev_bearing = current_bearing
                    
                    instruction = f"{direction}. {step.get('name', 'the path')}."
                    if step["distance"] > 0:
                        instruction += f" Continue for {int(step['distance'])} meters."
                    
                    if "name" in step and step["name"]:
                        instruction = f"You are on {step['name']}. " + instruction

                    if direction:
                        instruction = f"At the next intersection: {instruction}"
                    
                    steps.append(NavigationStep(
                        instruction=instruction,
                        distance=step["distance"],
                        direction=direction,
                        landmarks=[]
                    ))
            
            estimated_time = int(total_distance / (1.4 * 60))  # Convert to minutes
            
            return NavigationResponse(
                total_distance=total_distance,
                estimated_time=estimated_time,
                steps=steps
            )
        except requests.RequestException as e:
            raise Exception(f"Error fetching route: {str(e)}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Error processing route data: {str(e)}")