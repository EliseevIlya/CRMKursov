from typing import List, Optional
from app.db.mongo_models import TrainingPlanDoc
from beanie import PydanticObjectId


class TrainingPlanRepo:
    async def get_by_id(self, plan_id: PydanticObjectId) -> Optional[TrainingPlanDoc]:
        return await TrainingPlanDoc.get(plan_id)

    async def get_by_client(self, client_id: int) -> List[TrainingPlanDoc]:
        return await TrainingPlanDoc.find(TrainingPlanDoc.client_id == client_id).to_list()

    async def create(self, plan: TrainingPlanDoc) -> TrainingPlanDoc:
        await plan.insert()
        return plan

    async def update(self, plan: TrainingPlanDoc) -> TrainingPlanDoc:
        await plan.save()
        return plan

    async def delete(self, plan: TrainingPlanDoc):
        await plan.delete()
