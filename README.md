# Smart Glasses Navigation Server

Server API cho hệ thống kính thông minh hỗ trợ người khiếm thị với tính năng chỉ đường thời gian thực.

## Yêu cầu hệ thống

-   Python 3.8 hoặc cao hơn
-   pip (Python package manager)

## Cài đặt

1. Clone repository:

```bash
git clone <https://github.com/dinhducbkdn2004/pbl5-smart-glasses-server.git>
cd pbl5-smart-glasses-server
```

2. Tạo môi trường ảo Python:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

3. Cài đặt các dependencies:

```bash
pip install -r requirements.txt
```

4. Cấu hình môi trường:

```bash
# Chỉnh sửa file .env với thông tin cấu hình của bạn
# - Thêm Mapbox Access Token của bạn
```

## Chạy server

1. Kích hoạt môi trường ảo (nếu chưa kích hoạt):

```bash
# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

2. Khởi động server:

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại `http://localhost:8000`

## API Endpoints

### 1. REST API

#### Lấy thông tin chỉ đường

```http
POST /get_route
Content-Type: application/json

{
    "current_location": {
        "latitude": 16.0544,
        "longitude": 108.2022
    },
    "destination_name": "Đại học Bách Khoa Đà Nẵng"
}
```

### 2. WebSocket API

#### Kết nối WebSocket để nhận hướng dẫn thời gian thực

```javascript
// Kết nối
const ws = new WebSocket('ws://localhost:8000/ws/navigation/client-123');

// Gửi vị trí và điểm đến
ws.send(
    JSON.stringify({
        latitude: 16.0544,
        longitude: 108.2022,
        destination_name: 'Đại học Bách Khoa Đà Nẵng',
    })
);

// Lắng nghe hướng dẫn
ws.onmessage = (event) => {
    const guidance = JSON.parse(event.data);
    console.log(guidance);
};
```

## Tính năng

1. **Hướng dẫn chi tiết bằng tiếng Việt**

    - Chỉ dẫn theo số bước đi
    - Khoảng cách theo mét
    - Hướng rẽ chi tiết

2. **Cập nhật thời gian thực**

    - Theo dõi vị trí GPS
    - Tự động cập nhật hướng dẫn
    - Thông báo trước khi đến điểm rẽ

3. **Tính năng an toàn**
    - Cảnh báo chướng ngại vật
    - Thông báo thay đổi hướng đột ngột
    - Giám sát liên tục

## Kiểm tra API

Sau khi khởi động server, bạn có thể:

1. Truy cập documentation tại:

    - Swagger UI: `http://localhost:8000/docs`
    - ReDoc: `http://localhost:8000/redoc`

2. Test WebSocket bằng công cụ như [WebSocket King](https://websocketking.com)

## Lưu ý

-   Đảm bảo Mapbox Access Token hợp lệ trong file `.env`
-   Server cần duy trì kết nối ổn định để cập nhật theo thời gian thực
-   Khuyến nghị sử dụng SSL/TLS trong môi trường production
