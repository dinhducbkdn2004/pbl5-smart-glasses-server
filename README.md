# Smart Glasses Navigation Server

FastAPI backend server for the Smart Glasses project, providing navigation assistance for visually impaired users.

Backend server FastAPI cho dự án Smart Glasses, hỗ trợ điều hướng cho người khiếm thị.

## Features | Tính năng

-   Voice-guided navigation using GPS coordinates | Điều hướng bằng giọng nói sử dụng tọa độ GPS
-   Text-to-coordinates address lookup | Tìm kiếm địa chỉ từ văn bản sang tọa độ
-   Step-by-step walking directions | Chỉ đẫn đi bộ từng bước
-   Distance and time estimates | Ước tính khoảng cách và thời gian

## Project Structure | Cấu trúc dự án

```
app/
├── api/        # API routes and endpoints | Routes và endpoints của API
├── core/       # Core configurations and utilities | Cấu hình và tiện ích core
├── models/     # Data models and schemas | Models và schemas dữ liệu
├── services/   # Business logic and services | Logic nghiệp vụ và services
├── tests/      # Unit and integration tests | Unit test và integration test
├── main.py     # Application entry point | Điểm khởi đầu của ứng dụng
└── __init__.py # Package initialization | Khởi tạo package
```

## API Endpoints | Các Endpoints API

### Navigation Routes | Routes Điều hướng

#### POST `/api/v1/navigation`

-   Get navigation instructions using GPS coordinates | Lấy hướng dẫn điều hướng bằng tọa độ GPS
-   Request body | Body yêu cầu:

```json
{
    "current_location": {
        "latitude": float,
        "longitude": float
    },
    "destination": {
        "latitude": float,
        "longitude": float
    }
}
```

#### POST `/api/v1/navigation/by-text`

-   Get navigation instructions using text address | Lấy hướng dẫn điều hướng bằng địa chỉ văn bản
-   Request body | Body yêu cầu:

```json
{
    "current_location": {
        "latitude": float,
        "longitude": float
    },
    "destination_text": "string"
}

{
     "current_location": {
         "latitude": 16.061649799999998,
         "longitude": 108.15911509708195
     },
     "destination_text": "Đại học Bách Khoa Đà Nẵng"
 }
```

## Prerequisites | Yêu cầu

-   Python 3.10+
-   Docker and Docker Compose | Docker và Docker Compose
-   Git

## Local Development Setup | Cài đặt môi trường phát triển

1. Clone the repository | Clone repository

```bash
git clone https://github.com/dinhducbkdn2004/pbl5-smart-glasses-server.git
cd pbl5-smart-glasses-server
```

2. Install dependencies | Cài đặt dependencies

```bash
pip install -r requirements.txt
```

3. Run the development server | Chạy server phát triển

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at | API sẽ có sẵn tại: `http://localhost:8000`

## Docker Deployment | Triển khai Docker

1. Build and run using Docker Compose | Build và chạy bằng Docker Compose

```bash
docker-compose up -d
```

2. To stop the services | Để dừng services

```bash
docker-compose down
```

## Testing | Kiểm thử

Run tests using pytest | Chạy test bằng pytest:

```bash
pytest app/tests/
```

The test suite includes | Bộ test bao gồm:

-   Unit tests for navigation services | Unit test cho services điều hướng
-   API endpoint integration tests | Test tích hợp cho endpoints API
-   Mock tests for external services | Test mock cho services bên ngoài

## API Documentation | Tài liệu API

Once the server is running, visit | Khi server đang chạy, truy cập:

-   Swagger UI: `http://localhost:8000/docs`
-   ReDoc: `http://localhost:8000/redoc`

## Contributing | Đóng góp

1. Create a new branch for your feature | Tạo nhánh mới cho tính năng của bạn

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit | Thực hiện thay đổi và commit

```bash
git add .
git commit -m "feat: your feature description"
```

3. Push and create a pull request | Push và tạo pull request

```bash
git push origin feature/your-feature-name
```
