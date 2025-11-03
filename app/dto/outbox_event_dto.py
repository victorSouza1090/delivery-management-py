from typing import Any, Dict

class OutboxEventDTO:
    def __init__(self, id: str, order_id: str, event_type: str, payload: Dict[str, Any], sent: bool, created_at):
        self.id = id
        self.order_id = order_id
        self.event_type = event_type
        self.payload = payload
        self.sent = sent
        self.created_at = created_at

    @classmethod
    def from_model(cls, model):
        import json
        payload = model.payload
        if isinstance(payload, str):
            payload = json.loads(payload)
        return cls(
            id=model.id,
            order_id=model.order_id,
            event_type=model.event_type,
            payload=payload,
            sent=model.sent,
            created_at=model.created_at
        )
