from beanie import Document, init_beanie
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Exercise(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    notes: Optional[str] = None


class DayPlan(BaseModel):
    day: str
    exercises: List[Exercise]


class WeekPlan(BaseModel):
    week: int
    days: List[DayPlan]


class TrainingPlanDoc(Document):
    client_id: int
    trainer_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    weeks: List[WeekPlan]
    notes: Optional[str] = None

    class Settings:
        name = "training_plans"
