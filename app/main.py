from fastapi import FastAPI

from app.api.v1 import users, items, characters, monsters

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
app.include_router(monsters.router)
