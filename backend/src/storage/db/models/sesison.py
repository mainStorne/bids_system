from sqlalchemy import ForeignKey

from .base import Base, IDMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Session(IDMixin, Base):
    __tablename__ = 'sessions'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='sessions')