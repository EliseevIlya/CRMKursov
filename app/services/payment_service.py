class PaymentService:
    async def charge(self, client_id:int, amount: float) -> dict:
        # Здесь реальная интеграция с платежным провайдером.
        # Для задания можно симулировать успешный платёж:
        return {"ok": True, "tx_id": f"tx_{client_id}_{int(amount*100)}"}
