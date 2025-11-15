from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings, get_mongo_url
from app.db.mongo_models import TrainingPlanDoc

mongo_client: AsyncIOMotorClient | None = None

async def init_mongo():
    global mongo_client
    mongo_client = AsyncIOMotorClient(get_mongo_url())
    await init_beanie(database=mongo_client[settings.MONGO_DB], document_models=[TrainingPlanDoc])

    #test
    db = mongo_client[settings.MONGO_DB]
    await TrainingPlanDoc(client_id=1000, weeks=[]).insert()
    print(await mongo_client.list_database_names())
