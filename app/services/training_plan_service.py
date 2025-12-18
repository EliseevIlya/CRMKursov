from app.repositories.mongo.training_plan_repo import TrainingPlanRepo
from app.db.mongo_models import TrainingPlanDoc
from app.schemas.mongo import TrainingPlanCreate
from typing import List


class TrainingPlanService:
    def __init__(self):
        self.repo = TrainingPlanRepo()

    async def list_for_client(self, client_id: int):
        return await self.repo.get_by_client(client_id)

    async def create(self, payload: TrainingPlanCreate):
        #plan = TrainingPlanDoc(client_id=payload.client_id, trainer_id=payload.trainer_id, weeks=payload.weeks,notes=payload.notes)
        plan = TrainingPlanDoc(**payload.dict())
        return await self.repo.create(plan)

    """"
        async def update(self, plan_id, updated_doc: TrainingPlanDoc):
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        plan.weeks = updated_doc.weeks
        plan.notes = updated_doc.notes
        return await self.repo.update(updated_doc)
    """

    async def update(self, plan_id: str, updated_doc: TrainingPlanCreate):
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        update_data = updated_doc.dict(exclude_unset=True)  # только переданные поля

        for k, v in update_data.items():
            setattr(plan, k, v)  # обновляем только переданные поля

        return await self.repo.update(plan)

    async def delete(self, plan_id):
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
            return False
        await self.repo.delete(plan)
        return True
