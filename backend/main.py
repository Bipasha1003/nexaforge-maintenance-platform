from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.health import router as health_router
from api.query import router as query_router
from api.admin import router as admin_router
from api.public import router as public_router
from api.worker import router as worker_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(query_router)
app.include_router(admin_router)
app.include_router(public_router)
app.include_router(worker_router)