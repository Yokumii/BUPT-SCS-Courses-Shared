"""BUPT Intelligent Charging Station Scheduling & Billing System — FastAPI Entry Point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.models import *  # noqa: ensure all models are registered
from app.routers import auth, charging, pile, billing
from app.services.scheduler import scheduler
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _init_default_data(db)
        scheduler.initialize(db)
    finally:
        db.close()
    yield


def _init_default_data(db):
    """Initialize default piles and admin on first startup."""
    from sqlalchemy import text
    from app.models.pile import ChargingPile, PileType, PileStatus
    from app.models.user import User, UserRole
    from app.models.billing import SchedulingPolicy, SchedulingMode

    try:
        columns = [row[1] for row in db.execute(text("PRAGMA table_info(users)")).fetchall()]
        if columns and "balance" not in columns:
            db.execute(text("ALTER TABLE users ADD COLUMN balance FLOAT DEFAULT 0.0 NOT NULL"))
            db.commit()
    except Exception:
        db.rollback()

    # Create piles if not exist
    existing = db.query(ChargingPile).count()
    if existing == 0:
        for i in range(1, settings.FAST_CHARGING_PILE_NUM + 1):
            pile = ChargingPile(
                name=f"F{i}", pile_type=PileType.FAST,
                power=30.0, status=PileStatus.ONLINE
            )
            db.add(pile)
        for i in range(1, settings.TRICKLE_CHARGING_PILE_NUM + 1):
            pile = ChargingPile(
                name=f"T{i}", pile_type=PileType.TRICKLE,
                power=10.0, status=PileStatus.ONLINE
            )
            db.add(pile)
        db.commit()

    # Create default admin
    admin = db.query(User).filter(User.role == UserRole.ADMINISTRATOR).first()
    if not admin:
        import hashlib
        admin = User(
            username="admin",
            password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
            role=UserRole.ADMINISTRATOR,
            department="充电站管理部",
        )
        db.add(admin)
        db.commit()

    # Create default scheduling policy
    policy = db.query(SchedulingPolicy).first()
    if not policy:
        policy = SchedulingPolicy(mode=SchedulingMode.BASELINE)
        db.add(policy)
        db.commit()


app = FastAPI(
    title="BUPT 智能充电桩调度计费系统",
    description="北京邮电大学软件工程课程项目 — 充电桩调度与计费后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(charging.router)
app.include_router(pile.router)
app.include_router(billing.router)


@app.get("/")
def root():
    return {"message": "BUPT 智能充电桩调度计费系统 API", "docs": "/docs"}
