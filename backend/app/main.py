from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db
from .api import auth, grades, attendance, admin, parent, export, reports

app = FastAPI(
    title=settings.APP_NAME,
    description="Электронная система учёта успеваемости студентов",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

app.include_router(auth.router, prefix="/api/auth", tags=["Аутентификация"])
app.include_router(grades.router, prefix="/api/grades", tags=["Оценки"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Посещаемость"])
app.include_router(admin.router, prefix="/api/admin", tags=["Администрирование"])
app.include_router(parent.router, prefix="/api/parent", tags=["Родитель"])
app.include_router(export.router, prefix="/api/export", tags=["Экспорт"])
app.include_router(reports.router, prefix="/api/reports", tags=["Отчёты"])

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
async def root():
    return {
        "message": "API системы учёта успеваемости",
        "docs": "/api/docs"
    }