FROM python:3.11-slim

RUN  apt-get install python3-dev default-libmysqlclient-dev -y && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime

RUN pip install --upgrade pip && \
    pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry add gunicorn[gevent] && \
    poetry install --no-root --no-dev && \
    poetry cache clear

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# EXPOSE 8000

RUN chmod +x /app/bin/docker_start.sh

ENTRYPOINT [ "/app/bin/docker_start.sh" ]
