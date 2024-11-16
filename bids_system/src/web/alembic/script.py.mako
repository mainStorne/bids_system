"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

class Factory(SQLAlchemyFactory):
    __is_base_factory__ = True
    __set_relationships__ = False


# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}
    async def seed_db(connection: AsyncConnection):
        session = AsyncSession(bind=connection)
        Factory.__async_session__ = session
        factory = Factory.create_factory(User)
        await factory.create_batch_async(10)


    op.run_async(seed_db)


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
