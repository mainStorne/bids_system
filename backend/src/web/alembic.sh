#!/bin/bash

echo "Применение миграций"
alembic upgrade head
echo "Миграции успешно применены"
exec "$@"