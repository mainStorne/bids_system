# App

## Конфигурация приложения
    вся конфигурация находится в .env файле
### Создать контейнер: 
    docker compose build
### Запустить контейнер:
    docker compose up
### Зайти в запущенный контейнер
    docker exec -it backend bash
### Применение миграции
    alembic upgrade head

### Документация
    http://localhost/api/docs