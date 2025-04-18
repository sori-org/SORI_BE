from fastapi import FastAPI
from src.api import store, search

app = FastAPI()

app.include_router(store.router, prefix="/stores")
app.include_router(search.router, prefix="/search")
