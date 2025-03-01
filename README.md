# Smart Glasses Server

FastAPI backend server for the Smart Glasses project.

Backend server FastAPI cho dự án Smart Glasses.

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

## Prerequisites | Yêu cầu

-   Python 3.10+
-   Docker and Docker Compose | Docker và Docker Compose
-   Git

## Local Development Setup | Cài đặt môi trường phát triển

1. Clone the repository | Clone repository

```bash
git clone <repository-url>
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

## CI/CD Pipeline | Pipeline CI/CD

The project uses GitHub Actions for continuous integration and deployment.
Dự án sử dụng GitHub Actions cho tích hợp và triển khai liên tục.

### Pipeline Stages | Các giai đoạn Pipeline

1. **Test Stage | Giai đoạn Test**

    - Runs pytest test suite | Chạy bộ test pytest
    - Performs code quality checks with flake8 | Kiểm tra chất lượng code với flake8
    - Uses caching to speed up builds | Sử dụng cache để tăng tốc build

2. **Build & Deploy Stage | Giai đoạn Build & Deploy**
    - Builds Docker image | Build Docker image
    - Pushes to Docker Hub (on main branch) | Đẩy lên Docker Hub (trên nhánh main)
    - Uses layer caching for faster builds | Sử dụng layer caching để build nhanh hơn

### Setting up CI/CD | Cài đặt CI/CD

1. Add required GitHub secrets | Thêm GitHub secrets cần thiết:

    - `DOCKER_USERNAME`: Your Docker Hub username | Tên người dùng Docker Hub của bạn
    - `DOCKER_PASSWORD`: Your Docker Hub access token | Token truy cập Docker Hub của bạn

2. The pipeline automatically runs on | Pipeline tự động chạy khi:

    - Push to main branch | Push lên nhánh main
    - Pull requests to main branch | Tạo pull request vào nhánh main

3. Monitor deployments in | Theo dõi triển khai tại:
    - GitHub Actions tab | Tab GitHub Actions
    - Docker Hub repository | Repository Docker Hub

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

## License | Giấy phép

[Add your license information here | Thêm thông tin giấy phép của bạn vào đây]
