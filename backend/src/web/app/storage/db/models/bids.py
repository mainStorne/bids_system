from .base import Base, IDMixin
from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, String, func, ForeignKey, SmallInteger, Numeric, Date


class Bid(IDMixin, Base):
    __tablename__ = 'bids'
    start_date: Mapped[datetime] = mapped_column(
        Date
    )
    description: Mapped[str] = mapped_column(
        String(), nullable=True
    )
    completion_date: Mapped[datetime] = mapped_column(
        Date, nullable=True
    )

    computer_tech_type: Mapped[str] = mapped_column(
        String(length=80)
    )
    computer_tech_model: Mapped[str] = mapped_column(
        String(length=500)
    )

    issuer_id: Mapped[int] = mapped_column(
        ForeignKey('users.id')
    )


class BidMaster(IDMixin, Base):
    __tablename__ = 'bid_masters'
    bid_id: Mapped[int] = mapped_column(
        ForeignKey('bids.id')
    )
    master_id: Mapped[int] = mapped_column(
        ForeignKey('users.id')
    )


class Spare(IDMixin, Base):
    __tablename__ = 'spares'
    bid_id: Mapped[int] = mapped_column(
        ForeignKey('bids.id')
    )
    name: Mapped[str] = mapped_column(String(length=500), unique=True)
    count: Mapped[int] = mapped_column(SmallInteger)


class BidStatus(IDMixin, Base):
    __tablename__ = 'bid_statuses'
    name: Mapped[str] = mapped_column(String(length=90), unique=True)
