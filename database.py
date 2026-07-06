from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@dataclass(frozen=True)
class RateRecord:
    currency: str
    rate: float
    created_at: datetime


class CurrencyRate(Base):
    __tablename__ = "currency_rates"
    
    id = Column(Integer, primary_key=True)
    currency = Column(String(10))
    rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Создает таблицы в базе данных"""
    Base.metadata.create_all(engine)


def save_rate(currency: str, rate: float):
    session = SessionLocal()
    try:
        new_rate = CurrencyRate(currency=currency, rate=rate)
        session.add(new_rate)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_rates(rates: dict[str, float]) -> None:
    session = SessionLocal()
    try:
        session.add_all(
            CurrencyRate(currency=currency, rate=rate)
            for currency, rate in rates.items()
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_last_rate(currency: str):
    session = SessionLocal()
    try:
        rate = (
            session.query(CurrencyRate)
            .filter_by(currency=currency)
            .order_by(CurrencyRate.created_at.desc())
            .first()
        )
        return _to_record(rate) if rate else None
    finally:
        session.close()


def get_recent_rates(limit: int = 5) -> list[RateRecord]:
    session = SessionLocal()
    try:
        rates = (
            session.query(CurrencyRate)
            .order_by(CurrencyRate.created_at.desc())
            .limit(limit)
            .all()
        )
        return [_to_record(rate) for rate in rates]
    finally:
        session.close()


def _to_record(rate: CurrencyRate) -> RateRecord:
    return RateRecord(
        currency=rate.currency,
        rate=rate.rate,
        created_at=rate.created_at,
    )
