import os

folders = [
    "app",
    "app/core",
    "app/api/routes",
    "app/models",
    "app/schemas",
    "app/services",
    "app/repositories",
    "app/events",
    "app/db",
    "tests"
]

files = {
    "app/main.py": """from fastapi import FastAPI
from app.api.routes import orders

app = FastAPI(title="Delivery Service API")

app.include_router(orders.router, prefix="/orders", tags=["Orders"])
""",

    "app/api/routes/orders.py": """from fastapi import APIRouter, HTTPException
from app.schemas.order_schema import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate):
    return OrderService.create_order(order)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    return OrderService.get_order(order_id)
""",

    "app/schemas/order_schema.py": """from pydantic import BaseModel
from datetime import datetime

class OrderCreate(BaseModel):
    customer_name: str
    address: str

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    address: str
    status: str
    created_at: datetime
""",

    "app/services/order_service.py": """from app.schemas.order_schema import OrderCreate, OrderResponse
from app.repositories.order_repository import OrderRepository
from datetime import datetime
import uuid

class OrderService:
    @staticmethod
    def create_order(order: OrderCreate) -> OrderResponse:
        new_order = {
            "id": str(uuid.uuid4()),
            "customer_name": order.customer_name,
            "address": order.address,
            "status": "RECEIVED",
            "created_at": datetime.utcnow(),
        }
        OrderRepository.save(new_order)
        return OrderResponse(**new_order)

    @staticmethod
    def get_order(order_id: str):
        order = OrderRepository.get(order_id)
        if not order:
            raise Exception("Order not found")
        return OrderResponse(**order)
""",

    "app/repositories/order_repository.py": """orders_db = {}

class OrderRepository:
    @staticmethod
    def save(order):
        orders_db[order["id"]] = order

    @staticmethod
    def get(order_id):
        return orders_db.get(order_id)
""",

    "app/core/config.py": """import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Delivery Service"
    ENV: str = os.getenv("ENV", "development")

settings = Settings()
""",

    "app/db/database.py": """# Aqui futuramente entra a conexão com PostgreSQL ou Redis
""",

    ".env.example": """ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/delivery_service
""",

    "requirements.txt": """fastapi
uvicorn
pydantic
python-dotenv
""",

    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

    "docker-compose.yml": """version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
    restart: always
""",

    "README.md": """# Delivery Service API

Sistema de gerenciamento de entregas orientado a eventos, desenvolvido com FastAPI.
"""
}

# Cria diretórios
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Cria arquivos
for path, content in files.items():
    with open(path, "w") as f:
        f.write(content)

print("✅ Estrutura do projeto criada com sucesso!")
