from app.schemas.order_schema import OrderCreate, OrderResponse
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
