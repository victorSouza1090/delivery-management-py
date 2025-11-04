from app.models.order import OrderStatus

def test_order_status_next():
    assert OrderStatus.RECEIVED.next() == OrderStatus.IN_TRANSIT
    assert OrderStatus.IN_TRANSIT.next() == OrderStatus.DELIVERED
    assert OrderStatus.DELIVERED.next() is None