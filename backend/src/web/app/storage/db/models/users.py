from fastapi_permissions import Allow, Deny
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
    roles: Mapped[list['Role']] = relationship(back_populates='users', secondary='user_roles')
    files: Mapped[list['File']] = relationship(back_populates='user', secondary='user_files')

    async def principals(self):
        roles = await self.awaitable_attrs.roles
        return [role.name for role in roles] + ['role:admin'] if self.is_superuser else []


class UserRole(IDMixin, Base):
    __tablename__ = 'user_roles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))


class Role(IDMixin, Base):
    __tablename__ = 'roles'
    name: Mapped[str] = mapped_column(String(length=90), unique=True)
    users: Mapped[list['User']] = relationship(back_populates='roles', secondary='user_roles')

    def __acl__(self):
        return [
            (Allow, f'{self.name}', 'view'),
            (Allow, 'role:admin', 'view'),
        ]


class File(IDMixin, Base):
    __tablename__ = 'files'
    name: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped[list['User']] = relationship(back_populates='files', secondary='user_files')


class UserFile(IDMixin, Base):
    __tablename__ = 'user_files'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    file_id: Mapped[int] = mapped_column(ForeignKey('files.id'))