from fastapi import FastAPI

from app.routes import users, items, characters
from app.database import engine, Base

app = FastAPI()

'''
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
'''

@app.get("/ping")
async def ping():
    return {"status": "ok"}

app.include_router(users.router)
app.include_router(items.router)
app.include_router(characters.router)
