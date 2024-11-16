from sqlalchemy import SmallInteger, ForeignKey, String, Boolean, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, IDMixin


class User(IDMixin, Base):
    __tablename__ = 'users'

    phone: Mapped[int] = mapped_column(String(length=20), unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(length=200), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    first_name: Mapped[str] = mapped_column(
        String(length=320)
    )
    middle_name: Mapped[str] = mapped_column(
        String(length=320)
    )
    last_name: Mapped[str] = mapped_column(
        String(length=320))

    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    type_id: Mapped[int] = mapped_column(ForeignKey('user_types.id'))
    type: Mapped['UserType'] = relationship(back_populates='user')


class UserType(IDMixin, Base):
    __tablename__ = 'user_types'
    name: Mapped[str] = mapped_column(String(length=90), unique=True)
    user: Mapped['User'] = relationship(back_populates='type')
