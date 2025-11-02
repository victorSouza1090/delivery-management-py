from fastapi import APIRouter, Depends
from uuid import UUID
from app.services.order_service import OrderService
from app.dependencies import get_order_repository
from app.schemas.order_schema import OrderResponse, OrderEventResponse, OrderCreate

router = APIRouter()

# Injeção de Dependencia
async def get_order_service(
    repo = Depends(get_order_repository)
):
    return OrderService(order_repo=repo)

@router.post("/", response_model=OrderResponse)
async def create_order(order_request: OrderCreate, service: OrderService = Depends(get_order_service)):
    order = await service.create_order(order_request)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, service: OrderService = Depends(get_order_service)):
    order = await service.get_order(order_id)
    if not order:
        return {"error": "Pedido não encontrado"}
    return order

@router.get("/{order_id}/events", response_model=list[OrderEventResponse])
async def get_order_events(order_id: UUID, service: OrderService = Depends(get_order_service)):
    events = await service.get_order_events(order_id)
    return events
