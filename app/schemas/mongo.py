from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ExerciseSchema(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    notes: Optional[str] = None


class DayPlanSchema(BaseModel):
    day: str
    exercises: List[ExerciseSchema]


class WeekPlanSchema(BaseModel):
    week: int
    days: List[DayPlanSchema]


class TrainingPlanCreate(BaseModel):
    client_id: int
    trainer_id: Optional[int] = None
    weeks: List[WeekPlanSchema]
    notes: Optional[str] = None


class TrainingPlanRead(TrainingPlanCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
