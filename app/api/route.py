from fastapi import APIRouter, WebSocket, HTTPException
from typing import Dict
import json
import asyncio
from app.models.route_model import RouteRequest, RouteResponse, Coordinates
from app.services.mapbox_service import get_route, calculate_distance
from app.core.utils.helpers import ConnectionManager, NavigationHelper, SafetyMonitor, VoiceInstructionGenerator

router = APIRouter()

# Khởi tạo các managers và helpers
connection_manager = ConnectionManager()
safety_monitor = SafetyMonitor()
voice_generator = VoiceInstructionGenerator()

@router.post("/get_route", response_model=RouteResponse)
async def get_route_endpoint(request: RouteRequest):
    """API endpoint để lấy thông tin chỉ đường ban đầu."""
    try:
        route = await get_route(request.current_location, request.destination_name)
        return route
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi server khi tìm đường đi")

@router.websocket("/ws/navigation/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint cho hướng dẫn điều hướng thời gian thực."""
    await connection_manager.connect(client_id, websocket)
    
    try:
        while True:
            # Nhận cập nhật vị trí từ client
            data = await websocket.receive_text()
            location_update = json.loads(data)
            
            current_location = Coordinates(
                latitude=location_update["latitude"],
                longitude=location_update["longitude"]
            )
            
            # Kiểm tra yêu cầu tìm đường mới
            if "destination_name" in location_update:
                request = RouteRequest(
                    current_location=current_location,
                    destination_name=location_update["destination_name"]
                )
                route = await get_route(request.current_location, request.destination_name)
                connection_manager.set_route(client_id, route)
                
                # Gửi hướng dẫn ban đầu
                initial_guidance = await generate_guidance(route, current_location, True)
                await connection_manager.send_navigation_update(client_id, initial_guidance)
                
                # Bắt đầu task giám sát an toàn
                asyncio.create_task(safety_monitoring_task(client_id, websocket))
            
            # Cập nhật hướng dẫn cho tuyến đường hiện tại
            else:
                route = connection_manager.get_route(client_id)
                if route:
                    guidance = await generate_guidance(route, current_location)
                    await connection_manager.send_navigation_update(client_id, guidance)
                    
                    # Kiểm tra chướng ngại vật
                    obstacle_warning = await safety_monitor.monitor_obstacles(current_location)
                    if obstacle_warning:
                        await connection_manager.send_navigation_update(client_id, {
                            "alert": f"Cảnh báo: {obstacle_warning}",
                            "type": "obstacle"
                        })
    
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {str(e)}")
    finally:
        connection_manager.disconnect(client_id)

async def generate_guidance(route: RouteResponse, current_location: Coordinates, is_initial: bool = False) -> dict:
    """Tạo hướng dẫn chi tiết dựa trên vị trí hiện tại."""
    if not route.steps:
        return {
            "message": "Bạn đã đến đích",
            "type": "destination_reached"
        }
    
    current_step = route.steps[route.current_step_index]
    next_step = route.steps[route.current_step_index + 1] if route.current_step_index < len(route.steps) - 1 else None
    
    # Tính khoảng cách đến điểm tiếp theo
    distance_to_next = calculate_distance(current_location, Coordinates(
        latitude=next_step.latitude if next_step else route.steps[-1].latitude,
        longitude=next_step.longitude if next_step else route.steps[-1].longitude
    )) * 1000  # Chuyển đổi sang mét
    
    # Kiểm tra xem đã đến điểm rẽ chưa
    if distance_to_next <= 5:  # Trong vòng 5 mét
        route.current_step_index += 1
        if route.current_step_index >= len(route.steps):
            return {
                "message": "Bạn đã đến đích",
                "type": "destination_reached"
            }
        
        current_step = route.steps[route.current_step_index]
        next_step = route.steps[route.current_step_index + 1] if route.current_step_index < len(route.steps) - 1 else None
    
    # Tạo hướng dẫn chi tiết
    instruction = current_step.instruction
    is_approaching = distance_to_next <= 20  # 20 mét
    
    voice_instruction = voice_generator.generate_voice_instruction(
        instruction, 
        distance_to_next,
        is_approaching
    )
    
    detailed_instruction = NavigationHelper.generate_detailed_instruction(
        instruction,
        distance_to_next,
        next_step.instruction if next_step else None
    )
    
    return {
        "voice_instruction": voice_instruction,
        "text_instruction": detailed_instruction,
        "distance_remaining": distance_to_next,
        "next_turn_distance": distance_to_next if next_step else None,
        "step_index": route.current_step_index,
        "total_steps": len(route.steps),
        "type": "navigation_update",
        "is_approaching": is_approaching
    }

async def safety_monitoring_task(client_id: str, websocket: WebSocket):
    """Task giám sát an toàn và gửi cảnh báo."""
    while client_id in connection_manager.active_connections:
        try:
            route = connection_manager.get_route(client_id)
            if route and route.current_step_index < len(route.steps):
                current_step = route.steps[route.current_step_index]
                
                # Kiểm tra thay đổi hướng đột ngột
                if route.current_step_index > 0:
                    prev_step = route.steps[route.current_step_index - 1]
                    if await safety_monitor.check_sudden_direction_change(
                        prev_step.bearing,
                        current_step.bearing
                    ):
                        await connection_manager.send_navigation_update(client_id, {
                            "alert": "Cẩn thận: Thay đổi hướng đột ngột phía trước",
                            "type": "safety_warning"
                        })
            
            await asyncio.sleep(1)  # Kiểm tra mỗi giây
        except Exception as e:
            print(f"Safety monitoring error for client {client_id}: {str(e)}")
            break
