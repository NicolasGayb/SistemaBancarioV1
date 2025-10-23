from fastapi import FastAPI
from app.models.database import Base, engine
from app.views import user_routes, account_routes, routes

app = FastAPI(title="API Bancária Assíncrona", version="1.0")

app.include_router(user_routes.router)
app.include_router(account_routes.router)
app.include_router(routes.router)

@app.on_event("startup")
async def startup():
    """Cria as tabelas no banco de dados ao iniciar o aplicativo."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
