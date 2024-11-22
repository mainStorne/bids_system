FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1  # Отключаем создание .pyc файлов
ENV PYTHONUNBUFFERED 1  # Убеждаемся, что вывод логов сразу идет в консоль (без буферизации)

RUN pip install --upgrade pip
COPY worker.requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r worker.requirements.txt

FROM python:3.12-slim
COPY --from=builder /opt/venv /opt/venv
COPY src /src
WORKDIR /src
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH='/src:$PYTHONPATH'
CMD ["saq", "worker.main.settings", "--verbose",  "--web"]