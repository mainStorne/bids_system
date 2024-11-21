from typing import Iterable, Any

from fastapi_sqlalchemy_toolkit.model_manager import CreateSchemaT, ModelT
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseManager, logger
from ..conf import BASE_PATH
import aiofiles
from uuid import uuid4

from ..exceptions import FileDoesntSave
from fastapi import UploadFile


class FilesManager(BaseManager):
    async def _save_file_to_static(self, file: UploadFile):
        url = f'{uuid4()}{file.filename}'
        filename = BASE_PATH / 'static' / url
        try:
            async with aiofiles.open(filename, 'wb') as f:
                while data := await file.read(1024 * 1024):
                    await f.write(data)
        except Exception as e:
            logger.exception('Downloaded file with size %d', file.size, exc_info=e)
            raise FileDoesntSave from e
        finally:
            await file.close()

        return f'/staticfiles/{url}'

    async def create_user_file(self, session: AsyncSession, upload_file: UploadFile, **attrs) -> ModelT:
        async with session.begin_nested():
            url = await self._save_file_to_static(upload_file)
            create_data = {'file_path': url, 'name': upload_file.filename, **attrs}

            for field, default in self.defaults.items():
                if field not in create_data:
                    create_data[field] = default

            await self.run_db_validation(session, create_data)
            logger.info('data %s', create_data)
            db_obj = self.model(**create_data)
            session.add(db_obj)
            # await self.save(session)
            await session.commit()


        return db_obj
