from fastapi import FastAPI

from app.api import auth, oauth
from app.container import global_container
from app.mongo import init_mongo

app = FastAPI()


@app.on_event("startup")
async def startup():
    # init Mongo (Beanie)
    #await init_mongo()
    # init Redis
    #await init_redis()
    # Optionally ensure DB metadata (only for dev) - don't use in prod with Alembic
    # async with engine.begin() as conn:
    #     await conn.run_sync(models.Base.metadata.create_all)
    await global_container.connect()
    print("startup finished")

app.include_router(auth.router)
app.include_router(oauth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
