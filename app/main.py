from fastapi import FastAPI

from app.routes import users, items

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "ok"}

app.include_router(users.router)
app.include_router(items.router)
