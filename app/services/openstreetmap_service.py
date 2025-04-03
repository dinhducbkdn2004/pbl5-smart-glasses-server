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
        
        if angle_diff > 20:
            return "Rẽ Phải"
        elif angle_diff < -20:
            return "Rẽ Trái"
        else:
            return "Đi Thẳng"

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
                    
                    # Xử lý trường hợp đã đến đích
                    if step["distance"] == 0 and step == leg["steps"][-1]:
                        steps.append(NavigationStep(
                            instruction="Đích đến đang ở vị trí hiện tại.",
                            distance=0,
                            direction=direction
                        ))
                        continue
                        
                    # Bỏ qua các bước có distance = 0 trừ bước cuối cùng
                    if step["distance"] == 0 and step != leg["steps"][-1]:
                        continue
                    
                    # Cải thiện cấu trúc instruction
                    instruction = []
                    
                    # Thêm thông tin vị trí hiện tại
                    if "name" in step and step["name"]:
                        instruction.append(f"Bạn đang đi trên {step['name']}")
                    
                    # Thêm hướng dẫn rẽ
                    if direction:
                        if direction == "Đi Thẳng":
                            instruction.append("Tiếp tục đi thẳng")
                        else:
                            instruction.append(f"Đi đến điểm rẽ: {direction}")
                    elif not instruction:  # Nếu không có tên đường và không có hướng rẽ
                        instruction.append("Đi thẳng trên đường này")
                    
                    # Thêm khoảng cách
                    if step["distance"] > 0:
                        distance = step["distance"]
                        if distance > 1000:
                            # Làm tròn đến 1 chữ số thập phân khi chuyển sang km
                            distance_km = round(distance / 1000, 1)
                            instruction.append(f"Đi tiếp {distance_km} ki lô mét")
                        else:
                            instruction.append(f"Đi tiếp {int(distance)} mét")
                    
                    # Kết hợp các phần instruction
                    instruction = ". ".join(instruction) + "."
                    
                    steps.append(NavigationStep(
                        instruction=instruction,
                        
                        distance=step["distance"],
                        direction=direction,
                    ))
            
            # Tính thời gian ước tính dựa trên:
            # - WALKING_SPEED_MPS: Tốc độ đi bộ trung bình (mét/giây)
            # - SECONDS_PER_MINUTE: Số giây trong 1 phút
            WALKING_SPEED_MPS = 1  # 2 km/h = 0.6 m/s
            SECONDS_PER_MINUTE = 60
            
            estimated_time = int(total_distance / (WALKING_SPEED_MPS * SECONDS_PER_MINUTE))
            
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