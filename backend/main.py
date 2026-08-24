from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.health import router as health_router
from api.query import router as query_router
from api.admin import router as admin_router
from api.public import router as public_router
from api.worker import router as worker_router
from api.machines import router as machines_router
from api.documents import router as documents_router
from api.issues import router as issues_router

app = FastAPI()

app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://nexaforge-maintenance.netlify.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

app.include_router(health_router)
app.include_router(query_router)
app.include_router(admin_router)
app.include_router(public_router)
app.include_router(worker_router)
app.include_router(machines_router)
app.include_router(documents_router)
app.include_router(issues_router)