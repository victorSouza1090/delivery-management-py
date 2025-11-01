orders_db = {}

class OrderRepository:
    @staticmethod
    def save(order):
        orders_db[order["id"]] = order

    @staticmethod
    def get(order_id):
        return orders_db.get(order_id)
