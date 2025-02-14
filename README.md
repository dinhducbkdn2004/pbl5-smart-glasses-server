# Smart Glasses Navigation Server

A real-time navigation server API for smart glasses system supporting visually impaired people.

Server API cho hệ thống kính thông minh hỗ trợ người khiếm thị với tính năng chỉ đường thời gian thực.

## System Requirements | Yêu cầu hệ thống

- Python 3.8 or higher | Python 3.8 hoặc cao hơn
- pip (Python package manager)

## Installation | Cài đặt

1. Clone repository:

```bash
git clone https://github.com/dinhducbkdn2004/pbl5-smart-glasses-server.git
cd pbl5-smart-glasses-server
```

2. Create Python virtual environment | Tạo môi trường ảo Python:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

3. Install dependencies | Cài đặt các dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment | Cấu hình môi trường:

```bash
# Edit .env file with your configuration
# No API key required as we use OpenStreetMap

# Chỉnh sửa file .env với thông tin cấu hình của bạn
# Không cần API key vì chúng ta sử dụng OpenStreetMap
```

## Running the Server | Chạy server

1. Activate virtual environment (if not already activated) | Kích hoạt môi trường ảo (nếu chưa kích hoạt):

```bash
# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

2. Start the server | Khởi động server:

```bash
uvicorn app.main:app --reload
```

Server will run at | Server sẽ chạy tại `http://localhost:8000`

## API Endpoints

### 1. REST API

#### Get Route Information | Lấy thông tin chỉ đường

```http
POST /get_route
Content-Type: application/json

{
    "current_location": {
        "latitude": 16.061649799999998,
        "longitude": 108.15911509708195
    },
    "destination_text": "Đại học Bách Khoa Đà Nẵng"
}
```

## Features | Tính năng

1. **Detailed Vietnamese Voice Guidance | Hướng dẫn chi tiết bằng tiếng Việt**
    - Step-by-step instructions | Chỉ dẫn theo số bước đi
    - Distance in meters | Khoảng cách theo mét
    - Detailed turn directions | Hướng rẽ chi tiết

2. **Real-time Updates | Cập nhật thời gian thực**
    - GPS location tracking | Theo dõi vị trí GPS
    - Automatic guidance updates | Tự động cập nhật hướng dẫn
    - Turn notifications | Thông báo trước khi đến điểm rẽ

3. **Safety Features | Tính năng an toàn**
    - Obstacle warnings | Cảnh báo chướng ngại vật
    - Sudden direction change alerts | Thông báo thay đổi hướng đột ngột
    - Continuous monitoring | Giám sát liên tục

## Testing the API | Kiểm tra API

After starting the server, you can access | Sau khi khởi động server, bạn có thể truy cập:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes | Lưu ý

- Using OpenStreetMap for navigation services | Sử dụng OpenStreetMap cho dịch vụ chỉ đường
- Server requires stable connection for real-time updates | Server cần duy trì kết nối ổn định để cập nhật theo thời gian thực
- SSL/TLS recommended for production environment | Khuyến nghị sử dụng SSL/TLS trong môi trường production
