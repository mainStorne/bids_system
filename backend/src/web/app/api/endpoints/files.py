from ...managers import FilesManager
from ...storage.db.models import File
from crud import Context
from ...dependencies.session import get_session
from ...schemas.files import FileCreate, FileRead, FileUpdate
from ...utils.crud import CrudAPIRouter

files_manager = FilesManager(File)

r = CrudAPIRouter(Context(schema=FileRead, create_schema=FileCreate, update_schema=FileUpdate,
                      manager=files_manager, get_session=get_session))
