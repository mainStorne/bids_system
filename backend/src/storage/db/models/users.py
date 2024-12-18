from fastapi_permissions import Allow, Deny, All, Authenticated
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
    roles: Mapped[list['Role']] = relationship(back_populates='users', secondary='user_roles', cascade='all, delete')
    files: Mapped[list['File']] = relationship(back_populates='user', secondary='user_files', cascade='all, delete')
    sessions: Mapped[list['Session']] = relationship(back_populates='user', cascade='all, delete')

    def _get_user_roles(self, roles: list['Role']):
        return [role.name for role in roles] + ['role:admin'] if self.is_superuser else []

    async def principals(self):
        roles = await self.awaitable_attrs.roles
        return self._get_user_roles(roles)


    def __acl__(self):
        return [
            (Allow, f'user:{self.login}', 'view'),
            (Allow, 'role:admin', All),
            (Allow, 'role:consumer', 'view'),
            (Allow, Authenticated, 'batch')
        ]


class UserRole(IDMixin, Base):
    __tablename__ = 'user_roles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'))


class Role(IDMixin, Base):
    __tablename__ = 'roles'
    name: Mapped[str] = mapped_column(String(length=90), unique=True)
    users: Mapped[list['User']] = relationship(back_populates='roles', secondary='user_roles')

    def __acl__(self):
        return [
            (Allow, f'{self.name}', 'view'),
            (Allow, 'role:admin', All),
        ]


class File(IDMixin, Base):
    __tablename__ = 'files'
    name: Mapped[str] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped[list['User']] = relationship(back_populates='files', secondary='user_files', cascade='all, delete')

    def __acl__(self):
        return [
            (Allow, f'role:owner', 'view'),
            (Allow, 'role:admin', All),
        ]



class UserFile(IDMixin, Base):
    __tablename__ = 'user_files'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    file_id: Mapped[int] = mapped_column(ForeignKey('files.id', ondelete='CASCADE'))