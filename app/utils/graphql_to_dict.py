from strawberry import UNSET

from app.schemas.mongo import ExerciseSchema, DayPlanSchema, WeekPlanSchema


def graphql_to_dict(data):
    return {k: v for k, v in data.__dict__.items() if v is not UNSET}


""""
def graphql_to_dict_for_training_plan(data):
    ""
    Превращает Strawberry input в словарь для TrainingPlanDoc (Beanie Document).
    Вложенные weeks/days/exercises конвертируются в обычные dict.
    ""
    result = {k: v for k, v in data.__dict__.items() if v is not UNSET}

    if "weeks" in result and result["weeks"] is not None:
        weeks_converted = []
        for w in result["weeks"]:
            days_converted = []
            for d in w.days:
                exercises_converted = [e.__dict__ for e in d.exercises]
                days_converted.append({"day": d.day, "exercises": exercises_converted})
            weeks_converted.append({"week": w.week, "days": days_converted})
        result["weeks"] = weeks_converted

    return result


def graphql_to_dict_for_training_plan_t(data):
    ""
    Превращает Strawberry input в словарь для TrainingPlanDoc (Beanie Document).
    Вложенные weeks/days/exercises конвертируются в обычные dict.
    ""
    result = {k: v for k, v in data.__dict__.items() if v is not UNSET}

    if "weeks" in result and result["weeks"] is not None:
        weeks_converted = []
        for w in result["weeks"]:
            days_converted = []
            for d in w.days:
                exercises_converted = [ExerciseSchema(**e) for e in d.exercises]
                days_converted.append(DayPlanSchema(day=d.day, exercises=exercises_converted))
            weeks_converted.append(WeekPlanSchema(week=w.week, days=days_converted))
        result["weeks"] = weeks_converted

    return result
    
    def strawberry_input_to_dict(obj):
    ""Recursively convert Strawberry input objects to dictionaries.""
    if hasattr(obj, "__dict__"):
        result = {}
        for k, v in obj.__dict__.items():
            if v is None:
                result[k] = v
            elif isinstance(v, list):
                result[k] = [strawberry_input_to_dict(item) for item in v]
            else:
                result[k] = strawberry_input_to_dict(v)
        return result
    return obj


"""


def graphql_to_dict_for_training_plan(data):
    """
    Converts Strawberry input types into a plain dictionary compatible with Beanie (Pydantic).
    Handles nested weeks → days → exercises.
    Recursive
    """

    def to_dict(obj):
        if hasattr(obj, "__dict__"):
            return {
                k: to_dict(v) for k, v in obj.__dict__.items()
                if v is not None and v != UNSET
            }
        elif isinstance(obj, list):
            return [to_dict(item) for item in obj]
        else:
            return obj

    return to_dict(data)
