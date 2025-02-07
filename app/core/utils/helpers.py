from typing import Dict, Optional
from fastapi import WebSocket
import json
import asyncio
from app.models.route_model import Coordinates, RouteResponse

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """Thiết lập kết nối WebSocket mới."""
        await websocket.accept()
        self.active_connections[client_id] = {
            "websocket": websocket,
            "route": None,
            "alert_task": None
        }
    
    def disconnect(self, client_id: str):
        """Đóng kết nối WebSocket."""
        if client_id in self.active_connections:
            if self.active_connections[client_id]["alert_task"]:
                self.active_connections[client_id]["alert_task"].cancel()
            del self.active_connections[client_id]
    
    async def send_navigation_update(self, client_id: str, message: dict):
        """Gửi cập nhật điều hướng đến client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id]["websocket"].send_json(message)
    
    async def broadcast_alert(self, message: str):
        """Gửi cảnh báo đến tất cả clients đang kết nối."""
        for connection in self.active_connections.values():
            await connection["websocket"].send_json({"alert": message})
    
    def set_route(self, client_id: str, route: RouteResponse):
        """Cập nhật tuyến đường cho client."""
        if client_id in self.active_connections:
            self.active_connections[client_id]["route"] = route
    
    def get_route(self, client_id: str) -> Optional[RouteResponse]:
        """Lấy tuyến đường hiện tại của client."""
        if client_id in self.active_connections:
            return self.active_connections[client_id]["route"]
        return None

class NavigationHelper:
    @staticmethod
    def format_step_count(meters: float) -> str:
        """Chuyển đổi khoảng cách thành số bước đi ước tính."""
        steps = int(meters * 1.25)  # Trung bình 1.25 bước/mét
        return f"khoảng {steps} bước"
    
    @staticmethod
    def format_time_remaining(seconds: float) -> str:
        """Định dạng thời gian còn lại thành văn bản tiếng Việt."""
        minutes = int(seconds / 60)
        if minutes < 1:
            return "dưới một phút"
        return f"khoảng {minutes} phút"
    
    @staticmethod
    def generate_detailed_instruction(instruction: str, distance: float, next_turn: Optional[str] = None) -> str:
        """Tạo hướng dẫn chi tiết bằng tiếng Việt."""
        step_count = NavigationHelper.format_step_count(distance)
        base_instruction = f"{instruction} ({step_count})"
        
        if next_turn:
            base_instruction += f". Sau đó {next_turn}"
        
        return base_instruction

    @staticmethod
    def get_direction_warning(distance: float) -> Optional[str]:
        """Tạo cảnh báo dựa trên khoảng cách đến điểm rẽ tiếp theo."""
        if distance <= 5:
            return "Chuẩn bị rẽ"
        elif distance <= 20:
            return f"Sắp đến điểm rẽ trong {int(distance)} mét"
        return None

class SafetyMonitor:
    def __init__(self):
        self.obstacle_threshold = 1.5  # meters
        self.direction_change_threshold = 45  # degrees
    
    async def monitor_obstacles(self, coordinates: Coordinates) -> Optional[str]:
        """Giả lập kiểm tra chướng ngại vật (cần tích hợp với sensors thực tế)."""
        # Implement actual obstacle detection here
        return None
    
    async def check_sudden_direction_change(self, current_bearing: float, new_bearing: float) -> bool:
        """Kiểm tra thay đổi hướng đột ngột."""
        bearing_diff = abs(current_bearing - new_bearing)
        return bearing_diff > self.direction_change_threshold

class VoiceInstructionGenerator:
    @staticmethod
    def generate_voice_instruction(instruction: str, distance: float, is_approaching: bool = False) -> str:
        """Tạo hướng dẫn bằng giọng nói theo ngữ cảnh."""
        if is_approaching:
            return f"Chuẩn bị {instruction.lower()} trong {int(distance)} mét"
        
        base = instruction
        if distance > 0:
            step_count = NavigationHelper.format_step_count(distance)
            base += f". Đi {step_count}"
        
        return base