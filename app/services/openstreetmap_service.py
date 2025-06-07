import requests
from typing import List, Tuple, Dict
from app.models.route_model import LocationPoint, NavigationStep, NavigationResponse
import math
import urllib.parse
from functools import lru_cache
from app.core.logging import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

class OpenStreetMapService:
    def __init__(self):
        self.osrm_url = "http://router.project-osrm.org/route/v1/foot"
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "SmartGlassesNavigationApp/1.0"
        self._cache = {}
        
        retry_strategy = Retry(
            total=3, 
            backoff_factor=1,  
            status_forcelist=[500, 502, 503, 504], 
        )
        
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @lru_cache(maxsize=1000)
    def _calculate_bearing(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        d_lon = lon2 - lon1
        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360

    @lru_cache(maxsize=1000)
    def _get_direction(self, prev_bearing: float, next_bearing: float) -> str:
        angle_diff = ((next_bearing - prev_bearing + 180) % 360) - 180
        
        if angle_diff > 45:
            return "Rẽ phải vuông góc"
        elif angle_diff > 20:
            return "Rẽ phải nhẹ"
        elif angle_diff < -45:
            return "Rẽ trái vuông góc"
        elif angle_diff < -20:
            return "Rẽ trái nhẹ"
        else:
            return "Tiếp tục đi thẳng"

    def _format_distance(self, distance: float) -> str:
        if distance < 5:  # Giảm ngưỡng từ 10m xuống 5m
            return "ngay phía trước"
        elif distance < 20:  # Giảm ngưỡng từ 50m xuống 20m
            return "khoảng 30 bước chân phía trước"
        elif distance < 50:  # Giảm ngưỡng từ 100m xuống 50m
            return "khoảng 80 bước chân phía trước"
        else:
            # Giả sử mỗi bước chân dài khoảng 0.6 mét (phù hợp với tốc độ đi chậm và thận trọng)
            steps = int(distance / 0.6)
            if steps > 200:  # Nếu số bước quá lớn, chuyển sang đơn vị phút
                minutes = int(distance / (0.6 * 60))  # Giả sử tốc độ đi bộ 0.6m/bước, 60 bước/phút
                return f"khoảng {minutes} phút đi bộ phía trước"
            return f"khoảng {steps} bước chân phía trước"

    def _make_request(self, url: str, params: Dict = None, headers: Dict = None, timeout: int = 30) -> Dict:
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error(f"Request timeout for URL: {url}")
            raise Exception("Request timeout. Please try again.")
        except requests.RequestException as e:
            logger.error(f"Request error for URL {url}: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")

    @lru_cache(maxsize=1000)
    def geocode_address(self, address: str) -> LocationPoint:
        cache_key = f"geocode_{address}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for address: {address}")
            return self._cache[cache_key]

        params = {
            'q': address,
            'format': 'json',
            'countrycodes': 'vn',
            'limit': 1
        }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            results = self._make_request(self.nominatim_url, params=params, headers=headers, timeout=10)
            
            if not results:
                raise ValueError(f"No location found for address: {address}")
            
            location = results[0]
            result = LocationPoint(
                latitude=float(location['lat']),
                longitude=float(location['lon'])
            )
            
            # Cache kết quả
            self._cache[cache_key] = result
            logger.debug(f"Cached geocoding result for: {address}")
            
            return result
        except Exception as e:
            logger.error(f"Error during geocoding: {str(e)}")
            raise

    def get_navigation(self, current: LocationPoint, destination: LocationPoint) -> NavigationResponse:
        """Get navigation instructions from current location to destination with caching."""
        cache_key = f"nav_{current.latitude}_{current.longitude}_{destination.latitude}_{destination.longitude}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for navigation")
            return self._cache[cache_key]

        coords = f"{current.longitude},{current.latitude};{destination.longitude},{destination.latitude}"
        url = f"{self.osrm_url}/{coords}?steps=true&annotations=true&overview=full"
        
        try:
            data = self._make_request(url, timeout=30)
            
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
                    
                    # Xây dựng hướng dẫn chi tiết
                    instruction = ""
                    
                    # Thêm thông tin về vị trí hiện tại
                    if "name" in step and step["name"]:
                        instruction = f"Bạn đang đi trên {step.get('name')}. "
                    
                    # Thêm hướng dẫn về điểm mốc và rẽ
                    if direction != "Tiếp tục đi thẳng":
                        instruction += f"Tại điểm rẽ phía trước, {direction.lower()}. "
                        if step.get('name'):
                            instruction += f"Bạn sẽ rẽ vào {step.get('name')}. "
                    else:
                        instruction += f"{direction} trên {step.get('name', 'đường này')}. "
                    
                    # Thêm thông tin về khoảng cách
                    if step["distance"] > 0:
                        distance_text = self._format_distance(step["distance"])
                        instruction += f"Đi tiếp {distance_text}"
                        
                        # Thêm thông tin về điểm mốc tiếp theo nếu có
                        if len(step["intersections"]) > 1:
                            instruction += ", bạn sẽ gặp một ngã rẽ"
                    
                    # Thêm cảnh báo về địa hình hoặc chướng ngại vật nếu có
                    if "lanes" in step and step["lanes"] > 1:
                        instruction += f". Chú ý đây là đường có {step['lanes']} làn xe"
                    
                    steps.append(NavigationStep(
                        instruction=instruction,
                        
                        distance=step["distance"],
                        direction=direction,
                    ))
            
            estimated_time = int(total_distance / (1.4 * 60))
            
            result = NavigationResponse(
                total_distance=total_distance,
                estimated_time=estimated_time,
                steps=steps
            )
            
            # Cache kết quả
            self._cache[cache_key] = result
            logger.debug(f"Cached navigation result")
            
            return result
        except Exception as e:
            logger.error(f"Error processing route data: {str(e)}")
            raise