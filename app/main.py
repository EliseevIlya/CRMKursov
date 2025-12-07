from fastapi import FastAPI

from starlette.middleware.sessions import SessionMiddleware
from app.api import auth, oauth
from app.api.graphql import schema
from app.api.graphql_context import get_context
from app.config import settings
from app.container import global_container
from app.mongo import init_mongo

from strawberry.fastapi import GraphQLRouter

app = FastAPI()


@app.on_event("startup")
async def startup():
    await global_container.connect()
    print("startup finished")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,   # ОБЯЗАТЕЛЬНО: длинный secure ключ
    session_cookie="session",         # имя cookie
    max_age=60 * 60 * 24 * 7,         # 7 дней (в секундах)
    same_site="lax",                  # для OAuth редиректов лучше "lax"
    https_only=False,                 # в prod -> True
)


# GraphQLRouter с контекстом
graphql_router = GraphQLRouter(schema, context_getter=get_context,graphiql=True)  # get_context — асинхронная функция
app.include_router(graphql_router, prefix="/graphql")


app.include_router(auth.router)
app.include_router(oauth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
