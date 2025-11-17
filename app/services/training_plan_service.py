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
        plan = TrainingPlanDoc(client_id=payload.client_id, trainer_id=payload.trainer_id, weeks=payload.weeks,
                               notes=payload.notes)
        return await self.repo.create(plan)

    async def update(self, plan_id, updated_doc: TrainingPlanDoc):
        return await self.repo.update(updated_doc)

    async def delete(self, plan_id):
        plan = await self.repo.get_by_id(plan_id)
        if plan:
            await self.repo.delete(plan)
            return True
        return False
